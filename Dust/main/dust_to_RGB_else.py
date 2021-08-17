import os

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

def read(*args):
    '''
    input
        文件名,变量名1,变量名2...（均为字符串）
    output
        列表1,列表2...
    '''
    from netCDF4 import Dataset
    fh = Dataset(args[0], mode='r')#打开文件
    res=[]
    for loop in range(1,len(args)):
        tmp=fh.variables[args[loop]][:]
        res.append(tmp)
    fh.close()
    return res

import time
while 1:
    inpath="/himawari/AHI_out/"
    file_list=os.listdir(inpath)
    for file_name in file_list:
        if file_name[-7:]!="dust.nc":
            continue
        lat,lon,dust=read(inpath+file_name,"lat","lon","dust")
        ###三个段，所以有两个阈值
        sign_small=100
        sign_big=102

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
        os.remove(inpath+file_name)
        save_netCDF4(inpath+file_name, lat=lat, lon=lon, R=dustr, G=dustg, B=dustb)
    time.sleep(600)


