#coding=UTF-8

'''
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
'''
import os
import sys
import apscheduler as apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler as b_time
from datetime import datetime, timedelta
from pathlib import Path
import SC2_dayRename
# import SC1_10minsTo1hr
# import SC2I_referenceData
# import SC2I_monthlyStartRef
import SC2II_AOThrDataRein
import SC2III_groundMonitorNingxia
# import SC2IV_groundMonitorNingxiaRatio
# import SC2V_Average
# import SC2VI_Drawing
import SC2VII_Average
import SC2VIII_DrawingStep
# import SC2VIII_saveGrdStep
import SC2X_moveFile
import SC3_delete
import time
sys.path.append('..')
sys.path.append("/himawari/spq/code/FunctionLv1_1")
sys.path.append(os.getcwd())
sys.path.insert(1,"./FunctionLv1_1")

def Drawingpm2_5(grdpathHr, savepathHr):
    destpath = "/himawari/out"
    step = [0, 35, 75, 115, 150, 250]#PM2.5的几个画图的阈值或分界值
    # step=[0,50,150,250,350,420]#PM10的几个画图的阈值或分界值
    lonsName = 'lon'
    latsName = 'lat'
    dataName = 'pm2_5'
    pow = 0
    FigSize = (15, 15.85)
    glFlag = 0
    lonMin, lonMax, latMin, latMax = 104, 108, 35, 39.8#宁夏范围
    # lonMin,lonMax,latMin,latMax=70,140,15,55#中国范围
    cbarticks = [0, 50, 100, 150]
    dpi = 600
    shps = ['no', 'yes']
    grdHrfiles = os.listdir(grdpathHr)
    grdHrfiles.sort(reverse=True)
    #待画图的文件倒序排列，对最新的72个进行遍历(小时:72小时；天和月:对天和月会在下边进行进一步剪枝)
    if len(grdHrfiles)>72:
        index=72
    else:
        index=len(grdHrfiles)
    for i in range(index):  # len(grdHrfiles)
        #目标文件名，也就是将来复制过去的路径+文件名，判断是否存在，
        #若存在 && 是小时数据——不画了，跳过（对重复小时图进行剪枝）
        #若out中的日期文件夹不存在——跳过（对时间久远的文件进行剪枝，包括小时、日、月——对约六天之外的小时、日、月一律不再更新）
        destfile = destpath + '/' + grdHrfiles[i][0:8] + "/" + grdHrfiles[i][0:18] + "_no_600_250.png"
        if os.access(destfile, os.F_OK) == True and grdHrfiles[i][8:10]!="xx":
            print("第一处continue:" + destfile)
            continue#如果这个数据已存在并且是小时数据，那么跳过
        destdatepath = destpath + '/' + grdHrfiles[i][0:8]
        if grdHrfiles[i][6:8]=="xx":
            destdatepath = destpath + '/' + grdHrfiles[i][0:6]+"28"
        if Path(destdatepath).exists()==False:
            print("第二处continue:" + destdatepath)
            continue
        #进一步缩小遍历范围？

        for shp in range(len(shps)):
            for j in range(6):  # 哪几个阈值
                if j == 0:
                    savePath = savepathHr + '/' + grdHrfiles[i][0:len(grdHrfiles[i]) - 7] + '_' + shps[
                        shp] + '_'+str(dpi)+'_all.png'
                else:
                    savePath = savepathHr + '/' + grdHrfiles[i][0:len(grdHrfiles[i]) - 7] + '_' + shps[
                        shp] + '_'+str(dpi)+'_'+str(step[j])+'.png'
                # SC2VIII_DrawingStep.DrawingMini(grdpathHr + '/' + grdHrfiles[i], dataName, lonMin, lonMax, latMin, latMax, cbarticks, savePath,step[j])
                SC2VIII_DrawingStep.DrawingPro(grdHrfiles[i], grdpathHr + '/' + grdHrfiles[i], lonsName, latsName,
                                               dataName, lonMin, lonMax, latMin, latMax, cbarticks,
                                               savePath, step[j], FigSize, glFlag, pow, shp, dpi)

                print(grdHrfiles[i][0:len(grdHrfiles[i]) - 7] + '.png 画图完毕')

def aveH2DRun():
    outpath = "/himawari/out"
    grdpathDa = '/himawari/spq/output/ground2d/output/daily'
    now_time=time.strftime("%Y%m%d", time.localtime())
    PK_time = datetime.strptime(now_time, '%Y%m%d')
    PK_time = PK_time - timedelta(days=1)
    PK_time = PK_time.strftime("%Y%m%d")
    grdpathRe1 = os.path.join(outpath, now_time)
    grdpathRe2 = os.path.join(outpath, PK_time)
    SC2VII_Average.aveDaily(grdpathRe1,grdpathDa)
    SC2VII_Average.aveDaily(grdpathRe2,grdpathDa)

def run0to3():
    print("----------run0to3----------")
    #0(不再使用).L2十分钟数据->一小时数据。允许数据不够6个的情况 √
    # SC1_10minsTo1hr.run()

    #1(旧,不再使用).无数个小时数据->参考数据集。注意：考虑初始小时数据的问题 √
    # SC2I_referenceData.run()

    #1(新,不再使用).直接用L3月作为初始参考数据集。执行改名、改变量名的操作。
    # SC2I_monthlyStartRef.run()

    #2.不断放入新的一个小时->新的参考数据集。√
    SC2II_AOThrDataRein.run()

    #3.参考数据集拿走->用作对地面数据插值 √
    SC2III_groundMonitorNingxia.run()

    # # 8(1)(不再使用).对地面小时数据、日数据、月数据进行阶梯式提取（或画图）。50,75,100,150,200 √
    # # grdpathHr = "G:/00 SC/ground2d/output/hrly"
    # grdpathHr = "/himawari/spq/output/ground2d/output/hrly"
    # # savepathHr="G:/00 SC/preDrawing/hrly"
    # savepathHr="/himawari/spq/output/preDrawing"
    # step=[35,75,115,150,250]
    # SC2VIII_saveGrdStep.runHr(grdpathHr,savepathHr,step)

    # 9(1).对小时数据进行全方位画图
    print("第IX步处理：")
    # grdpathHr = "G:/00 SC/ground2d/output/hrly"
    grdpathHr = "/himawari/spq/output/ground2d/output/hrly"
    # savepathHr = "G:/00 SC/DrawingOutput/grd/hrly"
    savepathHr = "/himawari/spq/output/DrawingOutput/pm2.5"
    Drawingpm2_5(grdpathHr, savepathHr)

    # 10(1).复制小时数据
    print("MOVING......")
    cur_path1 = "/himawari/spq/output/ground2d/output/hrly"
    cur_path2 = "/himawari/spq/output/DrawingOutput/pm2.5"
    destpath = "/himawari/out"
    SC2X_moveFile.run_copy(cur_path1, cur_path2, destpath)


    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# def HourtoDay():
    print("----------HourtoDay----------")
    #0.对日期数据重命名
    SC2_dayRename.run()
    # # 5(1)(不需要用).对AOT小时数据、日数据、月数据求平均。小时->日，日->月 √
    # # AOTpathRe = "G:/00 SC/AOTreference"
    # # AOTpathDa = 'G:/00 SC/AOTowndaily'
    # AOTpathRe = "/himawari/spq/output/AOTreference"
    # AOTpathDa = '/himawari/spq/output/AOTowndaily'
    # print("第V步处理：")
    # SC2V_Average.aveDaily(AOTpathRe,AOTpathDa)
    # 7(1).对地面PM2.5/PM10监测数据的小时数据、日数据、月数据求平均。小时->日，日->月 √
    print("第VII步处理：")
    # grdpathRe = "G:/00 SC/ground2d/output/hrly"
    # grdpathDa = 'G:/00 SC/ground2d/output/daily'
    aveH2DRun()

    # # 8(2)(不再使用).对地面小时数据、日数据、月数据进行阶梯式提取（或画图）。50,75,100,150,200 √
    # # grdpathDa = 'G:/00 SC/ground2d/output/daily'
    # grdpathDa = '/himawari/spq/output/ground2d/output/daily'
    # # savepathDa="G:/00 SC/preDrawing/daily"
    # savepathDa="/himawari/spq/output/preDrawing"
    # step=[35,75,115,150,250]
    # SC2VIII_saveGrdStep.runDa(grdpathDa,savepathDa,step)

    # 9(2).对每天的数据进行全方位画图
    # grdpathDa = 'G:/00 SC/ground2d/output/daily'
    grdpathDa = '/himawari/spq/output/ground2d/output/daily'
    # savepathDa = "G:/00 SC/DrawingOutput/grd/daily"
    savepathDa = "/himawari/spq/output/DrawingOutput/pm2.5"

    Drawingpm2_5(grdpathDa, savepathDa)

    #10(2).复制天数据
    print("MOVING......")
    cur_path1 = "/himawari/spq/output/ground2d/output/daily"
    cur_path2 = "/himawari/spq/output/DrawingOutput/pm2.5"
    destpath = "/himawari/out"
    SC2X_moveFile.run_copy(cur_path1,cur_path2,destpath)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# def DaytoMonth():
    print("----------DaytoMonth----------")
    # print("第V步处理：")
    # # 5(2)(不需要用).对AOT小时数据、日数据、月数据求平均。小时->日，日->月 √
    # # AOTpathDa = 'G:/00 SC/AOTowndaily'
    # # AOTpathMo = 'G:/00 SC/AOTownmonthly'
    # AOTpathDa = '/himawari/spq/output/AOTowndaily'
    # AOTpathMo = '/himawari/spq/output/AOTownmonthly'
    # SC2V_Average.aveMonthly(AOTpathDa,AOTpathMo)

    print("第VII步处理：")
    # 7(2).对地面PM2.5/PM10监测数据的小时数据、日数据、月数据求平均。小时->日，日->月 √
    # grdpathDa = 'G:/00 SC/ground2d/output/daily'
    # grdpathMo = 'G:/00 SC/ground2d/output/monthly'
    grdpathDa = "/himawari/spq/output/ground2d/output/daily"
    grdpathMo = '/himawari/spq/output/ground2d/output/monthly'
    SC2VII_Average.aveMonthly(grdpathDa,grdpathMo)

    # # 8(3)(不再使用).对地面小时数据、日数据、月数据进行阶梯式提取（或画图）。50,75,100,150,200 √
    # # grdpathMo = 'G:/00 SC/ground2d/output/monthly'
    # grdpathMo = '/himawari/spq/output/ground2d/output/monthly'
    # # savepathMo="G:/00 SC/preDrawing/monthly"
    # savepathMo="/himawari/spq/output/preDrawing"
    # step=[35,75,115,150,250]
    # SC2VIII_saveGrdStep.runMo(grdpathMo,savepathMo,step)


    # 9(3).对每月的数据进行全方位画图
    # grdpathMo = 'G:/00 SC/ground2d/output/monthly'
    grdpathMo = '/himawari/spq/output/ground2d/output/monthly'
    # savepathMo = "G:/00 SC/DrawingOutput/grd/monthly"
    savepathMo = "/himawari/spq/output/DrawingOutput/pm2.5"
    Drawingpm2_5(grdpathMo, savepathMo)

    #10(3).剪切月数据
    print("MOVING......")
    cur_path1 = "/himawari/spq/output/ground2d/output/monthly"
    cur_path2 = "/himawari/spq/output/DrawingOutput/pm2.5"
    destpath = "/himawari/out"
    SC2X_moveFile.run(cur_path1,cur_path2,destpath)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # 附加删除：
    print("----------附加删除----------")
    SC3_delete.deleteRun()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

run0to3()
# HourtoDay()
# DaytoMonth()
aps=b_time()#如果第一次没执行完而到了间隔时间，它会并行运行。
# aps.add_job(run0to3,"interval",max_instances=100, hours=1)
# aps.add_job(HourtoDay,"interval",max_instances=100, hours=24)
# aps.add_job(DaytoMonth,"interval",max_instances=100, days=31)
aps.add_job(run0to3,"interval",max_instances=100, minutes=10)
# aps.add_job(HourtoDay,"interval",max_instances=100, minutes=5)
# aps.add_job(DaytoMonth,"interval",max_instances=100, minutes=5)
aps.start()
