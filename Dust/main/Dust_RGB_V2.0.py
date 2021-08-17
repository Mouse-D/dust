# import numpy as np
# from osgeo import gdal
# from osgeo import osr
# from netCDF4 import Dataset
# ftp://www.875773677_qq.com:SP+wari8@ftp.ptree.jaxa.jp/


def nc(*args):
    # 读取.nc文件
    from netCDF4 import Dataset
    with Dataset(args[0], mode='r') as fh:  # 打开文件
        res = []
        for loop in range(1, len(args)):
            tmp = fh.variables[args[loop]][:]
            res.append(tmp)
    return res



def readfile(inpath, lat_min, lat_max, lon_min, lon_max):
    # path为某个文件的路径，非文件夹
    
    # 提取识别并转换文件时间
    import datetime
    day = str(inpath[-37:-29])
    date=datetime.date(int(day[:4]),int(day[4:6]),int(day[6:]))
    time = int(inpath[-28:-24])
    if time < 1600:
        time = time+800
    else:
        time = time-1600
        date = date+datetime.timedelta(days = 1)
    date=int(datetime.datetime.strftime(date,'%Y%m%d'))
    time = str(date*10000+time)



    lat, lon, b1, b2, b3, b11, b13, b14, b15 = nc(
        inpath, "latitude", "longitude", "albedo_01", "albedo_02", "albedo_03", "tbb_11", "tbb_13", "tbb_14", "tbb_15")

    # 首先判断lat，lon开始结尾处的索引值
    lat_start = 0
    lat_end = 0
    lon_start = 0
    lon_end = 0
    sign = 0
    for loop in range(len(lat)):
        if lat[loop] < lat_max and sign == 0:
            lat_start = loop
            sign = 1
        if lat[loop] < lat_min and sign == 1:
            lat_end = loop
            break
    sign = 0
    for loop in range(len(lon)):
        if lon[loop] > lon_min and sign == 0:
            lon_start = loop
            sign = 1
        if lon[loop] > lon_max and sign == 1:
            lon_end = loop
            break
    # 然后依据此索引值把各波段数据切片


    # 返回该文件内需要的所有波段数据和时间
    return lat[lat_start:lat_end], lon[lon_start:lon_end], b1[lat_start:lat_end, lon_start:lon_end], b2[lat_start:lat_end, lon_start:lon_end], b3[lat_start:lat_end, lon_start:lon_end], b11[lat_start:lat_end, lon_start:lon_end], b13[lat_start:lat_end, lon_start:lon_end], b14[lat_start:lat_end, lon_start:lon_end], b15[lat_start:lat_end, lon_start:lon_end], time


def falseRGB(b11, b13, b15):
    # 假彩图
    import numpy as np

    # 红色通道
    r = b15-b13
    min = -4
    max = 2
    r[r < min] = min
    r[r > max] = max
    r = (r-min)/(max-min)*255
    # 绿色通道
    g = b13-b11
    min = 0
    max = 15
    gamma = 2.5
    g[g < min] = min
    g[g > max] = max
    g = np.power((g-min)/(max-min), 1/gamma)*255
    # 蓝色通道
    b = b13.copy()
    min = 261
    max = 289
    b[b < min] = min
    b[b > max] = max
    b = (b-min)/(max-min)*255

    return r.astype(int), g.astype(int), b.astype(int)


def realRGB(b1, b2, b3):
    # 真彩图
    r = b3/1*255
    g = b2/1*255
    b = b1/1*255
    return r.astype(int), g.astype(int), b.astype(int)


def dust(b1, b11, b13, b14, b15):
    import numpy as np

    # 沙尘识别图
    # 假彩图预处理
    r = b15-b13
    min = -4
    max = 2
    r[r < min] = min
    r[r > max] = max
    r = (r-min)/(max-min)*255

    g = b13-b11
    min = 0
    max = 15
    gamma = 2.5
    g[g < min] = min
    g[g > max] = max
    g = np.power((g-min)/(max-min), 1/gamma)*255

    # 沙尘识别
    yun = (b1 > 0.45) | (b15 < 240) | (b14 < 253)
    dustID = (((r > 135) & (r < 257)) & (g < 114)) & (~yun)
    dust = ((b15-b14)+100)*dustID


    ###三个段，所以有两个阈值
    sign_small=99.6
    sign_big=100.3

    dustlv=dust.copy()
    dustlv[dust>=sign_big]=3
    dustlv[(dust>sign_small)&(dust<sign_big)]=2
    dustlv[dust<=sign_small]=1
    dustr=dust.copy()
    dustr[dust>=sign_big]=190
    dustr[(dust>sign_small)&(dust<sign_big)]=232
    dustr[dust<=sign_small]=223
    dustg=dust.copy()
    dustg[dust>=sign_big]=48
    dustg[(dust>sign_small)&(dust<sign_big)]=124
    dustg[dust<=sign_small]=155
    dustb=dust.copy()
    dustb[dust>=sign_big]=48
    dustb[(dust>sign_small)&(dust<sign_big)]=6
    dustb[dust<=sign_small]=15
    dustdata=dust.copy()
    dustdata=((dustdata-90)/(20))
    dustdata[dustdata>1]=1
    dustdata[dustdata<0]=0

    dustlv[dust == 0] = 0
    dustr[dust == 0] = 0
    dustg[dust == 0] = 0
    dustb[dust == 0] = 0
    dustdata[dust == 0] = 0

    return dustr.astype(int),dustg.astype(int),dustb.astype(int),dustdata,dustlv


# def savepng(r,g,b,savepath):
#     from PIL import Image
#     import matplotlib.pyplot as pyplot
#     r=Image.fromarray(r).convert('L')
#     g=Image.fromarray(g).convert('L')
#     b=Image.fromarray(b).convert('L')
#     image = Image.merge("RGB", (r, g, b))
#     pyplot.axis('off')  #去掉坐标轴
#     pyplot.imshow(image)
#     pyplot.savefig(savepath, dpi=600, bbox_inches='tight')



# def savetiff(outpath,lat_max,lon_min,*args):
#     ##输入保存路径和图片数据(tiff格式)
# #   GDT_Byte = 1(C++中对应unsigned char)
# #   GDT_CFloat32 = 10
# #   GDT_CFloat64 = 11
# #   GDT_CInt16 = 8
# #   GDT_CInt32 = 9
# #   GDT_Float32 = 6(C++中对应float)
# #   GDT_Float64 = 7 (C++中对应double)
# #   GDT_Int16 = 3(C++中对应 short 或 short int)
# #   GDT_Int32 = 5(C++中对应int 或 long 或 long int)
# #   GDT_TypeCount = 12
# #   GDT_UInt16 = 2(C++中对应 unsigned short)
# #   GDT_UInt32 = 4(C++中对应unsigned long)
# #   GDT_Unknown = 0未知数据类型
# #   GFT_Integer = 0
# #   GFT_Real = 1
# #   GFT_String = 2
# #   GDT是数栅格数据的数据类型，GFT是矢量数据的数据类型
#     ##outpath,R,G,B
#     from osgeo import gdal
#     from osgeo import osr
#     if len(args)==1:
#         # 输出为tiff
#         driver_ = gdal.GetDriverByName("GTiff")
#         # 参数依次为：    文件名,
#         #               栅格矩阵的列数, 栅格矩阵的行数,
#         #               波段数, 数据类型
#         dataset = driver_.Create(outpath,
#                                 len(args[0][0]), len(args[0]),
#                                 1, gdal.GDT_Float32)
#         ##定义经纬度网格
#         #dataset.SetGeoTransform((lon_min, 0.05, 0.0, lat_max, 0.0, -0.05))
#         dataset.SetGeoTransform((lon_min, 0.02, 0.0, lat_max, 0.0, -0.02))
#         s = osr.SpatialReference()  # 建立编码
#         s.ImportFromEPSG(4326)  # WGS84纬度/经度
#         dataset.SetProjection(s.ExportToWkt())  # 导出坐标到文件
#         dataset.GetRasterBand(1).WriteArray(args[0])  # 写入数据
#         del dataset
#     if len(args)==3:
#         driver_ = gdal.GetDriverByName("GTiff")
#         dataset = driver_.Create(outpath,
#                                 len(args[0][0]), len(args[0]),
#                                 3, gdal.GDT_Float32)
#         dataset.SetGeoTransform((lon_min, 0.02, 0.0, lat_max, 0.0,-0.02))
#         s=osr.SpatialReference()  # 建立编码
#         s.ImportFromEPSG(4326)  # WGS84纬度/经度
#         dataset.SetProjection(s.ExportToWkt())  # 导出坐标到文件
#         dataset.GetRasterBand(1).WriteArray(args[0])  # 写入数据
#         dataset.GetRasterBand(2).WriteArray(args[1])  # 写入数据
#         dataset.GetRasterBand(3).WriteArray(args[2])  # 写入数据
#         del dataset


def save_netCDF4(*args, **kw):
    '''
    input
        文件名,标志位,变量名1：变量值,变量名2：变量值...
        标志位：
            1代表经度一维，纬度一维
            2代表经纬度各二维
    '''
    from netCDF4 import Dataset
    import numpy as np
    f_w = Dataset(args[0], mode='w')
    f_w.createDimension('lon', len(kw["lon"]))
    f_w.createDimension('lat', len(kw["lat"]))
    for key in kw:
        if key == 'lat' or key == 'lon':
            f_w.createVariable(key, np.float32, (key))
        else:
            f_w.createVariable(key, np.float32, ('lat', 'lon'))
    for key in kw:
        f_w.variables[key][:] = kw[key]
    f_w.close()


# def save_netCDF4_str(*args, **kw):
#     '''
#     input
#         文件名,标志位,变量名1：变量值,变量名2：变量值...
#         标志位：
#             1代表经度一维，纬度一维
#             2代表经纬度各二维
#     '''
#     from netCDF4 import Dataset
#     import numpy as np
#     f_w = Dataset(args[0], mode='w')
#     f_w.createDimension('lon', len(kw["lon"]))
#     f_w.createDimension('lat', len(kw["lat"]))
#     for key in kw:
#         if key == 'lat' or key == 'lon':
#             f_w.createVariable(key, np.float32, (key))
#         else:
#             f_w.createVariable(key, np.str, ('lat', 'lon'))
#     for key in kw:
#         f_w.variables[key][:] = kw[key]
#     f_w.close()


# def change(R,G,B):
#     import numpy as np
#     color=[]
#     digit = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","F","F"]
#     for loopone in range(len(R)):
#         print("颜色转换进度:",loopone/len(R)*100,"%")
#         tmp=[]
#         for looptwo in range(len(R[0])):
#             color1=str(digit[R[loopone][looptwo]//16])+str(digit[R[loopone][looptwo]%16])
#             color2=str(digit[G[loopone][looptwo]//16])+str(digit[G[loopone][looptwo]%16])
#             color3=str(digit[B[loopone][looptwo]//16])+str(digit[B[loopone][looptwo]%16])
#             tmp.append("#"+color1+color2+color3)
#         color.append(tmp)
#     return np.array(color)

def main(inpath, outpath, lat_min, lat_max, lon_min, lon_max):
    import numpy as np
    import os
    try:
        # 数据读取
        lat, lon, b1, b2, b3, b11, b13, b14, b15, time = readfile(
            inpath, lat_min, lat_max, lon_min, lon_max)
    except:
        print("文件打不开！！！")
        print(inpath)
        print("。。。。。。。。。。。。。。。。。。。。")
        return -1

    ##真彩图
    realR, realG, realB = realRGB(b1, b2, b3)
    realRGB_outpath = outpath+time[:-4]+"/"+time+"_real"
    if not os.path.isdir(outpath+time[:-4]):
        os.mkdir(outpath+time[:-4])
    save_netCDF4(realRGB_outpath+".nc", lat=lat, lon=lon, R=realR.astype(np.float32), G=realG.astype(np.float32), B=realB.astype(np.float32))
    # realcolor=change(realR, realG, realB)
    # save_netCDF4_str(realRGB_outpath+"_str.nc", lat=lat, lon=lon, data=realcolor)
    # savepng(realR,realG,realB,realRGB_outpath+".png")
    # savetiff(realRGB_outpath+".tiff",max(lat),min(lon),realR,realG,realB)

    ##假彩图
    falseR, falseG, falseB = falseRGB(b11, b13, b15)
    falseRGB_outpath = outpath+time[:-4]+"/"+time+"_false"
    save_netCDF4(falseRGB_outpath+".nc", lat=lat, lon=lon, R=falseR.astype(np.float32), G=falseG.astype(np.float32), B=falseB.astype(np.float32))
    # falsecolor=change(falseR, falseG, falseB)
    # save_netCDF4_str(falseRGB_outpath+"_str.nc", lat=lat, lon=lon, data=falsecolor)
    # savepng(falseR,falseG,falseB,falseRGB_outpath+".png")
    # savetiff(falseRGB_outpath+".tiff",max(lat),min(lon),falseR,falseG,falseB)

    #沙尘识别图
    dustR,dustG,dustB,dustdata,dustlv = dust(b1, b11, b13, b14, b15)
    dustRGB_outpath = outpath+time[:-4]+"/"+time+"_dust"
    save_netCDF4(dustRGB_outpath+".nc", lat=lat, lon=lon,dust=dustdata,level=dustlv)
    # savetiff(dustRGB_outpath+".tiff",max(lat),min(lon),dustR,dustG,dustB)
    # savetiff(dustRGB_outpath+"2.tiff",max(lat),min(lon),dustdata)
    # savetiff(dustRGB_outpath+"3.tiff",max(lat),min(lon),dustlv)
    return 1



def main_T():
    import os
    import datetime
    print("运行开始：",datetime.datetime.now())
    inpath = "/himawari/AHI/"
    outpath="/himawari/out/"
    for top_path,dir_names_list,file_names_list in os.walk(inpath):
        for file_name in file_names_list:
            # ##定位到.nc文件
            file_path=top_path+"/"+file_name

            # 提取识别并转换文件时间
            day = str(inpath[-37:-29])
            date=datetime.date(int(day[:4]),int(day[4:6]),int(day[6:]))
            time = int(inpath[-28:-24])
            if time < 1600:
                time = time+800
            else:
                time = time-1600
                date = date+datetime.timedelta(days = 1)
            date=int(datetime.datetime.strftime(date,'%Y%m%d'))
            time = str(date*10000+time)
            #判断文件是否被处理过
            if os.path.exists('/himawari/out/'+time[:-4]+"/"+time+"_real.nc"):
                # print("重复文件")
                continue

            # ##输出文件目录，是个文件夹
            ##需要的经纬度
            lat_min = 15
            lat_max = 55
            lon_min = 70
            lon_max = 140
            a=main(file_path, outpath, lat_min, lat_max, lon_min, lon_max)
            if a==-1:
                continue
            print("文件处理完成：",file_path)
            # os.remove(file_path)
    print("运行结束：",datetime.datetime.now())  
    print("-----------------------------------------------")

# #测试单个文件
# inpath="D:/progromdata/my_data/tianqi_in/NC_H08_20210721_0310_R21_FLDK.02401_02401.nc"
# outpath="D:/progromdata/my_data/tianqi_out/"
# lat_min = 15
# lat_max = 55
# lon_min = 70
# lon_max = 140
# main(inpath, outpath, lat_min, lat_max, lon_min, lon_max)



# #定时运行,当前程序如果在规定时间内没有运行完毕，则不进行下一次执行，等待当前执行完毕才执行下次
# from apscheduler.schedulers.blocking import BlockingScheduler as b_time
# aps=b_time()
# aps.add_job(main_T,"interval",seconds=600)
# aps.start()

import time
while 1:
    try:
        main_T()
    except:
        print("出现了其他的严重错误！！！！！！！！")
    time.sleep(600)



