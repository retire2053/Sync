import traceback
from variables import Variables
from util import Util
from syncservice import *
from plibraryservice import *

class CommandHub:
    def __init__(self, context):
        self.__context = context
        self.__command_group = context["command_group"]
        self.__commands = []
        for group in self.__command_group:
            for command in self.__command_group[group]['command']: self.__commands.append(command)

    def loop(self):
        message = "请输入命令："
        command = input(message)
        while True:
            if command not in self.__commands: print("命令输入错误，请重新输入")
            else:
                print("你输入的命令是：", command)
                Util.line()
                try:
                    self.execute(command)
                    Util.line()
                except Exception as e:
                    print(e.args)
                    traceback.print_exc()
                    Util.line()
            command = input(message)

    def execute(self, command):
        if command in self.__commands:
            for key in self.__command_group:
                if command in self.__command_group[key]['command']:
                    class_name = self.__command_group[key]['class']
                    context = self.__context
                    eval("%s(%s).service_%s()"%(class_name, "context", command))

if __name__ == "__main__":
    var_definition = {
            'storage_file_name':'.test.save',
            'types':['directory', 'file', 'time', 'int', 'text'],
            'variables':{
                'source': {'type': 'directory', 'desc': '设置source参数，代表原始目录的根位置'},
                'output': {'type': 'directory', 'desc': '设置output参数，代表目标目录的根位置'},
            }
        }
    app_info = {
                'name': '个人文档数据库管理',
                'desc' :'一个简单的程序，用来管理个人的数据，可以完成同步，查找，信息整理和挖掘',
                'shortname' : 'plibrary',
            }
    command_group = {
        "环境命令": {
                'class':'EnvironmentService',
                'command':{
                    'var': '显示当前的参数的值',
                    'set': '设置各类参数的值',
                    'saveconfig' :'将当前参数值保存成为一个配置',
                    'removeconfig' :'删除某一个配置',
                    'useconfig' :'使用某一个配置的值',
                    'help': '打印所有命令的信息',
                    'version': '了解程序的版本',
                    'exit':'退出应用程序',
                }
            },
        "同步命令": {
            'class':'SyncService',
            'command':{
                'analyze': '分析两个目录结构',
                'sync': '将source的差异项向output拷贝',
                'showsync':'查看哪些source中的文件要被拷贝',
                'showclean': '查看哪些output中的文件需要被清理',
                'clean': '清理output中的所有非备份文件',
                'search':'在source中搜索某个文件名',
                'open':'打开find的结果中的指定文件',
                'duplicate':'在source中查找重复文件',
                'big':'显示top100大文件',
            }
        }
    }
    context =  dict()
    context["command_group"] = command_group
    context["app_info"] = app_info
    context["variables"] = Variables(var_definition)

    command_hub = CommandHub(context)
    command_hub.execute("version")
    command_hub.execute("help")
    command_hub.loop()


            