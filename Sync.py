import os
import time
import shutil
import pickle
import sys

class Variables:

    def __init__(self, source=None, output=None, persistfile=None):
        self.__vars = ["source", "output"]
        self.__var_desc = {
            'source': '输入的目录位置，使用setsource命令修改',
            'output': '输出的目录位置，使用setoutput命令修改',
        }
        if persistfile is None:self.__var_persistence_file = os.environ['HOME'] + "/sync.save"
        else : self.__var_persistence_file = persistfile

        if os.path.exists(self.__var_persistence_file):
            self.__var_dict = pickle.load(open(self.__var_persistence_file, "rb"))
            for item in self.__vars:
                if item not in self.__var_dict: self.__var_dict[item] = None
        else:
            self.__var_dict = dict.fromkeys(self.__vars)
        if source is not None: self.__var_dict['source'] = source
        if output is not None: self.__var_dict['output'] = output

    def __save_var(self): pickle.dump(self.__var_dict, open(self.__var_persistence_file, "wb"))
    def get_var(self, var_name): return self.__var_dict[var_name]
    def list_vars(self):
        for item in self.__vars: print("\t", "参数 [%s] (%s) = %s" % (item, self.__var_desc[item], self.__var_dict[item]))

    def set_var(self, var_name):
        if var_name in ['source', 'output']: self.__set_directory(var_name)

    def __set_directory(self, var_name):
        print("当前参数 %s = %s" % (var_name, self.__var_dict[var_name]))
        text = input(self.__var_desc[var_name]+":").strip()
        if os.path.isdir(text) and os.path.exists(text):
            if text.endswith("/"): text = text[0:len(text)-1]
            self.__var_dict[var_name] = text
            self.__save_var()
            print("当前参数 %s = %s" % (var_name, self.__var_dict[var_name]))
        else:
            print("输入的不是目录或者目录不存在，请检查输入。")

class Clock:
    def __init__(self):self.__value = []

    def start(self, total_length, taskname):
        self.__value = {'stime': time.time(), 'count':0, 'progress':0, 'length':total_length, 'taskname':taskname}
        print("\t", taskname)

    def count_by_number(self):
        self.__value['count'] += 1
        new_progress = int(self.__value['count'] * 100 / self.__value['length'])
        if new_progress > self.__value['progress']:
            self.__value['progress'] = new_progress
            time_elapse = time.time() - self.__value["stime"]
            time_left = (100 - new_progress)*time_elapse/new_progress
            print("\t",self.__value["taskname"], "进度%d%%"%self.__value['progress'], "任务耗时%d秒"%(time_elapse), "预估剩余%d小时%d分钟%d秒"%(int(time_left/3600), int(time_left%3600/60), int(time_left%60)))

    def count(self, new_progress_base_on_100):
        self.__value['count'] += 1
        if new_progress_base_on_100 > self.__value['progress']:
            self.__value['progress'] = new_progress_base_on_100
            time_elapse = time.time() - self.__value["stime"]
            time_left = (100 - new_progress_base_on_100)*time_elapse/new_progress_base_on_100
            print("\t",self.__value["taskname"], "进度%d%%"%self.__value['progress'], "任务耗时%d秒"%(time_elapse), "预估剩余%d小时%d分钟%d秒"%(int(time_left/3600), int(time_left%3600/60), int(time_left%60)))


    def finish(self):
        print("\t", self.__value["taskname"] , "已结束")
        print("".join(["-"] * 40))

class Sync:

    def __init__(self):
        self.__source = None
        self.__output = None
        self.__source_file_info_dict = None
        self.__output_file_info_dict = None
        self.__difference = None
        self.__difference2 = None
        self.__search_results = None
        self.__inspect_results = []

    def set_source(self, source): self.__source = source
    def set_output(self, output): self.__output = output

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
        if self.__source_file_info_dict is None or self.__output_file_info_dict is None: return None
        difference = []
        difference2 = []
        for item in list(self.__source_file_info_dict.keys()):
            if item not in list(self.__output_file_info_dict.keys()):
                difference.append(item)
            elif self.__source_file_info_dict[item]!=self.__output_file_info_dict[item]:
                difference.append(item)
        for item in list(self.__output_file_info_dict.keys()):
            if item not in list(self.__source_file_info_dict.keys()):
                difference2.append(item)
        return difference,difference2

    def __prepare_analyze_action(self):
        if self.__source is None or not os.path.exists(self.__source) :
            print("请先使用setsource来设置[source]")
            return False
        elif self.__output is None or not os.path.exists(self.__output):
            print("请先使用setoutput来设置[output]")
            return False
        else:
            self.__source_file_info_dict = self.__get_directory_info_dict(self.__source)
            self.__output_file_info_dict = self.__get_directory_info_dict(self.__output)
            self.__difference,self.__difference2 = self.__compare()
            return True

    def analyze(self):
        if self.__prepare_analyze_action():
            print("[source] %s下包含%d个文件" % (self.__source, len(list(self.__source_file_info_dict.keys()))))
            print("[output] %s下包含%d个文件" % (self.__output, len(list(self.__output_file_info_dict.keys()))))
            print()
            print("其中有%d个文件在[source]中，但并不在[output]中" % len(self.__difference))
            print("同时，有%d个文件在[output], 但并不在[source]中" % len(self.__difference2))
            print()
            self.__detect_a_directory()

    def __detect_a_directory(self):
        total_bytes = 0
        first_level_dirs = [w for w in os.listdir(self.__source) if os.path.isdir(self.__source + "/" + w) and not w.startswith(".")]
        first_level_file_dict = dict.fromkeys(first_level_dirs)
        for item in first_level_file_dict: first_level_file_dict[item] = [0, 0]

        file_type_count_dict = dict()
        for x in self.__source_file_info_dict:
            total_bytes += self.__source_file_info_dict[x]
            first_level_dir = x.split("/")[1]
            if first_level_dir in first_level_file_dict:
                values = first_level_file_dict[first_level_dir]
                first_level_file_dict[first_level_dir][0] = values[0] + 1
                first_level_file_dict[first_level_dir][1] = values[1] + self.__source_file_info_dict[x]
            file_type = x.split("/")[-1].split(".")[-1].lower()
            if file_type in file_type_count_dict:
                file_type_count_dict[file_type] += 1
            else:
                file_type_count_dict[file_type] = 1

        print("[source] %s下包含总共占用磁盘%s字节" %(self.__source,format(total_bytes, ",")))
        print()
        print("[子目录]")
        self.__inspect_results = []

        for i in range(len(first_level_dirs)):
            item = first_level_dirs[i]
            average = int(first_level_file_dict[item][1] / (1024 * 1024 * first_level_file_dict[item][0]))
            self.__inspect_results.append([str(i+1), item, "contains %d files" % first_level_file_dict[item][0],
                                 "with %s Bytes" % format(first_level_file_dict[item][1], ","),
                                 "average %s MB" % format(average, ",")])
        self.__format_display(self.__inspect_results)
        print()
        print("[文件类型分布 (top 10)")
        sorted_list = sorted(file_type_count_dict.items(), key=lambda item: item[1], reverse=True)[0:10]
        display_list = []
        for item in sorted_list:
            display_list.append([item[0], "contains %d files" % item[1]])
        self.__format_display(display_list)
        print()

    def sync(self):
        if self.__is_analyzed():
            c = Clock()
            c.start(len(self.__difference), "同步%d个文件"%len(self.__difference))
            total_size = 0
            for x in self.__difference: total_size+=self.__source_file_info_dict[x]
            finish_size = 0
            for i in range(len(self.__difference)):
                item = self.__difference[i]
                source_file_path = self.__source+item
                output_file_path = self.__output+item
                output_path = "/".join(output_file_path.split("/")[0:-1])
                if not os.path.exists(output_path): os.makedirs(output_path)
                shutil.copy(source_file_path, output_file_path)
                finish_size+=self.__source_file_info_dict[item]
                c.count(int(finish_size*100/total_size))
            c.finish()
            self.__prepare_analyze_action()

    def clean(self):
        if self.__is_analyzed():
            c = Clock()
            c.start(len(self.__difference2), "删除%d个文件"%len(self.__difference2))
            for i in range(len(self.__difference2)):
                item = self.__difference2[i]
                output_file_path = self.__output+item
                os.remove(output_file_path)
                c.count_by_number()
            c.finish()
            self.__prepare_analyze_action()

    def show_sync(self):
        if self.__is_analyzed():
            temp_dict = dict()
            for item in self.__difference: temp_dict[item] = self.__source_file_info_dict[item]
            sorted_list = sorted(temp_dict.items(), key=lambda item: item[1], reverse = True)
            if len(sorted_list)>30: sorted_list = sorted_list[0:30]
            display_list = []
            for item in sorted_list:
                display_list.append(["占用磁盘%s"%(format(item[1]/1024*1024, ",")), self.__source+item[0]])
            self.__format_display(display_list)


    def show_clean(self):
        if self.__is_analyzed():
            temp_dict = dict()
            for item in self.__difference2: temp_dict[item] = self.__output_file_info_dict[item]
            sorted_list = sorted(temp_dict.items(), key=lambda item: item[1], reverse = True)
            if len(sorted_list)>30: sorted_list = sorted_list[0:30]
            display_list = []
            for item in sorted_list:
                display_list.append(["占用磁盘%s"%(format(item[1]/1024*1024, ",")), self.__output+item[0]])
            self.__format_display((display_list))

    def search(self):
        if self.__is_analyzed():
            text = input("请输入你想要检索的字符串:").strip().lower()
            count = 1
            self.__search_results = []
            for x in self.__source_file_info_dict:
                lower_case = x.lower()
                if text in lower_case:
                    lower_case_parts = lower_case.split("/")
                    parts = x.split("/")
                    for i in range(len(lower_case_parts)-1, -1, -1):
                        if text in lower_case_parts[i]: break
                    sub_path = "/".join(parts[0:i+1])
                    if sub_path not in self.__search_results: self.__search_results.append(sub_path)
            for x in self.__search_results:
                print("\t", count, x)
                count+=1
            if len(self.__search_results)==1:
                os.system("open \"%s%s\"" % (self.__source, self.__search_results[0]))
                print("\t只检索到一个文件，已经为您打开")
            else: print("\t请使用open命令来打开某个文件")

    def find_duplicate(self):
        if self.__is_analyzed():
            dup_dict = dict()
            for x in self.__source_file_info_dict:
                key = (x.split("/")[-1], self.__source_file_info_dict[x])
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
                        print("delete no.%d"%(i+1), self.__source + "/" + to_delete[i])
                        os.remove(self.__source+"/"+ to_delete[i])

    def open(self):
        if self.__is_analyzed():
            if self.__search_results is None or len(self.__search_results)==0:
                print("请先运行'analyze'和'search'命令")
                return
            text = input("请输入文件的编号:").strip()
            if text.isdigit() :
                id = int(text)-1
                if len(self.__search_results)>=id>=0:
                    os.system("open \"%s%s\""%(self.__source, self.__search_results[id]))

    def big(self):
        if self.__is_analyzed():
            lst = sorted(self.__source_file_info_dict.items(),key=lambda s:s[1], reverse = True)[0:100]
            display_list = []
            for i in range(len(lst)):
                display_list.append(["[%d]"%(i+1),  "\t占用磁盘%sMB"%format(int(lst[i][1]/(1024*1024)), ',') , "[%s]"%lst[i][0]])
            self.__format_display(display_list)

    def __is_analyzed(self):
        if self.__source_file_info_dict is None:
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

class Console:

    def __init__(self, variables, sync):
        self.__variables = variables
        self.__sync = sync
        self.__sync.set_source(self.__variables.get_var("source"))
        self.__sync.set_output(self.__variables.get_var("output"))
        self.__commands = ['var', 'setsource', 'setoutput', 'analyze', 'sync','showsync', 'showclean', 'clean', 'inspect', 'search','open', 'duplicate', 'big','help', 'version', 'exit']
        self.__command_desc = {
            'var':'显示配置的参数',
            'setsource' : '设置源目录',
            'setoutput' : '设置目标目录',
            'analyze': '分析两个目录结构',
            'sync': '将source的差异项向output拷贝',
            'showsync':'查看哪些source中的文件要被拷贝',
            'showclean': '查看哪些output中的文件需要被清理',
            'clean': '清理output中的所有非备份文件',
            'inspect': '探查source中的层级目录',
            'search':'在source中搜索某个文件名',
            'open':'打开find的结果中的指定文件',
            'duplicate':'在source中查找重复文件',
            'big':'显示top100大文件',
            'help': '打印所有命令的信息',
            'version': '了解程序的版本',
            'exit': '退出程序',
        }

    def version(self):
        print("=".join([''] * 40))
        print("同步、文件管理程序")
        print("最后更新日期：2022.09.30 16:00:00 by Jacob")
        print("-".join(['']*40))

    def work(self):
        self.version()
        self.__help()
        command = self.__get_input_command()
        while command != 'exit':
            if command not in self.__commands: print("错误的命名，请重新输入，或者输入help获得提示")
            else:
                #try:
                self.__call_service(command)
                #except Exception as e: print(e.args)
            command = self.__get_input_command()
        print("程序结束")

    def __get_input_command(self): return input("请输入命令，或者敲入help获得提示:")

    def __call_service(self, command):
        print("你当前的输入是", command)
        print(''.join(['-'] * 40))
        if command == 'var':self.__variables.list_vars()
        elif command == 'setsource':
            self.__variables.set_var("source")
            self.__sync.set_source(self.__variables.get_var("source"))
        elif command == 'setoutput':
            self.__variables.set_var("output")
            self.__sync.set_output(self.__variables.get_var("output"))
        elif command == 'analyze': self.__sync.analyze()
        elif command == 'sync' : self.__sync.sync()
        elif command == 'showsync' : self.__sync.show_sync()
        elif command == 'showclean':self.__sync.show_clean()
        elif command == 'clean':self.__sync.clean()
        elif command == 'inspect' : self.__sync.inspect()
        elif command == 'search': self.__sync.search()
        elif command == 'open':self.__sync.open()
        elif command == 'duplicate':self.__sync.find_duplicate()
        elif command == 'big':self.__sync.big()
        elif command == "version":self.version()
        elif command == 'help':self.__help()
        else:
            print("输入错误，请检查拼写；或者该服务尚未实现，请输入help获得提示。")
        print(''.join(['='] * 40))

    def __are_vars_exist(self, var_list):
        if len([var for var in var_list if self.__variables.get_var(var) is None])>0:
            print("\t请先设置参数%s，才能使用本命令。" % ("".join(var_list)))
            return False
        return True

    def __help(self):
        print("你可以使用如下的命令:")
        for item in self.__commands: print("\t[%s] - %s" % (item, self.__command_desc[item]))

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv)==4:
        source = sys.argv[1]
        output = sys.argv[2]
        persistfile = sys.argv[3]
    else:
        source = None
        output = None
        persistfile = None
    sync = Sync()
    variables = Variables(source, output, persistfile)
    console = Console(variables, sync)
    console.work()