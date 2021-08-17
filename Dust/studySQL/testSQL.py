##SQL学习例子1
import pymysql

##db是数据库名称
mysql_conn = pymysql.connect(host= '47.94.231.190', port= 3306, user= 'dl', password= 'DLjkl;123',db='DL_TEST_SQL')

# 通过cursor创建游标
mysql_cursor = mysql_conn.cursor()

# 创建sql 语句，并执行
# sql="CREATE DATABASE DL_TEST_SQL;"
# sql = "CREATE TABLE test_dl_sql ( dl_test_one INT(11) , dl_test_two VARCHAR(12) );"
# sql="INSERT INTO test_dl_sql VALUES (123324,'asdfqwertgvc')"
# sql="SELECT * FROM test_dl_sql"
###通过文件存储SQL语句
f=open("SQL\sql","r")
sql=f.read()
f.close()
print("需要执行的SQL语句：",sql)

###数据库执行SQL语句
a=mysql_cursor.execute(sql)
##返回的a是查询语句所查询到的数据的条数


###这句话在修改时必须要有，不然就相当于没执行
# mysql_conn.commit()


##返回的b是查询到的全部的数据，前面的查询只有使用此句才能获得实际的数据
b = mysql_cursor.fetchall()


print("查询到的语句有",a,"条","\n内容是：",b)


##先关游标，再关链接
mysql_cursor.close()
mysql_conn.close()
