from baseservice import *
import sys

class EnvironmentService(BaseService):
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
        print("版本：%s"%self.get_app_version())
        print(''.join(['-'] * 80))
    
    def service_exit(self):
        print("程序正常退出")
        sys.exit(0)