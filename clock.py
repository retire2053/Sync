import time

class Clock:
    def __init__(self):self.__value = []

    def start(self, total_length, taskname):
        self.__value = {'stime': time.time(), 'count':0, 'progress':0, 'length':total_length, 'taskname':taskname}
        print("\t", taskname)

    def count_by_number(self):
        self.__value['count'] += 1
        new_progress = int(self.__value['count'] * 100 / self.__value['length'])
        if new_progress > self.__value['progress']:
            self.__value['progress'] = new_progress
            time_elapse = time.time() - self.__value["stime"]
            time_left = (100 - new_progress)*time_elapse/new_progress
            print("\t",self.__value["taskname"], "进度%d%%"%self.__value['progress'], "任务耗时%d秒"%(time_elapse), "预估剩余%d小时%d分钟%d秒"%(int(time_left/3600), int(time_left%3600/60), int(time_left%60)))

    def count(self, new_progress_base_on_100):
        self.__value['count'] += 1
        if new_progress_base_on_100 > self.__value['progress']:
            self.__value['progress'] = new_progress_base_on_100
            time_elapse = time.time() - self.__value["stime"]
            time_left = (100 - new_progress_base_on_100)*time_elapse/new_progress_base_on_100
            print("\t",self.__value["taskname"], "进度%d%%"%self.__value['progress'], "任务耗时%d秒"%(time_elapse), "预估剩余%d小时%d分钟%d秒"%(int(time_left/3600), int(time_left%3600/60), int(time_left%60)))

    def finish(self):
        print("\t", self.__value["taskname"] , "已结束")
        print("".join(["-"] * 40))
