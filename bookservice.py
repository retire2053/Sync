from baseservice import *
import os
import re
import datetime

class BookService(BaseService):

    def __init__(self, context): 
        super().__init__(context)
        self.__regex = re.compile(r'\[[\u4e00-\u9fa5A-Za-z0-9]+\]')

    def __get_category_head(self, text, level_1):
        result = self.__regex.findall(text)
        if level_1: result = result[0:1]
        if result is not None and len(result)>0: return "".join(result) 
        return "无类别"

    def __is_directory_exists(self, var_name):
        if not self.are_vars_exist([var_name]): return False
        elif not os.path.exists(self.get_var(var_name)): 
            print("目录\"%s\"不存在"%self.get_var(var_name))
            return False
        else: return True

    def __is_effective_filename(self, file_name): return True if not file_name.startswith(".") and not file_name.startswith("_") else False

    def service_category(self):
        if not self.__is_directory_exists('source') :return 
        text = input("仅仅分析第一级目录吗？(yes分析第一级目录，其他分析全部目录):")
        if text == "yes": level_1 = True
        else: level_1 = False

        print("开始分析目录\"%s\""%self.get_var('source'))
        for root, dirs, files in os.walk(self.get_var('source')):
            effective_file_names = [w for w in files if self.__is_effective_filename(w)]
            print("\t子目录\"%s\"(%d)"%(root, len(effective_file_names)))
            category_dict = dict()

            for file_name in effective_file_names:
                head = self.__get_category_head(file_name, level_1)
                #print(file_name, "head is %s"%head)
                if head in category_dict: category_dict[head]+=1
                else: category_dict[head]=1
            if level_1:
                result = sorted(category_dict.items(), key=lambda item: item[1], reverse=True)
            else:
                result = sorted(category_dict.items(), key=lambda item: item[0], reverse=False)
            Util.format_display(result, indent = 12)
        print("目录分析完成")

    def service_exportlist(self):
        if not self.__is_directory_exists('source') :return 
        results = []
        for root, dirs, files in os.walk(self.get_var('source')):
            effective_file_names = sorted([w for w in files if self.__is_effective_filename(w)])
            if len(effective_file_names)>0:
                dir_list = "_".join([w for w in root[len(self.get_var('source')):].split("/") if w !=""])
                results.append(dir_list)
                for file_name in effective_file_names:
                    results.append("\t%s"%file_name)
        export_file_name = os.environ['HOME'] + "/book_list_%s.txt"%(Util.time_to_string_compact(datetime.datetime.now()))
        f = open(export_file_name, "w")
        f.write("\n".join(results))
        f.close()
        print("book list has been exported to %s"%export_file_name)