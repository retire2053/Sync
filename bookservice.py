from baseservice import *
import os
import re

class BookService(BaseService):

    def __init__(self, context): 
        super().__init__(context)
        self.__regex = re.compile(r'\[[\u4e00-\u9fa5A-Za-z0-9]+\]')

    def __get_category_head(self, text, level_1):
        result = self.__regex.findall(text)
        if level_1: result = result[0:1]
        if result is not None and len(result)>0: return "".join(result) 
        return "无类别"
        
    def service_category(self):
        if not self.are_vars_exist(['source']): return
        if not os.path.exists(self.get_var('source')): 
            print("目录\"%s\"不存在"%self.get_var('source'))
            return 
        text = input("仅仅分析第一级目录吗？(yes分析第一级目录，其他分析全部目录):")
        if text == "yes": level_1 = True
        else: level_1 = False

        print("开始分析目录\"%s\""%self.get_var('source'))
        for root, dirs, files in os.walk(self.get_var('source')):
            effective_file_names = [w for w in files if not w.startswith(".") and not w.startswith("_")]
            print("\t子目录\"%s\"(%d)"%(root, len(effective_file_names)))
            category_dict = dict()

            for file_name in effective_file_names:
                head = self.__get_category_head(file_name, level_1)
                #print(file_name, "head is %s"%head)
                if head in category_dict: category_dict[head]+=1
                else: category_dict[head]=1
            result = sorted(category_dict.items(), key=lambda item: item[0], reverse=False)
            Util.format_display(result, indent = 12)
        print("目录分析完成")