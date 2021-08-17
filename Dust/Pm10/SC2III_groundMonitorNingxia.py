#coding=UTF-8
"""
directions:
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
import numba as nb
from datetime import datetime, timedelta

def Absence(AOTpath,grdoutput,INDEX):
    AOTfiles= os.listdir(AOTpath)
    AOTfiles.sort()
    grdfiles= os.listdir(grdoutput)
    grdfiles.sort()
    print("开始反算：", AOTfiles[INDEX])

    utc_time = AOTfiles[INDEX][0:10]

    utc_time = datetime.strptime(utc_time, '%Y%m%d%H')
    PK_time = utc_time - timedelta(hours=1)
    PK_time = PK_time.strftime("%Y%m%d%H")
    # [lonR, latR, aotR] = readNetcdf4(AOTpath + '/' + AOTfiles[INDEX - 1], 'lon', 'lat', 'AOT')
    [lonR, latR, aotR] = readNetcdf4(AOTpath + '/' + PK_time+".nc", 'lon', 'lat', 'AOT')

    while True:
        try:
            # [lonG, latG, aotG] = readNetcdf4(grdoutput + '/' + PK_time + "xx_pm10_all.nc", 'lon', 'lat', 'pm10')
            [lonG, latG, aotG] = readNetcdf4("/himawari/out/" + PK_time[0:8] + "/"+PK_time+"xx_pm10_all.nc", 'lon', 'lat', 'pm10')
        except:
            if int(PK_time[0:8])<int((datetime.strptime(time.strftime("%Y%m%d", time.localtime()), '%Y%m%d')- timedelta(days=3)).strftime("%Y%m%d")):
                return
            PK_time = datetime.strptime(PK_time, '%Y%m%d%H')
            PK_time = PK_time - timedelta(hours=1)
            PK_time = PK_time.strftime("%Y%m%d%H")
            continue
        break

    [lonRT, latRT, aotRT] = readNetcdf4(AOTpath + '/' + AOTfiles[INDEX], 'lon', 'lat', 'AOT')
    aotR[aotR == masked] = np.nan
    aotG[aotG == masked] = np.nan
    aotRT[aotRT == masked] = np.nan
    aotR = np.array(aotR)
    aotG = np.array(aotG)
    aotRT = np.array(aotRT)

    # print(min(min(row) for row in aotG), max(max(row) for row in aotG))
    # print(min(min(row) for row in aotRT), max(max(row) for row in aotRT))
    # print(min(min(row) for row in aotR), max(max(row) for row in aotR))
    # print(np.count_nonzero(np.isnan(aotG)))
    # print(np.count_nonzero(np.isnan(aotRT)))
    # 如果弹出警告，e.g.,aotRT[81][0],说明某一数据存在nan(masked)，那最终结果就保存成nan

    aotGT = aotG * aotRT / aotR
    # print(type(aotRT), type(aotG),type(aotGT))
    writeNetcdf4(grdoutput+'/'+AOTfiles[INDEX][0:10]+'xx_pm10_all.nc', 1, lon=lonG, lat=latG, pm10=aotGT)  # 蓝皮绿骨：路径是grd路径，文件名是AOT文件名

def run():
    print("第III步处理：")
    #监测站数据路径
    mntDatapath = '/himawari/monitor/pmdata'
    # path = "G:/00 SC/ground/20210101-20210417" #监测站数据目录
    # mntDataFile='G:/00 SC/ground/monitorNingxia.xls';sheet='SHEET0'
    destpath = "/himawari/out"
    # 读取监测站的全部信息，以供地面数据缺失时写入csv
    mntInfmFile = '/himawari/spq/output/ground/monitor_final.xls'
    sheet = 'SHEET0'
    monitor = readExcel(mntInfmFile, sheet)
    mntInfm = np.array(monitor)
    # [lon, lat, aot] = readNetcdf4(AOTpath + '/' + AOTfiles[0], 'longitude', 'latitude', 'AOT_L2_Mean')

    #AOT参考数据集
    # AOTpath = "G:/00 SC/AOTreference" #使用第2步中生成的参考数据集，单位是每个小时
    AOTpath = "/himawari/spq/output/AOTreference" #使用第2步中生成的参考数据集，单位是每个小时
    #最终输出差值完毕的文件夹
    # grdoutput='G:/00 SC/ground2d/output/hrly'
    grdoutput='/himawari/spq/output/pm10/ground2d/output/hrly'
    #预处理过程的站点信息（经纬度、网格位置）
    # preInfmFile="G:/00 SC/ground2d/pre/preInfmSuper.csv"
    preInfmFile="/himawari/spq/output/ground2d/pre/preInfmSuper.csv"


    AOTfiles= os.listdir(AOTpath)
    AOTfiles.sort()
    #大体思路：读取preInfmSuper.csv，按图索骥，根据监测站编号
    #在对应的数据excel表格中拿取数据，用地面/AOT再求平均，即为
    #每个网格点的最终归宿

    #读取预处理过程的站点信息（经纬度、网格位置）
    csv_reader = csv.reader(open(preInfmFile))
    preInfm=[]
    for row in csv_reader:
        r=row
        preInfm.append(eval(r[0]))
    if len(AOTfiles)>72:
        index=len(AOTfiles)-72
    else:
        index=0
    for INDEX in range(index,len(AOTfiles)):#第一个是原始参考数据集，就不要拿了
        # 设定缺失信息文件的文件名
        # 首先读取数据。grdoutput+'/'+AOTfiles[INDEX][0:10]+'xx_pm10_all.nc'
        destfile=destpath+'/'+AOTfiles[INDEX][0:8]+"/"+AOTfiles[INDEX][0:10]+'xx_pm10_no_600_all.png'
        print(destfile)
        if os.access(destfile, os.F_OK) == True:
            print(destfile,"已存在")
            continue
        tmpfilename=mntDatapath+'/'+AOTfiles[INDEX][0:10]+'.csv'
        if os.access(tmpfilename, os.F_OK) != True:
            continue
        mntdatafile=tmpfilename
        MntData = []
        with open(mntdatafile, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)#0编号 1PM2.5 2PM10
            next(f)
            for row in reader:
                if len(MntData)==2181:
                    break
                MntData.append(float(row[2]))
        MntData = np.array(MntData).astype(np.float)


        #读取AOT参考数据集
        [lon, lat, aot] = readNetcdf4(AOTpath + '/' + AOTfiles[INDEX], 'lon', 'lat', 'AOT')
        aot[aot == masked]=np.nan
        aot=np.array(aot)
        print("AOT nan数量：",np.count_nonzero(np.isnan(aot)))
        print('正在处理：', INDEX + 1, '/', len(AOTfiles),AOTfiles[INDEX])
        # 读取监测站的数据
        # 具体如何读取要看数据的构造。待定。
        # 如果某时刻监测站数据缺失，则continue

        # 假设检测站数据已经读入一个名为MntData的变量中
        # MntData = np.random.rand(len(preInfm)) * 50
        d1, d2 = 97, 81
        groundData = np.full((d1, d2),np.nan)
        s=set()
        for j in range(len(lat)):
            # print(j/len(lat)*100,'%')
            for k in range(len(lon)):
                Infm=preInfm[j*len(lon)+k]
                concent=0
                if np.isnan(aot[j][k]):#如果当前AOT为nan，则此处就是nan，无需再议
                    groundData[j][k] = np.nan
                    continue
                cnt = 0
                for l in range(len(Infm)):
                    Num=int(Infm[l][3]-1)#对拿到的每个网格信息进行处理
                    Nums1=Infm[l][4]
                    Nums2=Infm[l][5]

                    #在这里加入判断监测站信息丢失、写入缺失信息
                    if MntData[Num]==-1:#暂时假设没数据的地方是''
                        continue
                    if np.isnan(aot[Nums1][Nums2]):
                        continue
                    cnt+=1
                    concent+=MntData[Num]/aot[Nums1][Nums2]#可能有类型转化问题
                    #监测站从1开始编号，因此需要把编号-1
                if cnt==0:
                    # cnt==0有两种情况：1是关联的所有的地面数据为-1
                    #     #2是关联的所有的AOT为NAN
                    #无论是何种情况，只要满足cnt==0，那就代表只有他自己一个关联，因而也就只能是nan了
                    concent=np.nan
                    cnt=1
                groundData[j][k] = concent / cnt
                groundData[j][k]*=aot[j][k]
        print("GRD nan数量：", np.count_nonzero(np.isnan(groundData)))
        writeNetcdf4(grdoutput+'/'+AOTfiles[INDEX][0:10]+'xx_pm10_all.nc', 1, lon=lon, lat=lat, pm10=groundData)
        #回溯判断一下，如果地面监测数据缺失超过10%，则触发等比例反算
        if np.count_nonzero(np.isnan(groundData))>80:
            Absence(AOTpath, grdoutput, INDEX)




