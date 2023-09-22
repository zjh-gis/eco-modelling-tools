面向对象无监督kmeans聚类算法
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 17:23:54 2021

@author: zjh
"""
import ogr
import gdal
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

cluster_num=4

def objects_clustering(segments, img,dst_file,gt, proj):
    labels = np.unique(segments)
    X = []
    Y = []
    for l in labels:
        print(l)
        Y.append(l)
        mask = segments == l
        feature = []
        for i in range(3):
            img_b = img[i,:, :]
            feature.append(img_b[mask].mean())
            feature.append(img_b[mask].std())
        X.append(feature)
    
    x = np.array(X)
    
    print('begin classifying...')
    kmeans = KMeans(n_clusters=cluster_num, random_state=0).fit(x)
    
    initial_type=[('x',FloatTensorType([None, x.shape[1]]))]
    onx=convert_sklearn(kmeans, initial_types=initial_type)
    with open('D:/tmp/kmeans_hz_farm.onnx', 'wb') as f:
        f.write(onx.SerializeToString())
        
    import onnxruntime as rt
    sess=rt.InferenceSession('D:/tmp/kmeans_hz_farm.onnx')
    input_name=sess.get_inputs()[0].name
    label_name=sess.get_outputs()[0].name
    
    pred_onx=sess.run([label_name],{input_name:x.astype(np.float32)})[0]
    
    y_class_labels = kmeans.labels_
    if len(y_class_labels)!=len(Y):
        print('the number of fid and labels are not equal')
        return
        
    cluster_dict = {'FID':Y,'y_class_labels':y_class_labels}
    cluster_results = pd.DataFrame(cluster_dict)
    cluster_results.to_csv('D:/tmp/clusterids.csv', sep=',',index=False )
    
    for s in range(len(Y)):
        mask = segments == Y[s]
        segments[mask] = y_class_labels[s]
        
    #聚类id为0和2的农田被利用了,1和3未被利用
    segments[segments==1]=9999
    segments[segments==3]=9999
    segments[segments==0]=1
    segments[segments==2]=1
    segments[segments==9999]=0
    
    xsize, ysize = segments.shape
    dst_format = 'GTiff'
    dst_nbands = 1
    dst_datatype = gdal.GDT_Float32

    driver = gdal.GetDriverByName(dst_format)
    dst_ds = driver.Create(dst_file, ysize, xsize, dst_nbands, dst_datatype)
    dst_ds.SetGeoTransform(gt)
    dst_ds.SetProjection(proj)
    dst_ds.GetRasterBand(1).WriteArray(segments)
    print('finished...')
    return dst_file

def reclassify_shp(shpfile, clusteridsf):
    dr = ogr.GetDriverByName("ESRI Shapefile")
    #Open()的第二个参数默认为0，是以只读方式打开文件；1是读写方式打开
    ds = dr.Open(shpfile,1)
    layer = ds.GetLayer(0)
    # extent = layer.GetExtent()  # minx, maxx, miny,  maxy
    #图层定义信息
    lydefn = layer.GetLayerDefn()
    fieldlist=[]
    for i in range(lydefn.GetFieldCount()):
         fddefn=lydefn.GetFieldDefn(i)
         # fddict={'name':fddefn.GetName(),'type':fddefn.GetType(),'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
         fieldlist+=[fddefn.GetName()]

    if 'detect' not in fieldlist:
        field_name = ogr.FieldDefn("detect", ogr.OFTInteger)
        layer.CreateField(field_name)

    # feat_num = layer.GetFeatureCount()
    # print(feat_num)
    
    clusterids=pd.read_csv(clusteridsf, sep=',')
    #count number of each cluster pixel
    # clusterids['y_class_labels'].value_counts()[0]
    
    for feat in layer:
        fid = feat.GetField('id')
        print(fid)
       
        #判断该多边形是否被聚类处理了
        if fid in list(clusterids['FID']):
            cid=clusterids.loc[clusterids['FID']==fid]['y_class_labels']
            print(list(cid)[0])
            clusterid=list(cid)[0]
    
            print(clusterid)
        else:
            clusterid=1
            print(fid,'is not clustered')
        
        #聚类id为0和2的农田被利用了
        if clusterid ==0 or clusterid==2:
            feat.SetField('detect', 1)
        elif clusterid==1 or clusterid==3:
            feat.SetField('detect', 0)
        
        #update shapefile field information
        layer.SetFeature(feat)
        feat.Destroy()
    ds.Destroy()
    print('finished')

def main():
    objectsf='D:/tmp/farm_projed_rst.tif'
    # objectsf='/mnt/rsimages/hz/tmp/farm_projed_rst.tif'
    ds = gdal.Open(objectsf)
    segments=ds.ReadAsArray()
    
    imgf='D:/tmp/gf1c_cut.tif'
    # imgf='/mnt/rsimages/hz/tmp/gf1c_cut.tif'
    imgds=gdal.Open(imgf)
    gt=imgds.GetGeoTransform()
    proj=imgds.GetProjection()
    img = imgds.ReadAsArray()
    
    dst_file='D:/tmp/gf1c_objects_onnx.tif'
    # dst_file='/mnt/rsimages/hz/tmp/gf1c_objects_cluster.tif'
    objects_clustering(segments, img, dst_file,gt, proj)
    
    # shpfile = 'D:/data/hz/farm.shp'
    # # shpfile = '/mnt/rsimages/hz/tmp/farm.shp'
    # classified_ids='D:/tmp/clusterids.csv'
    # # classified_ids='/mnt/rsimages/hz/tmp/clusterids.csv'
    # reclassify_shp(shpfile, classified_ids)
    
if __name__ == '__main__':  
    main()