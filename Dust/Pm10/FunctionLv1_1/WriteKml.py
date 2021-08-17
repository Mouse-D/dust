'''
生成kml文件
传入一维数据
'''
def go(path,lat,lon,data):
    from pykml.factory import KML_ElementMaker as KML
    #KML类似于HTML就是超文本文件，完全可以自己写入，这里使用官方提供的方法生成对象
    #然后使用lmxl格式化处理然后写入文本文件

    #先创建Folder里面的内容
    kmlfile=KML.Folder()#作为根目录，只能有一个
    for loop in range(len(data)):
            tmpfile=KML.Placemark(#定义地点
                KML.name(str(loop)),#定义名字
                KML.description("dl's description 描述待补充"),#添加描述
                KML.Point(#定义点要素
                    KML.coordinates(str(lon[loop])+","+str(lat[loop])+","+str(data[loop]))#经度，纬度，数据
                )
            )
            kmlfile.append(tmpfile)
    
    #把创建好的Folder根目录添加到文件中，根目录只有一个
    kmlfile=KML.kml(kmlfile)

    #转换成字符串并写入文件
    from lxml import etree#这是获取HTML、XML等标签并处理输出的库

    #etree.tostring(kmlfile, pretty_print就是好看的参数=True).decode('utf-8')这句话的作用是转换成字符串并且把格式变得好看点
    file=open(path,"w")
    file.write(etree.tostring(kmlfile, pretty_print=True).decode('utf-8'))
