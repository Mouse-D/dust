#coding=UTF-8
import time
from FunctionLv1_1.ReadNetcdf4 import go as readNetcdf4
from FunctionLv1_1.WriteNetcdf4 import go as writeNetcdf4
import os
import numpy as np


def run():
    print("第I步处理：")
    # path = "G:/00 SC/AOTdata"  # 文件夹目录
    path = "/himawari/AOT"  # 文件夹目录
    # outputpath = "G:/00 SC/AOTownhrly"  # 文件夹目录
    outputpath = "/himawari/spq/output/AOTownhrly"  # 文件夹目录
    # files[i][7:17]
    files = os.listdir(path)
    files.sort()

    for j in range(len(files)):
        [lon, lat, aot] = readNetcdf4(path + '/' + files[j], 'longitude', 'latitude', 'AOT_L2_Mean')
        # lon1, lon2, lat1, lat2 = 0, 1201, 100, 901
        lon1, lon2, lat1, lat2 = 480, 561, 404, 501
        writeNetcdf4(outputpath + '/' + files[j][4:12] + '.nc', 1, lon=lon[lon1:lon2], lat=lat[lat1:lat2], AOT=aot[lat1:lat2, lon1:lon2])

