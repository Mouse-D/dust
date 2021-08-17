from numpy.ma import masked
from FunctionLv1_1.ReadNetcdf4 import go as readNetcdf4
from FunctionLv1_1.WriteNetcdf4 import go as writeNetcdf4
import os
import numpy as np

def runHr(grdpathHr,savepathHr,step):
    print("第VIII步处理：")
    grdHrfiles = os.listdir(grdpathHr)
    grdHrfiles.sort()
    for i in range(len(grdHrfiles)):
        [lon, lat, aot] = readNetcdf4(grdpathHr + '/' + grdHrfiles[i], 'lon', 'lat', 'pm2_5')
        for j in range(len(step)):
            aot[aot == masked] = np.nan
            aot = np.array(aot)
            aot[aot < step[j]] = np.nan
            print(grdHrfiles[i][0:19] + str(step[j]) + '.nc')
            writeNetcdf4(savepathHr + '/' + grdHrfiles[i][0:18]+'_'+ str(step[j]) + '.nc', 1, lon=lon,
                         lat=lat, pm2_5=aot)

def runDa(grdpathDa,savepathDa,step):
    print("第VIII步处理：")
    grdDafiles = os.listdir(grdpathDa)
    grdDafiles.sort()
    for i in range(len(grdDafiles)):
        [lon, lat, aot] = readNetcdf4(grdpathDa + '/' + grdDafiles[i], 'lon', 'lat', 'pm2_5')
        for j in range(len(step)):
            aot[aot == masked] = np.nan
            aot = np.array(aot)
            aot[aot < step[j]] = np.nan
            print(grdDafiles[i][0:19] + str(step[j]) + '.nc')
            writeNetcdf4(savepathDa + '/' + grdDafiles[i][0:18] + '_' + str(step[j]) + '.nc', 1, lon=lon,
                         lat=lat, pm2_5=aot)

def runMo(grdpathMo,savepathMo,step):
    print("第VIII步处理：")
    grdMofiles = os.listdir(grdpathMo)
    grdMofiles.sort()
    for i in range(len(grdMofiles)):
        [lon, lat, aot] = readNetcdf4(grdpathMo + '/' + grdMofiles[i], 'lon', 'lat', 'pm2_5')
        for j in range(len(step)):
            aot[aot == masked] = np.nan
            aot = np.array(aot)
            aot[aot < step[j]] = np.nan
            print(grdMofiles[i][0:19] + str(step[j]) + '.nc')
            writeNetcdf4(savepathMo + '/' + grdMofiles[i][0:18] + '_'+ str(step[j]) + '.nc', 1, lon=lon,
                         lat=lat, pm2_5=aot)

