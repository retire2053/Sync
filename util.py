import datetime
import os

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
    def iso8859_to_utf(self, text): return text.encode("ISO-8859-1").decode("GBK").encode("UTF-8").decode("UTF-8")

    @staticmethod
    def clean(self,text): return ''.join(re.findall('[\u4e00-\u9fa5a-zA-Z0-9]', text))

    @staticmethod
    def line(): print(''.join(['-'] * 80))

    @staticmethod
    def short_line(): print(''.join(['='] * 40))

    @staticmethod
    def input(var_type, var_desc):
        try:
            if var_type == 'directory' :
                text= Util.__dir_recursive_finder(os.environ['HOME'], show_sub_file=False)
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
                    elif choice == 2: return Util.__dir_recursive_finder("/".join(parent.split("/")[0:-1]), show_sub_file)
                    else:  return Util.__dir_recursive_finder(parent + "/" + real_dirs[choice - 2 - 1], show_sub_file)
                else:
                    if choice == 1: text = "0"  # 意思是需要重新选择
                    elif choice == 2:return Util.__dir_recursive_finder("/".join(parent.split("/")[0:-1]), show_sub_file)
                    elif 3 <= choice <= 2 + len(real_dirs): return Util.__dir_recursive_finder(parent + "/" + real_dirs[choice - 2 - 1], show_sub_file)
                    else: return parent + "/" + real_files[choice - 1 - 2 - len(real_dirs)]

