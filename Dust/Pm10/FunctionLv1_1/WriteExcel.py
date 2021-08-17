'''
input
    文件名，表格名，数据列表
        列表中存储了整个表格的数据，[0][0]为第一行第一列，依此类推
'''
def go(path,sheet,res):
    '''
    @param path: 要保存的路径及文件名（需要加上.xlsx)
    @param sheet: 要生成的表格名。
    @param res: 数据列表，列表中存储了整个表格的数据，[0][0]为第一行第一列，依此类推
    '''
    import xlsxwriter as xw
    workbook = xw.Workbook(path)  # 新建一个工作簿
    sheet = workbook.add_worksheet(sheet)  # 在工作簿中新建一个表格
    for hang in range(len(res)):
        for lie in range(len(res[0])):
            sheet.write(hang, lie, res[hang][lie]) # 向表格中写入数据（对应的行和列）
    workbook.close()  # 关闭工作簿