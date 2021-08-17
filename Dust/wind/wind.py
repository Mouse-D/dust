def download(i,index,outpath):
    ##下载目录,获取预测数据时间
    import datetime
    import os
    from urllib.request import urlopen
    base_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/'
    date = datetime.datetime.now()
    for loop in range(8):
        #获取当前时间
        date_yun = datetime.datetime.strftime(date,'%Y%m%d')
        ##预测时间格式转换
        t=i+8+index
        while t>=24:
            t=t-24
            date2=date+datetime.timedelta(days = 1)
        ##本地时间
        date_local=datetime.datetime.strftime(date2,'%Y%m%d')
        ##下载链接
        down_url = base_url+'gfs.'+date_yun+"/"+str(i).zfill(2)+"/atmos/gfs.t"+str(i).zfill(2)+"z.pgrb2full.0p50.f"+str(index).zfill(3)
        

        ##判断本地文件是否存在
        if os.path.exists("/himawari/out/"+date_local+"/"+date_local+str(t).zfill(2)+"xx_wind.nc"):
            print("本地数据已存在")
            return -1


        ##判断网上文件是否存在
        try:
            with urlopen(down_url) as resp:
                code = resp.getcode()
                if code!=200:
                    print("网上暂无数据:",down_url)
                    return -1
        except:
            print("网上暂无数据:",down_url)
            return -1

    for loop in range(8):
        #获取当前时间
        date_yun = datetime.datetime.strftime(date,'%Y%m%d')
        ##预测时间格式转换
        t=i+8+index
        while t>=24:
            t=t-24
            date2=date+datetime.timedelta(days = 1)
        ##本地时间
        date_local=datetime.datetime.strftime(date2,'%Y%m%d')
        ##下载链接
        down_url = base_url+'gfs.'+date_yun+"/"+str(i).zfill(2)+"/atmos/gfs.t"+str(i).zfill(2)+"z.pgrb2full.0p50.f"+str(index).zfill(3)
        ##开始下载
        print("开始下载:","wget -O "+outpath+date_local+str(t).zfill(2)+" "+ down_url)
        os.system("wget -O "+outpath+date_local+str(t).zfill(2)+" "+ down_url)

        index = index + 3
    return 0



def grib(path):
    ##返回lat、lon、U、V


    # #输出所有数据条目
    # for grb in grbs:
    #     print (grb)
    # ##获取数据值
    # data=grbs[1070].values
    # print(data)
    ###获取经纬度
    # lat,lon=grbs[1070].latlons()
    import pygrib
    with pygrib.open(path) as grbs:
        ##划定范围获取数据
        data1=grbs[21].data(lat1=15,lat2=55,lon1=70,lon2=140)
        ##划定范围获取数据
        data2=grbs[22].data(lat1=15,lat2=55,lon1=70,lon2=140)


    return data1[1],data1[2],data1[0],data2[0]


def save_netCDF4(*args,**kw):
    '''
    input
        文件名,标志位,变量名1：变量值,变量名2：变量值...
        标志位：
            1代表经度一维，纬度一维
            2代表经纬度各二维
    '''
    from netCDF4 import Dataset
    import numpy as np
    with Dataset(args[0], mode='w') as f_w:
        if args[1]==1:
            f_w.createDimension('lon', len(kw["lon"]))
            f_w.createDimension('lat', len(kw["lat"]))
            for key in kw:
                if key == 'lat' or key =='lon':
                    f_w.createVariable(key, np.float32, (key))
                else:
                    f_w.createVariable(key, np.float32, ('lat', 'lon'))
        else:
            f_w.createDimension('one', len(kw["lon"]))
            f_w.createDimension('two', len(kw["lon"][0]))
            for key in kw:
                f_w.createVariable(key, np.float32, ('one', 'two'))
        for key in kw:
            f_w.variables[key][:] = kw[key]

def main():
    import os 
    inpath="/himawari/wind/"
    outpath="/himawari/out/"

    import datetime
    print(datetime.datetime.now())

    ##下载文件
    # sign=download(6,12,inpath)
    sign=0  
    sign=download(0,18,inpath)
    if sign==-1:
        return -1
    ##处理数据
    file_list=os.listdir(inpath)
    print("下载完成，开始处理本地文件：",file_list)

    

    for file_name in file_list:

        print("正在处理：",inpath+file_name)
        try:

            lat,lon,u,v=grib(inpath+file_name)
        except:
            print("文件读取错误!!!",inpath+file_name)
            continue


        if not (os.path.lexists(outpath+file_name[:-2]+"/")):
            os.mkdir(outpath+file_name[:-2])
        savepath=outpath+file_name[:-2]+"/"+file_name+"xx_wind.nc"
        save_netCDF4(savepath,2,lat=lat,lon=lon,u=u,v=v)


        os.remove(inpath+file_name)



import time
while 1:
    main()
    time.sleep(10000)

# #定时运行整个文件夹
# from apscheduler.schedulers.blocking import BlockingScheduler as b_time
# aps=b_time()
# ###main_T是需运行的函数，seconds是时间，中间的interval是间隔模式
# # weeks (int) – 间隔几周 
# # days (int) – 间隔几天 
# # hours (int) – 间隔几小时 
# # minutes (int) – 间隔几分钟 
# # seconds (int) – 间隔多少秒 
# # aps.add_job(main,"interval",hours=3)
# aps.add_job(main,'cron',hour=18)
# ##开始运行，先等待设定的时间再运行代码
# aps.start()