#coding=UTF-8
"""
directions:
"G:/00 SC/AOTreference"II中作为输出，III作为输出文件夹，一开始有一个初始参考数据集。

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
from datetime import datetime, timedelta
def run():
    print("第II步处理：")
    #AOT参考数据集
    # AOTpathRe = "G:/00 SC/AOTreference"
    AOTpathRe = "/himawari/spq/output/AOTreference"
    #L2小时数据
    # AOTpathHr = "G:/00 SC/AOTownhrly"
    AOTpathHr = "/himawari/spq/output/AOTownhrly"


    AOTRefiles= os.listdir(AOTpathRe)
    AOTRefiles.sort()
    AOTHrfiles= os.listdir(AOTpathHr)
    AOTHrfiles.sort()

    d1,d2=97,81# 宁夏范围
    lon1,lon2,lat1,lat2=480,561,404,501
    # d1, d2 = 801, 1201# 全国范围
    # lon1, lon2, lat1, lat2 = 0, 1201, 100, 901
    for i in range(len(AOTHrfiles)):
        print('正在处理：',i+1,'/',len(AOTHrfiles),AOTHrfiles[i][0:8]+'.nc')
        AOTRefiles = os.listdir(AOTpathRe)
        AOTRefiles.sort()
        #R代表参考数据集reference，H代表小时数据hour
        #读取（上一个）参考数据集
        [lonR, latR, aotR] = readNetcdf4(AOTpathRe + '/' + AOTRefiles[i], 'lon', 'lat', 'AOT')
        #读取小时数据
        [lontmp, lattmp, aottmp] = readNetcdf4(AOTpathHr + '/' + AOTHrfiles[i], 'lon', 'lat', 'AOT')
        #小时数据存在masked，设置成nan
        aottmp[aottmp == masked] = np.nan
        #赋值成nan再转换成数组类型，那么就不会让masked的地方变成异常值（如负几万，非常大的正数）
        lontmp, lattmp, aottmp=np.array(lontmp), np.array(lattmp), np.array(aottmp)
        #前面已经切片，这里不需要再切
        # lonH, latH, aotH=lontmp[lon1:lon2], lattmp[lat1:lat2], aottmp[lat1:lat2,lon1:lon2]
        #让命名规范一下
        lonH, latH, aotH=lontmp, lattmp, aottmp
        #AOT数据存在masked，设置成nan
        aotR[aotR == masked]=np.nan
        aotR=np.array(aotR)
        lonR, latR, aotR=np.array(lonR), np.array(latR), np.array(aotR)
        print("小时数据nan数量:",np.count_nonzero(np.isnan(aotH)))

        #数据不全导致最后仍存在Nan，要识别出来。
        aotH[aotH==-32768]=10000
        aotH[np.isnan(aotH)]=10000
        aotH[aotH == 0] = 1000000
        aotR[aotR==-32768]=10000
        aotR[np.isnan(aotR)]=10000
        aotR[aotR == 0] = 1000000
        # print(np.count_nonzero(~np.isnan(aotR)))
        print(aotH.shape,aotR.shape)
        newRefer=aotH+aotR#
        """
        NB:
        各种形式的nan已经变为10000了，不会因为nan+任何数=nan
        这一运算规则而导致数据越来越少。另外在该代码中，把0赋
        值为1000000似乎显得没有必要，然而在之前的代码中，使用
        初始全为0的数组进行0到6次不等的加法，具体而言，等于10000
        的值无法判定是否有0参与。（关于1000000：如果不建立初始
        数组而用第一个作为初始数组，那么其nan的网格将永无翻身之
        日，故必须建立初始0数组，用1000000来区分初始0和数据0，
        这在那个条件下是十分必要的。而现在，是两个数组相加，“两
        个”是确定了的，因此删去有关1000000的内容也可以。）后边
        该部分多次使用就不再详细说明。
        """
        flagH = (aotH != 10000)
        flagR = (aotR != 10000)
        cnt = np.zeros((d1, d2))
        cnt+=flagH;cnt+=flagR
        cnt[cnt==0]=1
        #这两行不可随意调换顺序
        newRefer[(newRefer >= 1000000) & (newRefer % 10000 == 0)] = 0#解决0+nan的问题
        newRefer[(newRefer >= 10000) & (newRefer % 10000 == 0)] = np.nan#解决NAN+NAN的问题
        for k in range(2):
            # 这两行不可随意调换顺序
            newRefer[newRefer >= 1000000] -= 1000000
            newRefer[newRefer>=10000]-=10000
        newRefer/=cnt
        #把一个小时文件裂变成24文件，首先加上30天，然后加上八小时由世界时转换为北京时，
        #生成24个核心内容一样的文件，只是命名不同。
        for l in range(24):
            utc_time = AOTHrfiles[i][0:8] + str(l).zfill(2)
            utc_time = datetime.strptime(utc_time, '%Y%m%d%H')
            PK_time = utc_time + timedelta(days=30) + timedelta(hours=8)
            PK_time = PK_time.strftime("%Y%m%d%H")

            writeNetcdf4(AOTpathRe + '/' + PK_time[0:8]+ PK_time[8:10] + '.nc', 1, lon=lonR, lat=latR,
                         AOT=newRefer)
