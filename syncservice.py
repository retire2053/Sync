import shutil
from clock import *
from baseservice import *
import os
from util import Util

class SyncService(BaseService):

    def __init__(self, context): 
        super().__init__(context)

    def __get_directory_info_dict(self, directory):
        if directory is None: return None
        file_info_set = set()
        for (root, dirs, files) in os.walk(directory):
            print("\t分析%s"%root)
            filenames = [w for w in files if not w.startswith(".") and not root.split("/")[-1].startswith(".")]
            for i in range(len(filenames)):
                file_name = filenames[i]
                print("\t\t", i+1, file_name)
                full_path = root+"/"+file_name
                related_path = full_path[len(directory):]
                file_info_set.add(related_path)
        return file_info_set

    def __compare(self):
        if self.get_param('source_file_info_dict') is None or self.get_param('output_file_info_dict') is None: return None
        difference = []
        difference2 = []

        difference_dict = dict()
        for item in self.get_param('source_file_info_dict'):
            difference_dict[item] = {'source':True, 'output':False}
        for item in self.get_param('output_file_info_dict'):
            if item in difference_dict:
                difference_dict[item]['output'] = True
            else:
                difference_dict[item] = {'output':True, 'source':False}
        for item in difference_dict:
            if difference_dict[item]['source'] and not difference_dict[item]['output']: difference.append(item)
            elif not difference_dict[item]['source'] and difference_dict[item]['output']:difference2.append(item)
        return difference,difference2

    def __prepare_analyze_action(self):
        if self.get_var('source') is None or not os.path.exists(self.get_var('source')) :
            print("请先使用setsource来设置[source]")
            return False
        elif self.get_var('output') is None or not os.path.exists(self.get_var('output')):
            print("请先使用setoutput来设置[output]")
            return False
        else:
            print("开始分析%s"%self.get_var('source'))
            self.set_param('source_file_info_dict', self.__get_directory_info_dict(self.get_var('source')))
            print("开始分析%s"%self.get_var('output'))
            self.set_param('output_file_info_dict', self.__get_directory_info_dict(self.get_var('output')))
            print('开始对比source和output目录')
            ret = self.__compare()
            self.set_param('difference', ret[0])
            self.set_param('difference2', ret[1])
            print("完成分析")
            return True

    def service_analyze(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__prepare_analyze_action():
            print("[source] %s下包含%d个文件" % (self.get_var('source'), len(self.get_param('source_file_info_dict'))))
            print("[output] %s下包含%d个文件" % (self.get_var('output'), len(self.get_param('output_file_info_dict'))))
            print()
            print("其中有%d个文件在[source]中，但并不在[output]中" % len(self.get_param('difference')))
            print("同时，有%d个文件在[output], 但并不在[source]中" % len(self.get_param('difference2')))
            print()
            self.__detect_a_directory()

    def __detect_a_directory(self):
        first_level_dirs = [w for w in os.listdir(self.get_var('source')) if os.path.isdir(self.get_var('source') + "/" + w) and not w.startswith(".")]
        first_level_file_dict = dict.fromkeys(first_level_dirs)
        for item in first_level_file_dict: first_level_file_dict[item] = [0, 0]

        file_type_count_dict = dict()
        for x in self.get_param('source_file_info_dict'):
            first_level_dir = x.split("/")[1]
            if first_level_dir in first_level_file_dict:
                values = first_level_file_dict[first_level_dir]
                first_level_file_dict[first_level_dir][0] = values[0] + 1
            file_type = x.split("/")[-1].split(".")[-1].lower()
            if file_type in file_type_count_dict:
                file_type_count_dict[file_type] += 1
            else:
                file_type_count_dict[file_type] = 1

        print()
        print("[子目录]")
        inspect_results = []

        for i in range(len(first_level_dirs)):
            item = first_level_dirs[i]
            if first_level_file_dict[item][0]==0: 
                inspect_results.append([str(i+1), item, "contains 0 files", "with 0 Bytes", "average 0 MB"])
            else:
                average = int(first_level_file_dict[item][1] / (1024 * 1024 * first_level_file_dict[item][0]))
                inspect_results.append([str(i+1), item, "contains %d files" % first_level_file_dict[item][0],"with %s Bytes" % format(first_level_file_dict[item][1], ","), "average %s MB" % format(average, ",")])
        Util.format_display(inspect_results)
        print()
        print("[文件类型分布 (top 10)")
        sorted_list = sorted(file_type_count_dict.items(), key=lambda item: item[1], reverse=True)[0:10]
        display_list = []
        for item in sorted_list:
            display_list.append([item[0], "contains %d files" % item[1]])
        Util.format_display(display_list)
        print()

    def service_sync(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            c = Clock()
            c.start(len(self.get_param('difference')), "同步%d个文件"%len(self.get_param('difference')))
            finish_size = 0
            total_size = 0
            size_dict = dict()
            for item in self.get_param('difference'):
                size_dict[item] = os.stat(self.get_var('source')+item).st_size
                total_size += size_dict[item]
                print("\t","搜集文件大小：%s"%item)
            print("总共需要拷贝的大小为%s"%format(total_size/1024*1024, ","))

            for i in range(len(self.get_param('difference'))):
                item = self.get_param('difference')[i]
                source_file_path = self.get_var('source')+item
                output_file_path = self.get_var('output')+item
                output_path = "/".join(output_file_path.split("/")[0:-1])
                if not os.path.exists(output_path): os.makedirs(output_path)
                shutil.copy(source_file_path, output_file_path)
                finish_size+=size_dict[item]
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
            for item in self.get_param('difference'): print("\t", item)

    def service_showclean(self):
        if not self.are_vars_exist(['source', 'output']):return
        if self.__is_analyzed():
            for item in self.get_param('difference2'): print("\t", item)

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
        if not self.are_vars_exist(['source']):return
        self.__prepare_analyze_action()
        sha256_dict = dict()
        count = 1
        for related_path in self.get_param('source_file_info_dict'):
            full_path = self.get_var('source')+related_path
            sha256 = Util.get_sha256(full_path)
            if sha256 not in sha256_dict: sha256_dict[sha256] = [related_path]
            else:
                sha256_dict[sha256].append(related_path)
            print("\t分析no.%d\"%s\",sha256=%s"%(count, related_path, sha256))
            count+=1
        duplicate_list = [sha256_dict[key] for key in sha256_dict if len(sha256_dict[key])>1]
        if len(duplicate_list)>0:
            print("重复的文件如下：共有%d组"%len(duplicate_list))
            for duplicate_item in duplicate_list:
                print("\t重复组：", " ".join(duplicate_item))
            text = input("你想删除这%d组中的重复项吗(输入yes确认)?"%len(duplicate_list)).strip()
            if text == 'yes':
                for duplicate_item in duplicate_list:
                    for related_file_name in duplicate_item[1:]:
                        full_path_to_delete = self.get_var('source')+related_file_name
                        prompt = input("\t确定删除%s(输入yes确认)?"%full_path_to_delete)
                        if prompt == "yes":
                            os.remove(full_path_to_delete)
                self.__prepare_analyze_action()
        else:
            print("太好了，没有发现sha256相同的文件")

    def service_namespec(self):
        if not self.are_vars_exist(['source']):return
        Util.namespec(self.get_var('source'))

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
            Util.format_display(display_list)

    def __is_analyzed(self):
        if self.get_param('source_file_info_dict') is None:
            return self.__prepare_analyze_action()
        else: return True

    def service_autorunchain(self):
        self.list_configs()
        text = input("请输入多个config，用空格隔开").strip()
        if text!="":
            parts = text.split(" ")
            for item in parts:
                if len(item)>0:
                    Util.line()
                    print("尝试运行\"%s\"配置"%item)
                    if self.use_config(item):
                        self.service_analyze()
                        self.service_sync()
                        self.service_clean



