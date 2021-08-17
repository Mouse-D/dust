##从FTP服务器定时下载文件的完成版


host="ftp.ptree.jaxa.jp"
part=21
username="www.875773677_qq.com"
password="SP+wari8"

##本地文件存储路径
local_file_path="D://progrom//FTP//"
##ftp文件路径（年月日文件夹）
ftp_file_path="/jma/netcdf/"

def local_date(local_file_path):
    import os 
    ##获取本地的最新的那个文件的日期
    local_file_list=os.listdir(local_file_path)##获取本地文件列表
    local_file_list.sort()##对文件名进行排序
    return local_file_list[-1]##本地最新的文件的时间

def ftp_date(ftp_file_path):
    ##获取FTP服务器上最新的文件的日期
    #传入路径应下应是以年+月命名的文件夹
    #仅适用于卫星数据，宋品清的AOT数据不适用，仍需改进
    from ftplib import FTP
    ftp=FTP()                         # 获取ftp变量
    ftp.connect(host,part)          #连接的ftp sever服务器
    ftp.login(username,password)      # 用户登陆
    ftp.cwd(ftp_file_path)#进入ftp服务器中的路径

    a=-1
    b=-1
    ##查找该路径下最新的年、月
    ftp_file_year_mouth=ftp.nlst()
    ftp_file_year_mouth.sort()
    ##进入最新的年、月文件夹
    ftp.cwd(ftp_file_year_mouth[a])
    #查找最新的日
    ftp_file_day=ftp.nlst()
    ftp_file_day.sort()
    #进入最新的日文件夹
    ftp.cwd(ftp_file_day[b])
    #获取文件名
    ftp_file_name=ftp.nlst()
    ##如果当前文件夹内是空的，需要进入上一个日文件夹，如果日文件夹没了则需要进入上一个月文件夹
    while len(ftp_file_name)==0:
        try:
            b-=1
            #进入上一个的日文件夹
            ftp.cwd(ftp_file_path+ftp_file_year_mouth[a]+"/"+ftp_file_day[b])
            #获取文件名
            ftp_file_name=ftp.nlst()
        except:
            a-=1
            b=-1
            #进入上一个年、月文件夹
            ftp.cwd(ftp_file_path+ftp_file_year_mouth[a])
            #查找最新的日
            ftp_file_day=ftp.nlst()
            ftp_file_day.sort()
            #进入最新的日文件夹
            ftp.cwd(ftp_file_day[b])
            ftp_file_name=ftp.nlst()
    
    #筛选出R21和02401标记的文件
    tmp=[] 
    for loop in ftp_file_name:
        if loop[21:]=="R21_FLDK.02401_02401.nc":
            tmp.append(loop)
    ftp_file_name=tmp
    
    ftp_file_name.sort()##对获取到的文件名进行排序
    ftp.quit()                        #退出ftp
    return ftp_file_name[-1]
    

def check(local_file_name,ftp_file_name):
    ##输入本地文件和ftp文件，返回需要下载的文件列表
    ##后续根据此列表下载文件即可
    import datetime
    file_list=[]
    while local_file_name<ftp_file_name:
        time=datetime.datetime(int(local_file_name[7:11]),int(local_file_name[11:13]),int(local_file_name[13:15]),int(local_file_name[16:18]),int(local_file_name[18:20]))
        time+=datetime.timedelta(minutes = 10)
        time=time.__format__('%Y%m%d%H%M')
        local_file_name=local_file_name[:7]+time[:8]+"_"+time[8:]+local_file_name[20:]
        file_list.append(local_file_name)
    return file_list


def ftp_download(ftppath,localpath):
    from ftplib import FTP
    bufsize=1024#缓冲区大小
    ftp=FTP()                         # 获取ftp变量
    ftp.connect(host,part)          #连接的ftp sever服务器
    ftp.login(username,password)      # 用户登陆
    file=open(localpath,"wb")
    ftp.retrbinary("RETR "+ftppath,file.write,bufsize)
    file.close() ##关闭文件
    ftp.quit()                        #退出ftp




def once():
    #####运行一次检查+下载

    ##获取服务器上最新的文件
    ftp_file_name=ftp_date(ftp_file_path)
    ##获取本地的最新的文件
    local_file_name=local_date(local_file_path)
    ##检查本地与服务器最新的文件是否存在差别，如有差别，返回需要下载的文件名列表
    filelist=check(local_file_name,ftp_file_name)
    #下载文件
    if len(filelist)!=0:
        for file in filelist:
            down_path=ftp_file_path+file[7:13]+"/"+file[13:15]+"/"+file##下载的路径
            save_path=local_file_path+file#保存的路径
            ftp_download(down_path,save_path)


def more(sleep_secend):
    #定时执行，传入间隔时间/秒
    from datetime import datetime
    import time
    while True:
        once()
        time.sleep(sleep_secend)

def my_download_new(*args):
    print(len(args))
    if len(args)==1:
        ##获取服务器上最新的文件
        file_name=ftp_date(ftp_file_path)
        down_path=ftp_file_path+file_name[7:13]+"/"+file_name[13:15]+"/"+file_name##下载的路径
        save_path=local_file_path+file_name#保存的路径
        ftp_download(down_path,save_path)
    elif len(args)==4:
        file_name="NC_H08_"+str(args[0]).zfill(4)+str(args[1]).zfill(2)+str(args[2]).zfill(2)+"_"+str(args[3]).zfill(2)+"00_R21_FLDK.02401_02401.nc"
        down_path=ftp_file_path+file_name[7:13]+"/"+file_name[13:15]+"/"+file_name##下载的路径
        print(down_path)
# my_download_new("new")
my_download_new(2021,7,21,12)