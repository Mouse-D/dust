'''
input
    文件名，表格名
output
    列表
    调用方式为：列表[行][列]
'''
def go(path,sheet):
    import xlrd
    #读取excel文件
    res=[]
    read_file = xlrd.open_workbook(path)# 打开Excel文件
    read_sheet = read_file.sheet_by_name(sheet)#通过excel表格名称(rank)获取工作表
    for a in range(read_sheet.nrows):  #循环读取表格内容（每次读取一行数据）
        # 每行数据赋值给cells,因为表内可能存在多列数据，0代表第一列数据，1代表第二列，以此类推
        res.append(read_sheet.row_values(a))
    return res
