from osgeo import gdal


imagefile='/mnt/win/data/xiongan/Jingjinji_7_15_utm.tif'
ds_img = gdal.Open(imagefile) 
xsize = ds_img.RasterXSize
ysize = ds_img.RasterYSize
off_list = gen_tiles_offs(xsize, ysize, BLOCK_SIZE,OVERLAP_SIZE)
for xoff, yoff in off_list:
    data = ds_img.ReadAsArray(xoff,yoff, BLOCK_SIZE, BLOCK_SIZE)
    if np.all(data == 0) or np.all(label == 0) or (data==0).sum()>128*128*3:
        continue
    band1=data[0]
    band2=data[1]
    band3=data[2]
    
    imgcolor = bands_stack(band1,band2,band3)

    import cv2
#         img = normalize(grey_data)
    cv2.imwrite('/tmp/jjj_2m/Jingjinji_7_15_%s_%s.jpg'%(xoff, yoff),imgcolor)