import sys
from util import Util

class PLibraryService():

    def __init__(self, context):
        self.__command_group = context["command_group"]
        self.__variables = context["variables"]
        self.__app_info = context["app_info"]
        self.__context = context

    def are_vars_exist(self, var_list):
        no_problem = True
        for item in var_list:
            if self.__variables.get_var(item) is None:
                print("请先设定参数%s" % item)
                no_problem = False
        return no_problem

    def get_var_dict(self):return self.__variables.get_var_dict()
    def get_var(self, var_name):return self.__variables.get_var(var_name)
    def set_var(self, var_name):return self.__variables.set_var(var_name)
    def get_var_list(self):return self.__variables.get_vars()
    def match_var_name(self, text):return self.__variables.match_var_name(text)
    def list_vars(self):return self.__variables.list_vars()
    def save_config(self, name): self.__variables.save_config(name)
    def list_configs(self):  self.__variables.list_configs()
    def use_config(self, name):return self.__variables.use_config(name)
    def remove_config(self, name): self.__variables.remove_config(name)
    def get_command_group(self):return self.__command_group
    def get_app_name(self):return self.__app_info['name']
    def get_app_desc(self):return self.__app_info['desc']
    def get_app_shortname(self):return self.__app_info['shortname']

    def set_param(self, key, value): 
        if self.__class__ in self.__context: 
            self.__context[self.__class__][key] = value
        else: 
            self.__context[self.__class__] = {key: value}

    def get_param(self, key):
        if self.__class__ in self.__context: 
            if key in self.__context[self.__class__]:
                return self.__context[self.__class__][key]
        return None    

class EnvironmentService(PLibraryService):
    def __init__(self, context): super().__init__(context)
    def service_var(self): 
        self.list_vars()
        Util.line()
        self.list_configs()

    def service_set(self):
        self.list_vars()
        var_name = input("请输入需要设置的参数名称:")
        var_name = self.match_var_name(var_name)
        if var_name is not None: self.set_var(var_name)
        else: print("请输入完整的参数名，或至少前3个字符进行模糊匹配")

    def service_removeconfig(self):
        self.list_configs()
        text = input("请输入要使用的配置的名称:").strip()
        if len(text)>0:
            self.remove_config(text)
    
    def service_saveconfig(self):
        self.list_configs()
        text = input("请输入要使用的配置的名称:").strip()
        if len(text)>0:
            self.save_config(text)
    
    def service_useconfig(self):
        self.list_configs()
        text = input("请输入要使用的配置的名称:").strip()
        if len(text)>0:
            self.use_config(text)
    
    def service_help(self):
        print("可以使用如下的这些命令:")
        command_group = self.get_command_group()
        for group in command_group:
            print(group)
            for command in command_group[group]['command']:
                print("\t[%s] - %s" % (command, command_group[group]['command'][command]))

    def service_version(self):
        print(''.join(['-'] * 80))
        print(self.get_app_name())
        print(self.get_app_desc())
        print(''.join(['-'] * 80))
    
    def service_exit(self):
        print("程序正常退出")
        sys.exit(0)