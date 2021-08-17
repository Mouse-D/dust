'''
input
    文件名,标志位,变量名1：变量值,变量名2：变量值...
    标志位：
        1代表经度一维，纬度一维
        2代表经纬度各二维
'''
def go(*args,**kw):
    from netCDF4 import Dataset
    import numpy as np
    f_w = Dataset(args[0], mode='w')
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
    f_w.close()