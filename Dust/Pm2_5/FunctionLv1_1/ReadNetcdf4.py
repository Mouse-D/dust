'''
input
    文件名,变量名1,变量名2...（均为字符串）
output
    列表1,列表2...
'''
def go(*args):
    from netCDF4 import Dataset
    fh = Dataset(args[0], mode='r')#打开文件
    res=[]
    for loop in range(1,len(args)):
        tmp=fh.variables[args[loop]][:]
        res.append(tmp)
    fh.close()
    return res
    
