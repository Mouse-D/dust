# #定时运行整个文件夹
# from apscheduler.schedulers.blocking import BlockingScheduler as b_time

# def main_T():
#     print("1")
# def main_Y():
#     print(" 2")
# def main_U():
#     print(" 3")

# aps=b_time()
# ###main_T是需运行的函数，seconds是时间，中间的interval是间隔模式
# # weeks (int) – 间隔几周
# # days (int) – 间隔几天
# # hours (int) – 间隔几小时
# # minutes (int) – 间隔几分钟
# # seconds (int) – 间隔多少秒
# aps.add_job(main_T,"interval",seconds=3)
# aps.add_job(main_Y,"interval",seconds=5)
# aps.add_job(main_U,"interval",seconds=7)
# ##开始运行，先等待设定的时间再运行代码
# aps.start()

# import numpy as np
# a=np.array([[1,2,3,4],[5,6,7,8],[9,10,np.nan,np.nan]])
# a[a>8]=255
# a[(a<=8)&(a>3)]=1
# print(a)


# from urllib.request import urlopen
 
# url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20210528/06/atmos/gfs.t06z.atmanl.nc '
# resp = urlopen(url)
# code = resp.getcode()
# if code!=200:
#     print('the result is :', code)
# resp.close()



# inpath = "D:/progrom/Dust/"
# import os

# for file_path,dir_names_list,file_names_list in os.walk(inpath):
#     for file_name in file_names_list:
#         print(file_path+"/"+file_name)
#         if os.path.exists(file_path+"/"+file_name):
#             print("存在")



# from urllib.request import urlopen
# down_url="http://www.ba1idu.com"
# try:
#     with urlopen(down_url) as resp:
#         code = resp.getcode()
#         if code!=200:
#             print("网上暂无数据:",down_url)
#             print(1)
#         print("you")
# except:
#     print("mei")

# def get_date(num):
#     # 把一年中的第num天转换为月/日
#     mouth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#     mm = -1
#     for loop in range(12):
#         if (num-mouth[loop]) <= 0:
#             mm = loop+1
#             break
#         num = num-mouth[loop]
#     dd = num
#     return str(mm), str(dd)


# print(get_date(275))
# print(get_date(121))
# print(get_date(69))

# def change(R,G,B):
#     color=[]
#     digit = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
#     for loopone in range(len(R)):
#         tmp=[]
#         for looptwo in range(len(R[0])):
#             color1=str(digit[R[loopone][looptwo]//16])+str(digit[R[loopone][looptwo]%16])
#             color2=str(digit[G[loopone][looptwo]//16])+str(digit[G[loopone][looptwo]%16])
#             color3=str(digit[B[loopone][looptwo]//16])+str(digit[B[loopone][looptwo]%16])
#             tmp.append("#"+color1+color2+color3)
#         color.append(tmp)
#     return color

# import numpy as np
# R=np.array([[123,11,255],[16,145,15]])
# G=np.array([[12,134,255],[32,156,12]])
# B=np.array([[45,61,0],[24,235,255]])
# print(change(R,G,B))


# import os
# inpath = "/himawari/spq/output/DrawingOutput/"
# for top_path,dir_names_list,file_names_list in os.walk(inpath):
#     for file_name in file_names_list:
#         file_path=top_path+"/"+file_name
#         if file_path[-3:]==".nc":
#             print(file_path)
#             os.remove(file_path)

# import os
# path="D:/progrom/"
# if not (os.path.lexists(path)):
#     print(os.path.lexists(path))
# else:
#     print(00000)


# def main_1():
#     while(1):
#         a=1
# def main_2():
#     print("zhengchang")

# #定时运行,当前程序如果在规定时间内没有运行完毕，则不进行下一次执行，等待当前执行完毕才执行下次
# from apscheduler.schedulers.blocking import BlockingScheduler as b_time
# aps=b_time()
# aps.add_job(main_1,"interval",seconds=3)
# aps.add_job(main_2,"interval",seconds=4)
# aps.start()


import datetime
time=datetime.date(2021,4,23)

print(time)
print(datetime.datetime.strftime(time,'%Y%m%d'))
