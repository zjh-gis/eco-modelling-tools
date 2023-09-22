import os
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from osgeo import ogr

N_min=15;N_max=56;E_min=72;E_max=137

dem_path = '/mnt/mfs31/SRTMGL1/'
fname = '/mnt/mfs31/RUSLE_LS'
tmp_dir='/mnt/mfs31/tmp'
# zip_name='N19E101.SRTMGL1.hgt.zip'
# filename='N19E108.hgt'

def China_ls():
    cn_border = '/mnt/mfs31/china_border/shp_cn_province.shp'
    for n in range(N_min, N_max):
        for e in range(E_min, E_max):
            print(n,e)
            # 创建格网多边形
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(e, n)
            ring.AddPoint(e+1, n)
            ring.AddPoint(e+1, n+1)
            ring.AddPoint(e, n+1)
            ring.AddPoint(e, n)  # 闭合多边形

            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            e = str(e).zfill(3)

            input_ds = ogr.Open(cn_border)
            if input_ds is None:
                print("无法打开输入shapefile文件")
                return

            # 获取输入shapefile的第一个图层
            input_layer = input_ds.GetLayer()

            # 获取输入shapefile的空间参考信息
            source_srs = input_layer.GetSpatialRef()

            # 判断格网是否与多边形相交或在多边形内部
            input_layer.SetSpatialFilter(poly)

            for feature in input_layer:
                if feature.geometry().Intersects(poly):
                    print('xiangjiao...')
                    lsfile = os.path.join(fname, 'LS_N%s_E%s.tif'%(n,e))
                    zipfile=os.path.join(dem_path,'N%sE%s'%(n,e)+'.SRTMGL1.hgt.zip')
                    unzip_path = os.path.join(dem_path,'unzip')
                    if not os.path.exists(lsfile) and os.path.exists(zipfile):
                        #第一步合并d8的dem文件
                        srcfiles1 = ''
                        for i in range(n-1,n+2):
                            for j in range(int(e)-1, int(e)+2):
                                jj=str(j).zfill(3)
                                zipfile=os.path.join(dem_path,'N%sE%s'%( i,jj)+'.SRTMGL1.hgt.zip')
                                datafile = os.path.join(unzip_path,'N%sE%s.hgt'%( i,jj))                               
                                if not os.path.exists(datafile):
                                    unzip_cmd = 'unzip  %s -d %s'%(zipfile,unzip_path)
                                    os.system(unzip_cmd)
                                if os.path.exists(datafile):
                                    srcfiles1 = srcfiles1+datafile
                                    srcfiles1 = srcfiles1+' '
                        c_dem = os.path.join(unzip_path,'N%sE%s.hgt'%( n,e))     
                        print('当前正在处理%s.......'%c_dem) 
                        num_neighbors = len(srcfiles1.split(' '))
                        print('the %s dem file has %s neighbor files.'% (c_dem, num_neighbors))
                                
                        d8merge_dem=os.path.join(tmp_dir, 'DEM_N%s_E%s.tif'%(n,e))
                        tmp_ls=os.path.join(tmp_dir, 'tmp_LS_N%s_E%s.tif'%(n,e))
                        c_dem_3857=os.path.join(tmp_dir,'dem_3857_N%s_E%s.tif'%(n,e))                     
 
                        merge_cmd1 = 'gdalwarp -wo NUM_THREADS=ALL_CPUS -t_srs EPSG:3857 %s %s'%(srcfiles1, d8merge_dem)
                        os.system(merge_cmd1)   
                        if not os.path.exists(d8merge_dem):
                            print('the dem file %s has no enough d8 files.'% c_dem)

                            continue  

                        #第二步计算d8范围的LS因子
                        cmd = "saga_cmd terrain_analysis 'ta_ls_factor' -DEM %s -LS_FACTOR %s -LS_METHOD 1 -PREPROCESSING 1"%(d8merge_dem, tmp_ls)
                        print(cmd)
                        os.system(cmd)       

                        #第三步转换dem投影到LS因子投影
                        merge_cmd1 = 'gdalwarp -t_srs EPSG:3857 %s %s'%(c_dem, c_dem_3857)
                        os.system(merge_cmd1)   

                        #第四步读取中心区域的LS因子值并保存
                        with rasterio.open(c_dem_3857) as src:
                            # input_image = src.read(1)
                            # input_transform = src.transform
                            # input_crs = src.crs
                            src_bounds = src.bounds
                            crop_box = box(src_bounds.left, src_bounds.bottom, src_bounds.right, src_bounds.top)
                        
                        with rasterio.open(tmp_ls) as src:
                            out_image, out_meta = crop_image(src, crop_box)
                            # 将裁剪后的影像数据保存到新文件中
                            with rasterio.open(lsfile, 'w', **out_meta) as dst:
                                dst.write(out_image)
                        #第五步删除中间临时文件
                        rm_cmd='rm -rf %s %s %s'%(d8merge_dem,tmp_ls,c_dem_3857)
                        print(rm_cmd)
                        os.system(rm_cmd)
                    
                    
def crop_image(src, crop_box):
    # 使用crop_box对源影像进行裁剪
    out_image, out_transform = mask(src, [crop_box], crop=True)
    # 更新裁剪后影像的元数据
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    return out_image, out_meta
# def main():
#     # 打开文件以写入模式
#     with open('/mnt/mfs31/tmp/my_failed_ls_loc.txt', 'w') as file:
#         for n in range(N_min, N_max):
#             for e in range(E_min, E_max):
#                 e = str(e).zfill(3)

#                 zipfile = os.path.join(dem_path,'N%sE%s.SRTMGL1.hgt.zip'%( n,e))
#                 unzip_path = os.path.join(dem_path,'unzip')
#                 unzipfile=os.path.join(unzip_path,'N%sE%s.hgt'%( n,e))
#                 if not os.path.exists(unzipfile):
#                     unzip_cmd = 'unzip %s -d %s'%(zipfile,unzip_path)
#                     os.system(unzip_cmd)

#                 d8merge_dem=os.path.join(tmp_dir, 'DEM_N%s_E%s.tif'%(n,e))
#                 tmp_ls=os.path.join(tmp_dir, 'tmp_LS_N%s_E%s.tif'%(n,e))
#                 c_dem_3857=os.path.join(tmp_dir,'dem_3857_N%s_E%s.tif'%(n,e))
#                 lsfile = os.path.join(fname, 'LS_N%s_E%s.tif'%(n,e))
                
#                 c_dem = unzipfile     
#                 print('当前正在处理%s.......'%c_dem) 
                
#                 if not os.path.exists(lsfile):
#                     #第一步合并d8的dem文件
#                     srcfiles1 = ''
#                     for i in range(n-1,n+2):
#                         for j in range(int(e)-1, int(e)+2):
#                             jj=str(j).zfill(3)
#                             datafile = os.path.join(unzip_path,'N%sE%s.hgt'%( i,jj))
#                             srcfiles1 = srcfiles1+datafile
#                             srcfiles1 = srcfiles1+' '
#                             zipfile=os.path.join(dem_path,'N%sE%s'%( i,jj)+'.SRTMGL1.hgt.zip')
#                             if not os.path.exists(datafile):
#                                 unzip_cmd = 'unzip  %s -d %s'%(zipfile,unzip_path)
#                                 os.system(unzip_cmd)
                
#                     num_neighbors = len(srcfiles1.split(' '))
#                     if num_neighbors<10:
#                         print('the %s dem file has %s neighbor files.'% (c_dem, num_neighbors))
#                         print(srcfiles1)
#                         file.write('This is failed: N%sE%s \n'%( n,e)) 
#                         continue  
#                     merge_cmd1 = 'gdalwarp -wo NUM_THREADS=ALL_CPUS -t_srs EPSG:3857 %s %s'%(srcfiles1, d8merge_dem)
#                     os.system(merge_cmd1)   
#                     if not os.path.exists(d8merge_dem):
#                         print('the dem file %s has no enough d8 files.'% c_dem)
#                         file.write('This is failed: N%sE%s \n'%( n,e)) 
#                         continue  

#                     #第二步计算d8范围的LS因子
#                     cmd = "saga_cmd terrain_analysis 'ta_ls_factor' -DEM %s -LS_FACTOR %s -LS_METHOD 1 -PREPROCESSING 1"%(d8merge_dem, tmp_ls)
#                     print(cmd)
#                     os.system(cmd)       

#                     #第三步转换dem投影到LS因子投影
#                     merge_cmd1 = 'gdalwarp -t_srs EPSG:3857 %s %s'%(c_dem, c_dem_3857)
#                     os.system(merge_cmd1)   

#                     #第四步读取中心区域的LS因子值并保存
#                     with rasterio.open(c_dem_3857) as src:
#                         input_image = src.read(1)
#                         input_transform = src.transform
#                         input_crs = src.crs
#                         src_bounds = src.bounds
#                         crop_box = box(src_bounds.left, src_bounds.bottom, src_bounds.right, src_bounds.top)
                    
#                     with rasterio.open(tmp_ls) as src:
#                         out_image, out_meta = crop_image(src, crop_box)
#                         # 将裁剪后的影像数据保存到新文件中
#                         with rasterio.open(lsfile, 'w', **out_meta) as dst:
#                             dst.write(out_image)
#                     #第五步删除中间临时文件
#                     rm_cmd='rm -rf %s %s %s'%(d8merge_dem,tmp_ls,c_dem_3857)
#                     print(rm_cmd)
#                     os.system(rm_cmd)

if __name__ == '__main__':
    China_ls()



        

       