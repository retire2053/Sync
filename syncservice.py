import shutil
from clock import *
from plibraryservice import PLibraryService
import os

class SyncService(PLibraryService):

    def __init__(self, context): 
        super().__init__(context)

    def __get_directory_info_dict(self, directory):
        if directory is None: return None
        file_info_dict = dict()
        file_path_list = []
        for (root, dirs, files) in os.walk(directory):
            filenames = [w for w in files if not w.startswith(".") and not root.split("/")[-1].startswith(".")]
            for file_name in filenames:
                full_path = root+"/"+file_name
                related_path = full_path[len(directory):]
                file_path_list.append(related_path)
                file_info_dict[related_path] = os.stat(full_path).st_size
        return file_info_dict

    def __compare(self):
        if self.get_param('source_file_info_dict') is None or self.get_param('output_file_info_dict') is None: return None
        difference = []
        difference2 = []
        for item in list(self.get_param('source_file_info_dict').keys()):
            if item not in list(self.get_param('output_file_info_dict').keys()):
                difference.append(item)
            elif self.get_param('source_file_info_dict')[item]!=self.get_param('output_file_info_dict')[item]:
                difference.append(item)
        for item in list(self.get_param('output_file_info_dict').keys()):
            if item not in list(self.get_param('source_file_info_dict').keys()):
                difference2.append(item)
        return difference,difference2

    def __prepare_analyze_action(self):
        if self.get_var('source') is None or not os.path.exists(self.get_var('source')) :
            print("请先使用setsource来设置[source]")
            return False
        elif self.get_var('output') is None or not os.path.exists(self.get_var('output')):
            print("请先使用setoutput来设置[output]")
            return False
        else:
            self.set_param('source_file_info_dict', self.__get_directory_info_dict(self.get_var('source')))
            self.set_param('output_file_info_dict', self.__get_directory_info_dict(self.get_var('output')))
            ret = self.__compare()
            self.set_param('difference', ret[0])
            self.set_param('difference2', ret[1])
            return True

    def service_analyze(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__prepare_analyze_action():
            print("[source] %s下包含%d个文件" % (self.get_var('source'), len(list(self.get_param('source_file_info_dict').keys()))))
            print("[output] %s下包含%d个文件" % (self.get_var('output'), len(list(self.get_param('output_file_info_dict').keys()))))
            print()
            print("其中有%d个文件在[source]中，但并不在[output]中" % len(self.get_param('difference')))
            print("同时，有%d个文件在[output], 但并不在[source]中" % len(self.get_param('difference2')))
            print()
            self.__detect_a_directory()

    def __detect_a_directory(self):
        total_bytes = 0
        first_level_dirs = [w for w in os.listdir(self.get_var('source')) if os.path.isdir(self.get_var('source') + "/" + w) and not w.startswith(".")]
        first_level_file_dict = dict.fromkeys(first_level_dirs)
        for item in first_level_file_dict: first_level_file_dict[item] = [0, 0]

        file_type_count_dict = dict()
        for x in self.get_param('source_file_info_dict'):
            total_bytes += self.get_param('source_file_info_dict')[x]
            first_level_dir = x.split("/")[1]
            if first_level_dir in first_level_file_dict:
                values = first_level_file_dict[first_level_dir]
                first_level_file_dict[first_level_dir][0] = values[0] + 1
                first_level_file_dict[first_level_dir][1] = values[1] + self.get_param('source_file_info_dict')[x]
            file_type = x.split("/")[-1].split(".")[-1].lower()
            if file_type in file_type_count_dict:
                file_type_count_dict[file_type] += 1
            else:
                file_type_count_dict[file_type] = 1

        print("[source] %s下包含总共占用磁盘%s字节" %(self.get_var('source'),format(total_bytes, ",")))
        print()
        print("[子目录]")
        inspect_results = []

        for i in range(len(first_level_dirs)):
            item = first_level_dirs[i]
            average = int(first_level_file_dict[item][1] / (1024 * 1024 * first_level_file_dict[item][0]))
            inspect_results.append([str(i+1), item, "contains %d files" % first_level_file_dict[item][0],
                                 "with %s Bytes" % format(first_level_file_dict[item][1], ","),
                                 "average %s MB" % format(average, ",")])
        self.__format_display(inspect_results)
        print()
        print("[文件类型分布 (top 10)")
        sorted_list = sorted(file_type_count_dict.items(), key=lambda item: item[1], reverse=True)[0:10]
        display_list = []
        for item in sorted_list:
            display_list.append([item[0], "contains %d files" % item[1]])
        self.__format_display(display_list)
        print()

    def service_sync(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            c = Clock()
            c.start(len(self.get_param('difference')), "同步%d个文件"%len(self.get_param('difference')))
            total_size = 0
            for x in self.get_param('difference'): total_size+=self.get_param('source_file_info_dict')[x]
            finish_size = 0
            for i in range(len(self.get_param('difference'))):
                item = self.get_param('difference')[i]
                source_file_path = self.get_var('source')+item
                output_file_path = self.get_var('output')+item
                output_path = "/".join(output_file_path.split("/")[0:-1])
                if not os.path.exists(output_path): os.makedirs(output_path)
                shutil.copy(source_file_path, output_file_path)
                finish_size+=self.get_param('source_file_info_dict')[item]
                c.count(int(finish_size*100/total_size))
            c.finish()
            self.__prepare_analyze_action()

    def service_clean(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            c = Clock()
            c.start(len(self.get_param('difference2')), "删除%d个文件"%len(self.get_param('difference2')))
            for i in range(len(self.get_param('difference2'))):
                item = self.get_param('difference2')[i]
                output_file_path = self.get_var('output')+item
                os.remove(output_file_path)
                c.count_by_number()
            c.finish()
            self.__prepare_analyze_action()

    def service_showsync(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            temp_dict = dict()
            for item in self.get_param('difference'): temp_dict[item] = self.get_param('source_file_info_dict')[item]
            sorted_list = sorted(temp_dict.items(), key=lambda item: item[1], reverse = True)
            if len(sorted_list)>30: sorted_list = sorted_list[0:30]
            display_list = []
            for item in sorted_list:
                display_list.append(["占用磁盘%s"%(format(item[1]/1024*1024, ",")), self.get_var('source')+item[0]])
            self.__format_display(display_list)


    def service_showclean(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            temp_dict = dict()
            for item in self.get_param('difference2'): temp_dict[item] = self.get_param('output_file_info_dict')[item]
            sorted_list = sorted(temp_dict.items(), key=lambda item: item[1], reverse = True)
            if len(sorted_list)>30: sorted_list = sorted_list[0:30]
            display_list = []
            for item in sorted_list:
                display_list.append(["占用磁盘%s"%(format(item[1]/1024*1024, ",")), self.get_var('output')+item[0]])
            self.__format_display((display_list))

    def service_search(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            text = input("请输入你想要检索的字符串:").strip().lower()
            count = 1
            search_results = []
            for x in self.get_param('source_file_info_dict'):
                lower_case = x.lower()
                if text in lower_case:
                    lower_case_parts = lower_case.split("/")
                    parts = x.split("/")
                    for i in range(len(lower_case_parts)-1, -1, -1):
                        if text in lower_case_parts[i]: break
                    sub_path = "/".join(parts[0:i+1])
                    if sub_path not in search_results: search_results.append(sub_path)
            for x in search_results:
                print("\t", count, x)
                count+=1
            if len(search_results)==1:
                os.system("open \"%s%s\"" % (self.get_var('source'), search_results[0]))
                print("\t只检索到一个文件，已经为您打开")
            elif len(search_results)==0:
                print("\t没有找到结果，请重新检索")
            else:
                print("\t请使用open命令来打开某个文件")
            self.set_param('search_results', search_results)

    def service_duplicate(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            dup_dict = dict()
            for x in self.get_param('source_file_info_dict'):
                key = (x.split("/")[-1], self.get_param('source_file_info_dict')[x])
                if key not in dup_dict: dup_dict[key] = [x]
                else: dup_dict[key].append(x)
            count = 0
            to_delete = []
            for x in dup_dict:
                if len(dup_dict[x])>1:
                    count += 1
                    for item in dup_dict[x]:print("\t[group%d]"%count, item)
                    to_delete.extend(dup_dict[x][1:])
                    print()
            if count == 0 : print("没有找到任何重复的文件")
            else:
                text = input("你想删除这些%d个重复项吗？输入yes进行删除:"%len(to_delete)).strip()
                if text == 'yes':
                    for i in range(len(to_delete)):
                        print("delete no.%d"%(i+1), self.get_var('source') + "/" + to_delete[i])
                        os.remove(self.get_var('source')+"/"+ to_delete[i])

    def service_open(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            if self.get_param("search_results") is None or len(self.get_param("search_results"))==0:
                print("请先运行'analyze'和'search'命令")
                return
            text = input("请输入文件的编号:").strip()
            if text.isdigit() :
                id = int(text)-1
                if len(self.get_param("search_results"))>=id>=0:
                    os.system("open \"%s%s\""%(self.get_var('source'), self.get_param("search_results")[id]))

    def service_big(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            lst = sorted(self.get_param('source_file_info_dict').items(),key=lambda s:s[1], reverse = True)[0:100]
            display_list = []
            for i in range(len(lst)):
                display_list.append(["[%d]"%(i+1),  "\t占用磁盘%sMB"%format(int(lst[i][1]/(1024*1024)), ',') , "[%s]"%lst[i][0]])
            self.__format_display(display_list)

    def __is_analyzed(self):
        if self.get_param('source_file_info_dict') is None:
            return self.__prepare_analyze_action()
        else: return True

    def __format_display(self, lst):
        if len(lst)>0:
            maxlen = [0]*len(lst[0])
            for item in lst:
                for i in range(len(item)):
                    if len(item[i])>maxlen[i]:maxlen[i] = len(item[i])
            for item in lst:
                for i in range(len(item)):
                    how_many_space = maxlen[i]-len(item[i])
                    print(item[i]+''.join([" "]*how_many_space)+"  ", end='')
                print("", end='\n')
        else: print("没有可显示的内容")