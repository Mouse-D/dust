'''
创建shp文件
传入一维的经纬度和数据列表
'''

def go(path,lat,lon,data):
    import shapefile
    from osgeo import osr
    shp = shapefile.Writer(path)

    shp.field('value', 'F', '40')

    # 循环创建点，
    for loop in range(len(lat)):
        # 第一列，第二列作为经纬度（x，y）创建点
        shp.point(float(lon[loop]), float(lat[loop]))
        '''
        第三列作为value值输出到属性表中，在record中增加参数只在属性表的一条数据中的记录
        依次与shp.field创建的新列名称对应
        '''
        shp.record(data[loop])  # 1是随便写的
    shp.close()

    # 创建投影
    spatial_ref = osr.SpatialReference()
    # WGS84
    spatial_ref.ImportFromEPSG(4326)

    file = open(path[0:-4]+'.prj', 'w')
    file.write(spatial_ref.ExportToWkt())
    file.close()