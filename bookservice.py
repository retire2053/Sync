from baseservice import *
import os
import re
import datetime
import json

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

    def service_category(self):
        if not self.__is_directory_exists('source') :return 
        text = input("仅仅分析第一级目录吗？(yes分析第一级目录，其他分析全部目录):")
        if text == "yes": level_1 = True
        else: level_1 = False

        print("开始分析目录\"%s\""%self.get_var('source'))
        for root, dirs, files in os.walk(self.get_var('source')):
            effective_file_names = [w for w in files if Util.is_effective_filename(w)]
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
            effective_file_names = sorted([w for w in files if Util.is_effective_filename(w)])
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

    def service_buildsha(self):
        if not self.__is_directory_exists('source') :return 
        if os.path.exists(self.__get_sha_file()):
            old_sha_dict = json.load(open(self.__get_sha_file(), "r"))
        else:
            old_sha_dict = dict()
        with open(self.__get_sha_file(), 'w') as fp:
            sha_dict = self.__build_sha_dict(self.get_var('source'), old_sha_dict)
            json.dump(sha_dict, fp, indent=2, ensure_ascii=False)
            print("sha文件被生成在\"%s\""%self.__get_sha_file())

    def service_checktempdir(self):
        if not self.__is_directory_exists('source') :return 
        sha_file_path = self.__get_sha_file()
        if os.path.exists(sha_file_path):
            dir = Util.input("directory", None)
            if os.path.exists(dir) and os.path.isdir(dir):
                Util.namespec(dir)

                saved_sha_dict = json.load(open(self.__get_sha_file(), "r"))

                sha_dict = dict()
                temp_dir_sha_dict = self.__build_sha_dict(dir, sha_dict)
                duplicate_items = []
                for item in temp_dir_sha_dict.items():
                    if item[1] in saved_sha_dict.values():
                        print("\t\t重复的sha：%s"%item[0])
                        duplicate_items.append(item[0])
                if len(duplicate_items)>0:
                    text = input("是否删除掉临时目录中sha相同的文件（输入yes确认）？")
                    if text == "yes":
                        for duplicate_item in duplicate_items:
                            file_path_to_remove = dir + duplicate_item
                            print("删除文件\"%s\""%file_path_to_remove)
                            os.remove(file_path_to_remove)
        else:
            print("请运行buildsha命令生成source的sha文件")

    def __get_sha_file(self): return self.get_var('source')+"/.sha_dict.json"
    
    def __build_sha_dict(self, rootdir, old_sha_dict):

        all_related_paths = Util.get_all_related_path_list(rootdir)
        
        count = 1
        for related_path in all_related_paths:
            full_path = rootdir + related_path
            if related_path not in old_sha_dict:
                sha = Util.get_sha256(full_path)
                old_sha_dict[related_path] = sha
                print("\t\t[%d]%s %s"%(count, related_path, sha))
                count+=1
        keys_to_delete = []
        for key in old_sha_dict:
            if key not in all_related_paths: keys_to_delete.append(key)
        for key in keys_to_delete: del old_sha_dict[key]
        return old_sha_dict

    