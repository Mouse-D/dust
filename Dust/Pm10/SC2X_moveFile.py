import os
import shutil
from datetime import datetime, timedelta, date


def last_day_of_month(any_day):
    """
    获取获得一个月中的最后一天
    :param any_day: 任意日期
    :return: string
    """
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


def show_files(path, destpath):
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path, destpath)
        else:
            # try:
            destfile = os.path.join(destpath, file[0:8])
            movetofile = os.path.join(destpath, file[0:8])  # /20210629/
            if file[6:8] == "xx":
                PK_time = file[0:6]
                # a=datetime.date(PK_time[0:4], PK_time[4:6], 1)
                res = last_day_of_month(date(int(PK_time[0:4]), int(PK_time[4:6]), 1))
                PK_time = res.strftime("%Y%m%d")
                destfile = os.path.join(destpath, PK_time)  # /20210630/
                movetofile = destfile  # /20210630/
            movetofile = os.path.join(movetofile, file)
            if os.path.isdir(destfile):
                if os.access(movetofile, os.F_OK) == True:
                    os.remove(movetofile)
                shutil.move(cur_path, destfile)
            # except:
            #     pass


def run(cur_path1, cur_path2, destpath):
    # cur_path="G:/00 SC/pm10/ground2d/output"
    # cur_path="/himawari/spq/output/pm10/ground2d/output"
    # destpath="G:/00 SC/out"
    # destpath="/himawari/out"
    show_files(cur_path1, destpath)

    # cur_path="/himawari/spq/output/DrawingOutput"
    # cur_path="G:/00 SC/DrawingOutput/pm10"
    show_files(cur_path2, destpath)



def copy_files(path,destpath):

    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path,destpath)
        else:
            # try:
            destfile = os.path.join(destpath, file[0:8])
            movetofile = os.path.join(destpath, file[0:8])  # /20210629/
            if file[6:8]=="xx":#不是日就是月
                print(file)
                PK_time = file[0:6]
                # a=datetime.date(PK_time[0:4], PK_time[4:6], 1)
                res = last_day_of_month(date(int(PK_time[0:4]), int(PK_time[4:6]), 1))
                PK_time = res.strftime("%Y%m%d")
                destfile = os.path.join(destpath, PK_time)
                movetofile = destfile  # /20210630/
                print("movetofile:",movetofile)
            movetofile = os.path.join(movetofile, file)
            if os.path.isdir(destfile):
                if os.access(movetofile, os.F_OK) == True:
                    os.remove(movetofile)
                shutil.copy(cur_path, destfile)
            # except:
            #     pass

def run_copy(cur_path1,cur_path2,destpath):
    # cur_path="G:/00 SC/pm10/ground2d/output"
    # cur_path="/himawari/spq/output/ground2d/output"
    # destpath="G:/00 SC/out"
    # destpath="/himawari/out"
    copy_files(cur_path1,destpath)


    # cur_path="/himawari/spq/output/DrawingOutput/pm2.5"
    # cur_path="G:/00 SC/DrawingOutput/pm10"
    copy_files(cur_path2,destpath)