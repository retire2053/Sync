import sys
from util import Util

class BaseService:

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
    def get_app_version(self): return self.__app_info['version']

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