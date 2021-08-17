"""
#0 ×.L2十分钟数据->一小时数据。允许数据不够6个的情况
#1 ×(old).无数个小时数据->参考数据集。注意：考虑初始小时数据的问题。执行流程时再解决。
#1 ×(new).直接用L3月作为初始参考数据集。执行改名、改变量名的操作。
#2 √.不断放入新的一个小时->新的参考数据集。
#3 √.参考数据集拿走->用作对地面数据插值，同时引入等比例计算的处罚机制，代替原IV的功能
#4 ×.某一时刻地面监测数据缺失->用昨天的G R、今天的R，等比例计算出今天的G
#5 ×.对AOT小时数据、日数据、月数据求平均。小时->日，日->月
#6 ×.对AOT小时数据、日数据、月数据画图
#7 √.对地面监测数据的小时数据、日数据、月数据求平均。小时->日，日->月
#8 ×.对地面小时数据、日数据、月数据进行阶梯式存储。
#9 √.对小时数据、天数据、月数据进行全方位画图
#10√.把生成的小时数据、日数据、月数据（包括nc和png）进行剪切
"""


import time
from numpy.ma import masked

from FunctionLv1_1.ReadNetcdf4 import go as readNetcdf4
from FunctionLv1_1.ReadExcel import go as readExcel
from FunctionLv1_1.WriteNetcdf4 import go as writeNetcdf4
import os
import numpy as np
import csv
import math
import copy
from numba import jit
#优化思路：20210710全遍历，文件名满足条件的放入列表中后边统一处理
#1.小时位不为xx。2.文件种类匹配上。3.末三位是.nc
#生成到daily中，为月平均做准备
def aveDaily(AOTpathRe,AOTpathDa):
    AOTRefiles = os.listdir(AOTpathRe)
    AOTRefiles.sort()
    d1, d2 = 97, 81
    # d1, d2 = 801, 1201
    pmlist=[]
    sum = np.zeros((d1, d2))
    cnt = np.zeros((d1, d2))
    for i in range(len(AOTRefiles)):#2021010100xx_pm2.5
        if AOTRefiles[i][8:10]!="xx" and AOTRefiles[i][13:18]=="pm2.5" and AOTRefiles[i][-3:]==".nc":
            [lon, lat, aot] = readNetcdf4(AOTpathRe + '/' + AOTRefiles[i], 'lon', 'lat', 'pm2_5')
            pmlist.append([lon, lat, aot])
            aot[np.isnan(aot)] = 10000
            aot[aot == 0] = 1000000
            aot = np.array(aot)
            sum += aot
            flag = (aot != 10000)
            cnt += flag
    sum[(sum >= 1000000) & (sum % 10000 == 0)] = 0
    sum[(sum >= 10000) & (sum % 10000 == 0)] = np.nan
    for j in range(len(pmlist)):
        sum[sum >= 1000000] -= 1000000
    for j in range(len(pmlist)):
        sum[sum >= 10000] -= 10000
    # print(np.count_nonzero(sum >= 10000))
    cnt[cnt == 0] = 1
    sum = sum / cnt
    print(AOTpathRe[-8:] + '.nc Nan数量：', np.count_nonzero(np.isnan(sum)))
    if len(pmlist)>0:
        writeNetcdf4(AOTpathDa + '/' + AOTpathRe[-8:] + 'xxxx_pm2.5_all.nc', 1, lon=pmlist[0][0],
                 lat=pmlist[0][1], pm2_5=sum)


"""
def aveDaily(AOTpathRe,AOTpathDa):
    AOTRefiles = os.listdir(AOTpathRe)
    AOTRefiles.sort()
    d1, d2 = 97, 81
    # d1, d2 = 801, 1201
    i = 0
    while i < len(AOTRefiles):
        # 大体思路：把第一个依次与后边的比较，如果“ ”名称一样，步长+1，比到不一样，就break
        step = 0
        for j in range(1, 24):#一天24小时，最多迈出23步
            if i + j >= len(AOTRefiles):
                break
            if AOTRefiles[i][0:8] == AOTRefiles[i + j][0:8]:
                step += 1
            else:
                break
        dataOri = []
        sum = np.zeros((d1, d2))
        cnt = np.zeros((d1, d2))
        for j in range(step + 1):
            [lon, lat, aot] = readNetcdf4(AOTpathRe + '/' + AOTRefiles[i + j], 'lon', 'lat', 'pm2_5')
            dataOri.append([lon, lat, aot])
            aot[np.isnan(aot)] = 10000
            aot[aot == 0] = 1000000
            aot = np.array(aot)
            sum += aot
            flag = (aot != 10000)
            cnt += flag
        sum[(sum >= 1000000) & (sum % 10000 == 0)] = 0
        sum[(sum >= 10000) & (sum % 10000 == 0)] = np.nan
        for j in range(step + 1):
            sum[sum >= 1000000] -= 1000000
        for j in range(step + 1):
            sum[sum >= 10000] -= 10000
        # print(np.count_nonzero(sum >= 10000))
        cnt[cnt == 0] = 1
        sum = sum / cnt
        print(AOTRefiles[i][0:8] + '.nc Nan数量：', np.count_nonzero(np.isnan(sum)))
        writeNetcdf4(AOTpathDa + '/' + AOTRefiles[i][0:8] + 'xxxx_pm2.5_all.nc', 1, lon=dataOri[0][0], lat=dataOri[0][1], pm2_5=sum)
        i = i + step + 1
"""

def aveMonthly(AOTpathDa,AOTpathMo):
    AOTDafiles = os.listdir(AOTpathDa)
    AOTDafiles.sort()
    d1, d2 = 97, 81
    # d1, d2 = 801, 1201
    i = 0
    while i < len(AOTDafiles):
        # 大体思路：把第一个依次与后边的比较，如果“ ”名称一样，步长+1，比到不一样，就break
        step = 0
        for j in range(1, 32):  # 一个月最多31天
            if i + j >= len(AOTDafiles):
                break
            if AOTDafiles[i][0:6] == AOTDafiles[i + j][0:6]:
                step += 1
            else:
                break
        dataOri = []
        sum = np.zeros((d1, d2))
        cnt = np.zeros((d1, d2))
        for j in range(step + 1):
            [lon, lat, aot] = readNetcdf4(AOTpathDa + '/' + AOTDafiles[i + j], 'lon', 'lat', 'pm2_5')
            dataOri.append([lon, lat, aot])
            aot[np.isnan(aot)] = 10000
            aot[aot == 0] = 1000000
            aot = np.array(aot)
            sum += aot
            flag = (aot != 10000)
            cnt += flag
        # 弹警告：RuntimeWarning: invalid value encountered in remainder
        # 是因为存在nan
        sum[(sum >= 1000000) & (sum % 10000 == 0)] = 0
        sum[(sum >= 10000) & (sum % 10000 == 0)] = np.nan
        for j in range(step + 1):
            sum[sum >= 1000000] -= 1000000
        for j in range(step + 1):
            sum[sum >= 10000] -= 10000
        # print(np.count_nonzero(sum >= 10000))
        cnt[cnt == 0] = 1
        sum = sum / cnt
        print(AOTDafiles[i][0:6] + '.nc Nan数量：', np.count_nonzero(np.isnan(sum)))
        writeNetcdf4(AOTpathMo + '/' + AOTDafiles[i][0:6] + 'xxxxxx_pm2.5_all.nc', 1, lon=dataOri[0][0], lat=dataOri[0][1], pm2_5=sum)
        i = i + step + 1

