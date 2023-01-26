import os,pickle
from util import Util
from copy import deepcopy

class Variables:

    def __init__(self, var_difinition):
        self.__var_definition = var_difinition
        self.__vars = list(self.__var_definition['variables'].keys())
        print(os.environ)
        self.__var_persistence_file = os.path.join(os.path.expanduser("~"),self.__var_definition['storage_file_name'])
        self.__var_dict = None
        self.__configs = None

        if os.path.exists(self.__var_persistence_file):
            object = pickle.load(open(self.__var_persistence_file, "rb"))
            if object is not None and type(object)== tuple :
                self.__var_dict, self.__configs = object
                for item in self.__vars:
                    if item not in self.__var_dict: self.__var_dict[item] = None
        if self.__var_dict is None: 
            self.__var_dict = dict.fromkeys(self.__vars)
            self.__configs = dict()

    def __save_var(self): 
        result = (self.__var_dict, self.__configs)
        pickle.dump(result, open(self.__var_persistence_file, "wb"))

    def get_var(self, var_name): return self.__var_dict[var_name]
    def get_vars(self):return self.__vars
    def get_var_dict(self):return self.__var_dict
    def list_vars(self):
        for item in self.__vars: print("\t", "参数 [%s] (%s) = %s" % (item, self.__var_definition['variables'][item]['desc'], self.__var_dict[item]))

    def match_var_name(self, text):
        if text is not None and len(text.strip())>2:
            matched =[w for w in self.__vars if w.startswith(text)]
            if len(matched)==1: return matched[0]
        return None

    def __print_var(self, var_name): print("当前参数 %s = %s" % (var_name, self.__var_dict[var_name]))

    def set_var(self, var_name):
        self.__print_var(var_name)
        value = Util.input(self.__var_definition['variables'][var_name]['type'], self.__var_definition['variables'][var_name]['desc'])
        if value is not None:
            self.__var_dict[var_name] = value
            self.__save_var()
            self.__print_var(var_name)

    def set_var_value(self, var_name, var_value):
        self.__var_dict[var_name] = var_value
        self.__save_var()
        self.__print_var(var_name)

    def list_configs(self):
        if len(self.__configs)>0:
            print("已经存在了这些配置")
            for key in self.__configs:
                print("配置名称\"%s\""%key)
                for item in self.__configs[key]:
                    print("\t[%s] = %s"%(item, self.__configs[key][item]))
        else: print("还没有创建配置")        

    def remove_config(self, name):
        if name in self.__configs: del self.__configs[name]
    
    def save_config(self, name):
        new_var_dict = deepcopy(self.__var_dict)
        self.__configs[name] = new_var_dict
        self.__save_var()
    
    def use_config(self, name):
        if name in self.__configs:
            values = self.__configs[name]
            for item in self.__vars:
                if item in values:
                    self.__var_dict[item] = values[item]
            self.__save_var()
            return True
        else: 
            print("配置\"%s\"没有找到"%name)
            return False

        
