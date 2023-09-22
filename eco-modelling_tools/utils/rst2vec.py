import os, sys
from osgeo import gdal, ogr, osr

def polygonize_raster(inRasterfile, outShapefile):
    src_ds = gdal.Open(inRasterfile)
    if src_ds is None:
        print('Unable to open %s' % inRasterfile)
        sys.exit(1)
    srcband = src_ds.GetRasterBand(1)
    srs_wkt=src_ds.GetProjectionRef()
    
    driname = outShapefile.split('.')[-1]
    if driname=='shp':
        outDriver = ogr.GetDriverByName("ESRI Shapefile")
    elif driname =='geojson':
        outDriver = ogr.GetDriverByName("geojson")
    else:
        print('the vector format is not supported, only shp and geojson')
        sys.exit(1)
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDataSource = outDriver.CreateDataSource(outShapefile)
    
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(srs_wkt)
    if spatialRef is None:
        print('no projection information')
        sys.exit(1)
    outLayer = outDataSource.CreateLayer('segs', srs=spatialRef)

    idField = ogr.FieldDefn('id', ogr.OFTInteger)
    outLayer.CreateField(idField)
    dst_field = outLayer.GetLayerDefn().GetFieldIndex('id')
    print(dst_field)
    gdal.Polygonize(srcband, None, outLayer, dst_field, [], callback=None)
    outDataSource.Destroy()

    srcband = None
    src_ds = None
    return
def polygonize_array(gt, proj, array, outShapefile):
    tmpRasterfile='/home/zjh/tmp/segraster.tif'
    xsize, ysize = array.shape
    dst_format = 'GTiff'
    dst_nbands = 1
    dst_datatype = gdal.GDT_Int16  # GDT_Float32
    
    driver = gdal.GetDriverByName(dst_format)
    dst_ds = driver.Create(tmpRasterfile, ysize, xsize, dst_nbands, dst_datatype)
    dst_ds.SetGeoTransform(gt)
    dst_ds.SetProjection(proj)
    dst_ds.GetRasterBand(1).WriteArray(array)
    dst_ds = None
#     cmd='gdal_polygonize.py %s -f GEOJSON  %s' % (dst_file,jsonfile)
#     os.system(cmd)
    polygonize_raster(tmpRasterfile, outShapefile)
    cmd = 'rm %s'%tmpRasterfile
    print(cmd)
    os.system(cmd)
    #             cmd='gdal_polygonize.py %s -f GEOJSON  %s' % (dst_file,jsonfile)
    #             os.system(cmd)
#     return vector_file 
    del dst_ds
    return