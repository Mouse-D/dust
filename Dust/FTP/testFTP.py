##FTP学习例子1

from ftplib import FTP            # 导入ftplib模块

host="ftp.ptree.jaxa.jp"
part=21
username="www.875773677_qq.com"
password="SP+wari8"

def ftp_download(host,part,username,password,ftppath,localpath):
    bufsize=1024#缓冲区大小
    ftp=FTP()                         # 获取ftp变量
    # ftp.set_debuglevel(2)             # 打开调试级别2，显示详细信息,这句话去掉也行
    ftp.connect(host,part)          #连接的ftp sever服务器
    ftp.login(username,password)      # 用户登陆
    # ftp.cwd(ftppath)                # 进入目录
    file=open(localpath,"wb")
    ftp.retrbinary("RETR "+ftppath,file.write,bufsize)
    # ftp.retrbinary("RETR "+ftpname,file,bufsize) # 接收服务器上文件并写入本地文件
    # ftp.set_debuglevel(0)             #关闭调试模式
    file.close() ##关闭文件
    ftp.quit()                        #退出ftp
def ftp_ls(host,part,username,password,ftppath):
    ftp=FTP()                         # 获取ftp变量
    # ftp.set_debuglevel(2)             # 打开调试级别2，显示详细信息,这句话去掉也行
    ftp.connect(host,part)          #连接的ftp sever服务器
    ftp.login(username,password)      # 用户登陆
    ftp.cwd(ftppath)                # 进入目录
    print(ftp.dir())#打印文件信息
    # ftp.set_debuglevel(0)             #关闭调试模式
    ftp.quit()                        #退出ftp


ftp_ls(host,part,username,password,ftppath)
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