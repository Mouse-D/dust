##FTP学习例子2

from ftplib import FTP            # 导入ftplib模块

host="ftp.ptree.jaxa.jp"
part=21
username="www.875773677_qq.com"
password="SP+wari8"

ftppath="/jma/netcdf/202105"#05
ftpname="README_HimawariHSD_en.txt"#NC_H08_20210505_0210_R21_FLDK.06001_06001.nc

localpath="D://test.txt"
localname="test.txt"


def ftp_on(host,part,username,password):
    ###建立ftp服务器连接
    ftp=FTP()                         # 获取ftp变量
    ftp.connect(host,part)          #连接的ftp sever服务器
    ftp.login(username,password)      # 用户登陆
    return ftp
def ftp_off(ftp):
    ##关闭连接
    ftp.close()


def ftp_download(ftp,ftppath,localpath):
    ##从ftp服务器上下载文件到本地
    bufsize=1024#缓冲区大小
    file=open(localpath,"wb")
    ftp.retrbinary("RETR "+ftppath,file.write,bufsize)
    file.close() ##关闭文件

def ftp_ls(ftp,ftppath):
    ##打印传入路径下所有文件信息
    print(ftp.dir(ftppath))                #打印文件信息

ftp=ftp_on(host,part,username,password)
ftp_ls(ftp,ftppath)
ftp_off(ftp)

# ftp.cwd(ftppath)                 # 设置ftp当前操作的路径
# ftp.dir()                         # 显示目录下所有文件信息
# ftp.nlst()                        # 获取目录下的文件，返回一个list
# ftp.mkd(pathname)                 # 新建远程目录
# ftp.pwd()                         # 返回当前所在路径
# ftp.rmd(dirname)                  # 删除远程目录
# ftp.delete(filename)              # 删除远程文件
# ftp.rename(fromname, toname) # 将fromname修改名称为toname。
# ftp.storbinaly("STOR filename.txt",fid,bufsize)  # 上传目标文件
# ftp.retrbinary("RETR filename.txt",fid,bufsize)  # 下载FTP文件