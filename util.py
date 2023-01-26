import datetime
import os
import hashlib
import math
import platform

class Util():

    @staticmethod
    def string_to_time(time_string): return datetime.datetime.strptime(time_string, "%Y/%m/%d %H:%M:%S")

    @staticmethod
    def offset_of_two_time(early_time, later_time): return (later_time - early_time).seconds * 500

    @staticmethod
    def get_next_day_oclock(start_time, oclock_int):
        next_day = start_time + datetime.timedelta(days=1)
        return datetime.datetime(next_day.year, next_day.month, next_day.day, oclock_int, 0, 0)

    @staticmethod
    def time_to_string_compact(time): return time.strftime('%Y%m%d%H%M%S')

    @staticmethod
    def iso8859_to_utf( text): return text.encode("ISO-8859-1").decode("GBK").encode("UTF-8").decode("UTF-8")

    @staticmethod
    def clean(text): return ''.join(re.findall('[\u4e00-\u9fa5a-zA-Z0-9]', text))

    @staticmethod
    def line(): print(''.join(['-'] * 80))

    @staticmethod
    def short_line(): print(''.join(['='] * 40))

    @staticmethod
    def format_display(lst, indent=8):
        if len(lst)>0:
            maxlen = [0]*len(lst[0])
            for item in lst:
                for i in range(len(item)):
                    if len(str(item[i]))>maxlen[i]:maxlen[i] = len(str(item[i]))
            for item in lst:
                if indent>0: print(''.join([" "]*indent), end='')
                for i in range(len(item)):
                    how_many_space = maxlen[i]-len(str(item[i]))
                    print(str(item[i])+''.join([" "]*how_many_space)+"  ", end='')
                print("", end='\n')
        else: 
            if indent>0: print(''.join([" "]*indent), end='')
            print("没有可显示的内容")

    @staticmethod
    def input(var_type, var_desc):
        try:
            if var_type == 'directory' :
                plat = platform.system()
                if plat=="Windows":
                    text = input("请输入目录位置")
                else:
                    text = Util.__dir_recursive_finder(os.path.expanduser("~"), show_sub_file=False)
                value = text if text is not None and os.path.isdir(text) and os.path.exists(text) else None
            elif var_type == 'file' :
                text= Util.__dir_recursive_finder(os.environ['HOME'], show_sub_file=True)
                value = text if text is not None and os.path.isfile(text) and os.path.exists(text) else None
            else:
                text = input(var_desc).strip()
                if var_type == 'time': value = datetime.datetime.strptime(text, "%Y/%m/%d %H:%M:%S")
                elif var_type == 'int': value = int(text)
                else: value = text
            if value is None:
                print("输入不正确，请检查输入。")
                return None
            else:
                return value
        except Exception as e:
            print(e.args)
            return None

    @staticmethod
    def __dir_recursive_finder(parent, show_sub_file=False):
        if not show_sub_file: message = "选择1代表选中当前子目录，选择2代表返回，选择其他数字代表进入某个子目录，回车表示放弃:"
        else: message = "选择2代表返回，选择其他子目录数字代表进入某个子目录，选择文件的数字表示确定，回车表示放弃:"
        special_dirs = {"当前目录": ".", "父目录": ".."}
        real_dirs = [w for w in sorted(os.listdir(parent)) if  os.path.exists(parent + "/" + w) and os.path.isdir(parent + "/" + w) and not w.startswith(".")]
        real_files = [] if not show_sub_file else [w for w in sorted(os.listdir(parent)) if os.path.exists(parent + "/" + w) and os.path.isfile( parent + "/" + w) and not w.startswith(".")]
        print("\t目录\"%s\"包含如下的子目录:" % parent)
        for i in range(len(list(special_dirs.keys()))): print("\t\t[%d]" % (i + 1) + " ",  list(special_dirs.keys())[i], special_dirs[list(special_dirs.keys())[i]])
        for i in range(len(real_dirs)): print( "\t\t[%d]" % (i + 1 + len(special_dirs)) + (" " if i + 1 + 2 < 10 else ""), "子目录", real_dirs[i])
        for i in range(len(real_files)): print("\t\t[%d]" % (i + 1 + len(special_dirs) + len(real_dirs)) + (" " if i + 1 + 2 + len(real_dirs) < 10 else ""), "文件", real_files[i])
        text = input(message).strip()
        if text == "": return None
        while True:
            if not text.isdigit() or int(text) < 1 or int(text) > len(special_dirs) + len(real_dirs) + len( real_files):
                text = input(message).strip()
            else:
                choice = int(text)
                if not show_sub_file:
                    if choice == 1: return parent
                    elif choice == 2: 
                        parts = parent.split("/")
                        if len(parts)<=2 : #比如parent是/Users这样的一级目录，或者/根目录
                            return Util.__dir_recursive_finder("/", show_sub_file)
                        else: return Util.__dir_recursive_finder("/".join(parent.split("/")[0:-1]), show_sub_file)
                    else:  
                        if parent=="/": return Util.__dir_recursive_finder("/" + real_dirs[choice - 2 - 1], show_sub_file)
                        else: return Util.__dir_recursive_finder(parent + "/" + real_dirs[choice - 2 - 1], show_sub_file)
                else:
                    if choice == 1: text = "0"  # 意思是需要重新选择
                    elif choice == 2:
                        parts = parent.split("/")
                        if len(parts)<=2: return Util.__dir_recursive_finder("/", show_sub_file)
                        else: return Util.__dir_recursive_finder("/".join(parent.split("/")[0:-1]), show_sub_file)
                    elif 3 <= choice <= 2 + len(real_dirs): 
                        if parent=="/": return Util.__dir_recursive_finder("/" + real_dirs[choice - 2 - 1], show_sub_file)
                        else: return Util.__dir_recursive_finder(parent + "/" + real_dirs[choice - 2 - 1], show_sub_file)
                    else: 
                        if parent=="/" : return "/" + real_files[choice - 1 - 2 - len(real_dirs)] 
                        else: return parent + "/" + real_files[choice - 1 - 2 - len(real_dirs)]

    @staticmethod
    def get_sha256(file_path):
       
        with open(file_path, 'rb') as fp:
            data = fp.read()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def is_effective_filename(file_name): 
        return True if not file_name.startswith(".") and not file_name.startswith("_") else False

    @staticmethod
    def get_all_related_path_list(dir):
        all_related_paths = []
        for root, dirs, files in os.walk(dir):
            related_root = root[len(dir):]
            print("遍历目录：root=%s, related_root=%s"%(root, related_root))            
            effective_file_names = sorted([w for w in files if Util.is_effective_filename(w)])
            for effective_file_name in effective_file_names:                
                full_related_path = os.path.join(related_root,effective_file_name)
                print("\t追加相关路径:%s"%full_related_path)
                all_related_paths.append(full_related_path)
        return all_related_paths

    @staticmethod
    def namespec(dir):
        impossible_set = set(['(', ')', '（', '）', '-', ' ', ':', '：',';','；', '——', '__', '，', ',','+'])
        remove_set = set(["、", "·", "《", "<", "》", ">","…","！","!"])
        need_to_changed_list = []
        print("分析\"%s\".................."%dir)
        for related_path in Util.get_all_related_path_list(dir):
            file_name = related_path.split("/")[-1]
            if len(impossible_set.intersection(file_name))>0 or len(remove_set.intersection(file_name))>0:
                need_to_changed_list.append(related_path)
        if len(need_to_changed_list)>0:
            print("总共有%d个文件的文件名需要整改"%len(need_to_changed_list))
            for related_path in need_to_changed_list:
                print("\t%s"%related_path)
            prompt = input("你想进行自动命名吗(输入yes确认)?")
            if prompt == "yes":
                all_allowed = False
                count = 1
                for related_path in need_to_changed_list:
                    file_name = related_path.split("/")[-1]
                    head = related_path[0:(len(related_path) - len(file_name))]
                    new_file_name = file_name
                    for chars in impossible_set:
                        if chars=="+" and "c++" in file_name and "C++" in file_name: continue
                        new_file_name = new_file_name.replace(chars, "_")
                    for chars in remove_set:
                        new_file_name = new_file_name.replace(chars, "")
                    new_file_name = new_file_name.replace("_.", ".")
                    new_file_name = new_file_name.replace("__", "_")
                    new_file_name = new_file_name.replace("【", "[")
                    new_file_name = new_file_name.replace("】", "]")
                   
                    print()
                    print("\t[%d]源文件：%s"%(count, related_path))
                    print("\t[%d]修改为：%s"%(count, head+new_file_name))
                    count+=1
                    this_allowed = False
                    if not all_allowed :
                        prompt = input("\t确认修改文件名吗(输入yes确认，all表示全部)？")
                        if prompt == "all": all_allowed = True
                        if prompt == "yes": this_allowed = True
                    if all_allowed or this_allowed: os.rename(dir+related_path, dir+head+new_file_name)
        else:
            print("太好了，没有文件的命名需要整改")    

    @staticmethod
    def vector_add(v1, v2): return [v1[i]+v2[i] for i in range(len(v1))]

    @staticmethod
    def vector_add_all(vector_list):
        return [sum(vector_list[j][i]) for j in range(len(vector_list)) for i in range(len(vector_list[0]))]

    @staticmethod
    def vector_sub(v1, v2): return [v1[i]-v2[i] for i in range(len(v1))]

    @staticmethod
    def vector_distance(v1, v2):
        return math.sqrt(sum([(v1[i]-v2[i])*(v1[i]-v2[i]) for i in range(len(v1))]))