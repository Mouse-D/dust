def main():
    import os
    import datetime
    date = datetime.datetime.now()
    date=date+datetime.timedelta(days = 1)
    #获取当前时间
    mk_name = datetime.datetime.strftime(date,'%Y%m%d')
    path="/himawari/out/"+str(mk_name)
    os.system("mkdir "+path)
from apscheduler.schedulers.blocking import BlockingScheduler as b_time
aps=b_time()
aps.add_job(main,'cron',hour=6)
aps.start()