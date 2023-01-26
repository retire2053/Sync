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
        export_file_name = os.path.join(os.path.expanduser("~"),"book_list_%s.txt"%(Util.time_to_string_compact(datetime.datetime.now())))
        f = open(export_file_name, "w")
        f.write("\n".join(results))
        f.close()
        print("book list has been exported to %s"%export_file_name)

    def service_buildindex(self):
        if not self.__is_directory_exists('source') :return 
        old_index_list = self.__load_json_list()
        print("index文件目前包含总条目数量为%d"%len(old_index_list))
        with open(self.__get_index_file(), 'w') as fp:
            index_list = self.__build_index_file(self.get_var('source'), old_index_list)
            json.dump(index_list, fp, indent=2, ensure_ascii=False)
            print("index文件被生成在\"%s\"，总条目数量为%d"%(self.__get_index_file(), len(index_list)))

    def service_find(self):
        if not self.are_vars_exist(['source']):return
        if not os.path.exists(self.__get_index_file()): 
            print("请先试用buildindex来创建索引文件")
            return
        
        index_list = self.__load_json_list()
        saved_related_path_list = []
        for item in index_list: saved_related_path_list.append(item['path'])
            
        text = input("请输入你想要检索的字符串:").strip().lower()
        count = 1
        find_results = []
        for related_path in saved_related_path_list:
            if text in related_path:
                find_results.append(related_path)
        for x in find_results:
            print("\t", count, x)
            count+=1
        if len(find_results)==1:
            os.system("open \"%s%s\"" % (self.get_var('source'), find_results[0]))
            print("\t只检索到一个文件，已经为您打开")
        elif len(find_results)==0:
            print("\t没有找到结果，请重新检索")
        else:
            print("\t请使用open命令来打开某个文件")
            while True:
                choice = input("请输入具体的要打开的文件的编号(回车退出)?")
                if choice=="": break
                elif choice.isdigit() :
                    num = int(choice)
                    if 1<=num<=len(find_results): 
                        os.system("open \"%s%s\"" % (self.get_var('source'), find_results[num-1]))
                    else: print("输入错误，请输入一个介于[1,%d]之间的整数"%len(find_results))
                else: print("请输入一个整数")

    def service_dup(self):
        if not self.are_vars_exist(['source']):return
        if not os.path.exists(self.__get_index_file()): 
            print("请先试用buildindex来创建索引文件")
            return
        index_list = self.__load_json_list()
        count = 1
        dup_dict = dict()
        print("分析%d个文件的sha"%len(index_list))
        for item in index_list:
            sha256 = item['sha256']
            if sha256 not in dup_dict: dup_dict[sha256] = [item['path']]
            else:
                dup_dict[sha256].append(item['path'])
            #print("\t分析no.%d\"%s\",sha256=%s"%(count, related_path, sha256))
            count+=1
        duplicate_list = [dup_dict[key] for key in dup_dict if len(dup_dict[key])>1]
        if len(duplicate_list)>0:
            print("重复的文件如下：共有%d组"%len(duplicate_list))
            for i in range(len(duplicate_list)):
                for item in duplicate_list[i]:
                    print("\t重复组[%d]：%s"%(i+1,item))
                print()
            text = input("确定只保留每组第一个非重复项的吗(yes表示确认)？")
            if text == "yes":
                for i in range(len(duplicate_list)):
                    for j in range(1, len(duplicate_list[i]), 1):
                        print("\t删除[%d]：%s"%(i+1, duplicate_list[i][j]))
                        os.remove(self.get_var('source')+duplicate_list[i][j])
                    print()
                print("重建索引文件")
                self.service_buildindex()
                print("索引文件重建完毕")

        else:
            print("太好了，没有发现sha256相同的文件")

    def service_checktempdir(self):
        if not self.__is_directory_exists('source') :return 
        if not os.path.exists(self.__get_index_file()): 
            print("请先试用buildindex来创建索引文件")
            return
        
        dir = Util.input("directory", None)
        if os.path.exists(dir) and os.path.isdir(dir):
            Util.namespec(dir)
            index_list = self.__load_json_list()
            saved_sha256_list = []
            for item in index_list: saved_sha256_list.append(item['sha256'])

            sha_dict = dict()
            temp_dir_sha_dict = self.__build_sha_dict(dir, sha_dict)
            duplicate_items = []
            for item in temp_dir_sha_dict.items():
                if item[1] in saved_sha256_list:
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

    def __get_index_file(self):return self.get_var('source') + os.sep + ".index_dict.json"

    def __load_json_list(self):
        if os.path.exists(self.__get_index_file()): 
            try:
                index_list = json.load(open(self.__get_index_file(), "r"))
                if index_list is not None: return index_list
            except Exception as e:
                print("读取%s中发生错误：%s"%(self.__get_index_file(), str(e.args)))
        return []

    def __build_index_file(self, rootdir, old_index_list):
        print("要创建索引的根目录是:%s"%rootdir)
        all_related_paths = Util.get_all_related_path_list(rootdir)

        if len(old_index_list) == 0:
            count = 1
            for related_path in all_related_paths:
                full_path = rootdir + os.sep + related_path
                print("[%d]完整路径:%s:"%(count, full_path))
                sha256 = Util.get_sha256(full_path) 
                old_index_list.append({'path':related_path, 'filelen':os.stat(full_path).st_size, 'sha256':sha256})
                print("\t[%d]增加文件的索引信息：%s"%(count, full_path))
                count+=1
            return old_index_list
        else:
            count = 1
            saved_related_path_list = []
            for item in old_index_list: saved_related_path_list.append(item['path'])
            
            for related_path in all_related_paths:
                if related_path not in saved_related_path_list:
                    full_path = rootdir + os.sep + related_path
                    sha256 = Util.get_sha256(full_path)     
                    old_index_list.append({'path':related_path, 'filelen':os.stat(full_path).st_size, 'sha256':sha256})
                    print("[%d]增加文件的索引信息：%s"%(count, full_path))
                    count+=1
            print()
            items_to_delete = []
            count = 1
            for i in range(len(old_index_list)):
                if old_index_list[i]['path'] not in all_related_paths:
                    print("[%d]拟删除%s"%(count, old_index_list[i]['path']))
                    items_to_delete.append(i)
                    count+=1
            if len(items_to_delete)>0:
                print("删除掉%d个索引信息"%len(items_to_delete))
                for id in reversed(items_to_delete): 
                    old_index_list.pop(id)
            return old_index_list

    def service_filelen(self):
        if not self.__is_directory_exists('source') :return 
        print("开始分析目录\"%s\""%self.get_var('source'))
        file_len_dict = dict()
        MIN_THRESHOLD = 60
        text = input("请输入最低的文件长度，最少为%d："%MIN_THRESHOLD)
        if text.isdigit():
            threshold = int(text)
            if threshold > MIN_THRESHOLD:
                total_file_count = 0
                for root, dirs, files in os.walk(self.get_var('source')):
                    effective_file_names = [w for w in files if Util.is_effective_filename(w)]
                    for file_name in effective_file_names:
                        file_length = len(file_name)
                        if file_length > threshold:
                            print("文件：%s 长度=%d"%(file_name, file_length))
                            ext = file_name.split(".")[-1]
                            parts = file_name[0:-1*(len(ext)+1)].split("_")
                            if len(parts)<=1:print("文件需手动处理")
                            for i in range(1,len(parts),1):
                                suggest_file_name = "_".join(file_name[0:-1*(len(ext)+1)].split("_")[0:i])+"."+ext
                                print("\t[%d] %s"%(i, suggest_file_name))
                            text = input("\t确认你的选择(1-%d)，输入m手动，输入q退出："%(len(parts)-1))
                            if text.isdigit():
                                choice = int(text)
                                if choice>=1 and choice<len(parts):
                                    suggest_file_name = "_".join(file_name[0:-1*(len(ext)+1)].split("_")[0:choice])+"."+ext
                                    os.rename(root+"/"+file_name, root+"/"+suggest_file_name) 
                                    print("完成修改，修改为%s"%suggest_file_name)
                                else:print("没有更改，或者输入错误")
                            elif text=="q": 
                                print("退出改名")
                                break
                            elif text=="m":
                                new_name=input("请输入新的文件名：")
                                confirm = input("确认使用\"%s\"(输入y确认)?"%new_name)
                                if confirm == "y": os.rename(root+"/"+file_name, root+"/"+new_name) 
                                else: print("修改取消")
                            else: print("没有更改，或者输入错误")
                            print()
                            total_file_count+=1
                            if file_length not in file_len_dict: file_len_dict[file_length]=1
                            else: file_len_dict[file_length]+=1
                result = sorted(file_len_dict.items(), key=lambda item: item[0], reverse=True)
                print("经统计，文件名长度超过%d的文件有%d个"%(threshold,total_file_count))
                print(result)
            else: print("输入错误，不能少于30")
        else:
            print("输入错误，请输入数字")

    