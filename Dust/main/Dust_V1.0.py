# import numpy as np
# from osgeo import gdal
# from osgeo import osr
# from netCDF4 import Dataset



def nc(*args):
    # 读取.nc文件
    from netCDF4 import Dataset
    fh = Dataset(args[0], mode='r')  # 打开文件
    res = []
    for loop in range(1, len(args)):
        tmp = fh.variables[args[loop]][:]
        res.append(tmp)
    fh.close()
    return res


def readfile(inpath, lat_min, lat_max, lon_min, lon_max):
    # path为某个文件的路径，非文件夹
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

    # 提取识别并转换文件时间
    date = int(inpath[-37:-29])
    time = int(inpath[-28:-24])
    if time <= 1600:
        time = time+800
    else:
        time = time-1600
        date = date+1
    time = str(date*10000+time)
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

    return r, g, b


def realRGB(b1, b2, b3):
    # 真彩图
    r = b3/1*255
    g = b2/1*255
    b = b1/1*255
    return r, g, b


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
    dust[dust == 0] = np.nan

    return dust


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


def main(inpath, outpath, lat_min, lat_max, lon_min, lon_max):
    # 数据读取
    lat, lon, b1, b2, b3, b11, b13, b14, b15, time = readfile(
        inpath, lat_min, lat_max, lon_min, lon_max)

    ##真彩图
    realR, realG, realB = realRGB(b1, b2, b3)
    realRGB_outpath = outpath+time+"real.nc"
    save_netCDF4(realRGB_outpath, lat=lat, lon=lon, R=realR, G=realG, B=realB)

    ##假彩图
    falseR, falseG, falseB = falseRGB(b11, b13, b15)
    falseRGB_outpath = outpath+time+"false.nc"
    save_netCDF4(falseRGB_outpath, lat=lat, lon=lon, R=falseR, G=falseG, B=falseB)

    ##沙尘识别图
    dustdata = dust(b1, b11, b13, b14, b15)
    dust_outpath = outpath+time+"dust.nc"
    save_netCDF4(dust_outpath, lat=lat, lon=lon, dust=dustdata)

def main_T():
    import os
    import datetime
    print("运行中，当前时间：",datetime.datetime.now())
    inpath = "/himawari/AHI"
    outpath="/himawari/AHI_out/"
    yyyymm_list=os.listdir(inpath)
    if len(yyyymm_list)!=0:
        for year_month in yyyymm_list:
            dd_list=os.listdir(inpath+"/"+year_month)
            if len(dd_list)!=0:
                for day in dd_list:
                    name_list=os.listdir(inpath+"/"+year_month+"/"+day)
                    if len(name_list)!=0:
                        for name in name_list:
                            # ##定位到.nc文件
                            file_path=inpath+"/"+year_month+"/"+day+"/"+name
                            # ##输出文件目录，是个文件夹
                            
                            ##需要的经纬度
                            lat_min = 15
                            lat_max = 55
                            lon_min = 70
                            lon_max = 140
                            main(file_path, outpath, lat_min, lat_max, lon_min, lon_max)
                            os.remove(file_path)
    print("运行结束：",datetime.datetime.now())                            

# ##运行整个文件夹一次
# main_T()

# ##运行一个文件一次
# # ##定位到.nc文件
# file_path="D:/in/NC_H08_20210506_1100_R21_FLDK.02401_02401.nc"
# # ##输出文件目录，是个文件夹
# outpath="D:/out/"
# ##需要的经纬度
# lat_min = 15
# lat_max = 55
# lon_min = 70
# lon_max = 140
# main(file_path, outpath, lat_min, lat_max, lon_min, lon_max)

#定时运行整个文件夹
from apscheduler.schedulers.blocking import BlockingScheduler as b_time
aps=b_time()
###main_T是需运行的函数，seconds是时间，中间的interval是间隔模式
# weeks (int) – 间隔几周 
# days (int) – 间隔几天 
# hours (int) – 间隔几小时 
# minutes (int) – 间隔几分钟 
# seconds (int) – 间隔多少秒 
aps.add_job(main_T,"interval",seconds=600)
##开始运行，先等待设定的时间再运行代码
aps.start()
    












# def savetiff(outpath,lat_max,lon_min,*args):
#     ##输入保存路径和图片数据(tiff格式)
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
#                                 1, gdal.GDT_Float64)
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
#                                 3, gdal.GDT_Float64)
#         dataset.SetGeoTransform((lon_min, 0.05, 0.0, lat_max, 0.0,-0.05))
#         s=osr.SpatialReference()  # 建立编码
#         s.ImportFromEPSG(4326)  # WGS84纬度/经度
#         dataset.SetProjection(s.ExportToWkt())  # 导出坐标到文件
#         dataset.GetRasterBand(1).WriteArray(args[0])  # 写入数据
#         dataset.GetRasterBand(2).WriteArray(args[1])  # 写入数据
#         dataset.GetRasterBand(3).WriteArray(args[2])  # 写入数据
#         del dataset
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
# savetiff(realRGB_outpath+".tiff",max(lat),min(lon),realR,realG,realB)
# savepng(realR,realG,realB,"/home/admin/D/real"+time+"realRGB.png")
