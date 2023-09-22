# 对所有卫星数据获取其边界bbox，并按照经度和纬度排序
import os,gdal
def getbox(file):
    ds = gdal.Open(file)
    rows, cols=ds.RasterYSize, ds.RasterXSize
    geot=ds.GetGeoTransform()
    minx=geot[0]
    maxy=geot[3]
    maxx=minx+cols*geot[1]
    miny =maxy+geot[5]*rows
    return minx,maxy,maxx,miny

path=os.getcwd()

import pandas as pd
def bbox_pd_sort(path):
    all_files = [f for f in os.listdir(path)]
    #pd.DataFrame是按列存储的，每个字典中的key都是一列的列标题，所以分别存储每一列
    file_list=[]
    minx_list=[]
    maxy_list=[]
    maxx_list=[]
    miny_list=[]
    for i in range(len(all_files)):
        if all_files[i].endswith('.tif'):
            bbox = getbox(os.path.join(path,all_files[i]))
            file_list.append(all_files[i])
            minx_list.append(bbox[0])
            maxy_list.append(bbox[1])
            maxx_list.append(bbox[2])
            miny_list.append(bbox[3])
    bb = {}
    bb["filename"]=file_list
    bb["minx"]=minx_list
    bb["maxy"]=maxy_list
    bb["maxx"]=maxx_list
    bb["miny"]=miny_list
    #存储到pandas的dataframe中，按经度和纬度排序（numpy的array不能存储不同类型，如字符串和数字）
    df=pd.DataFrame(bb)
    yd=df.sort_values(by='maxy',ascending=False)
    yd.to_csv('yd.csv')
    xs=df.sort_values(by='minx', ascending=True)
    xs.to_csv('xs.csv')

    #将所有卫星影像的边框输出到shapefile文件中
    from shapely.geometry import mapping, Polygon
    import fiona
    all_files = [f for f in os.listdir(path)]
    shp_file="bbox.shp"
    # schema是一个字典结构，指定了geometry及其它属性结构
    schema={'geometry': 'Polygon', 'properties': {'labelid': 'int', 'imageid': 'str'} }
    # 使用fiona.open方法打开文件，写入数据
    with fiona.open(shp_file, mode='w', driver='ESRI Shapefile', schema=schema, crs='EPSG:4326', encoding='utf-8') as layer:
        for i in range(len(all_files)):
            minx,maxy,maxx,miny = getbox(os.path.join(path,all_files[i]))
            poly=Polygon([[minx,maxy],[maxx,maxy],[maxx,miny],[minx,miny],[minx,maxy]])
            element = {'geometry':mapping(poly), 'properties': {'labelid': i, 'imageid': all_files[i][8:-13]}}
            layer.write(element)

