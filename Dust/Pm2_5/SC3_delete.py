import sys
sys.path.append("/himawari/spq/code/FunctionLv1_1")
import os
from datetime import datetime, timedelta
import time
from pathlib import Path
def deleteRun():
    path1=["/himawari/spq/output/ground2d/output/hrly",
           "/himawari/spq/output/ground2d/output/daily",
           "/himawari/spq/output/AOTownhrly",
           "/himawari/spq/output/DrawingOutput/pm2.5",]

    now_time=time.strftime("%Y%m%d", time.localtime())
    PK_time = datetime.strptime(now_time, '%Y%m%d')
    PK_time = PK_time - timedelta(days=60)
    PK_time = PK_time.strftime("%Y%m%d")

    for i in range(len(path1)):
        files1 = os.listdir(path1[i])
        files1.sort()
        for j in range(len(files1)):
            files1DelName = files1[j][0:8]
            if files1[j][6:8]=="xx":
                files1DelName=files1[j][0:6]+"28"
            if int(files1DelName)<int(PK_time) and Path(os.path.join(path1[i], files1[j])).exists()==True:
                os.remove(os.path.join(path1[i], files1[j]))

    path2=["/himawari/spq/output/AOTreference"]

    for i in range(len(path2)):
        files2 = os.listdir(path2[i])
        files2.sort()
        while True:
            if len(files2)>1440:
                files2 = os.listdir(path2[i])
                files2.sort()
                os.remove(os.path.join(path2[i], files2[1]))
            else:
                break