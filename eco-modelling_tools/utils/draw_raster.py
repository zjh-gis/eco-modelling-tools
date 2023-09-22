import gdal,ogr, json
import h5py
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
# import cartopy.io.shapereader as shpreader
from shapely.geometry import geo

classid2rgb_map = {
    6: [204, 204, 0],  # "cyan" Ns
    9: [255, 0, 0],  # "red" St
    7: [255, 153, 153],  # "green" Cu
    1: [204, 204, 255],  # "purple" Ci
    3: [0, 0, 255],  # "blue" Dc
    255: [255, 255, 255],  # "yello"
}

def label2rgb(pred_y):
    #print(set(list(pred_y.reshape(-1))))
    rgb_img = np.zeros((pred_y.shape[0], pred_y.shape[1], 3))
    for i in range(len(pred_y)):
        for j in range(len(pred_y[0])):
            rgb_img[i][j] = classid2rgb_map.get(pred_y[i][j], [255, 255, 255])
    return rgb_img.astype(np.uint8)
def draw(geotif,shpname,geo_range_str,dstfig):
    if geotif.endswith('.hdf'):
        f = h5py.File(geotif,'r')
        data = f['FY4CLT'][()]
    elif geotif.endswith('.tif'):
        #cloudtype -- gray to rgb
        ds = gdal.Open(geotif)
        data = ds.ReadAsArray()
    cloudt_rgb = label2rgb(data)
        # 绘图
    PlateCarree = ccrs.PlateCarree()
    plt.figure('figure name')
    ax = plt.axes(projection=PlateCarree)

    provinces_geometrys = []
    dr = ogr.GetDriverByName('ESRI Shapefile')
    shp_ds = dr.Open(shpname)
    layer = shp_ds.GetLayer(0)
    feat_num = layer.GetFeatureCount()
    for i in range(feat_num):
        feat = layer.GetFeature(i)
        geom = feat.GetGeometryRef()
        geojson = json.loads(geom.ExportToJson())
        x = geo.shape(geojson)
        provinces_geometrys.append(x)
    
    # for feature in vector:
    #     x = geo.shape(feature['geometry'])
    #     provinces_geometrys.append(x)
    # provinces_records = list(shpreader.Reader(shpname).records())
    # print(provinces_records[0].geometry)
    # provinces_geometrys = [x.geometry for x in provinces_records]
    ax.add_geometries(provinces_geometrys, PlateCarree,
                      edgecolor='black', facecolor='None')
    
    lat_S, lat_N, lon_W, lon_E, step = eval(geo_range_str)
    extent=[lon_W - 0.05, lon_E + 0.05, lat_S - 0.05, lat_N + 0.05]
    
    ax.imshow(cloudt_rgb, transform=PlateCarree, origin='upper',
              extent=extent)
#     ax.imshow(cloudt_rgb, cmap='rgb', transform=PlateCarree, origin='upper',
#               extent=extent)
    ax.set_xticks(list(range(int(lon_W), int(lon_E)+1, 10)), PlateCarree)
    ax.set_yticks(list(range(int(lat_S), int(lat_N)+1, 10)), PlateCarree)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.coastlines()
#     plt.show()
    # plt.savefig(r'..\data\FY4A\FY4A-_AGRI--_N_REGC_1047E_L1-_FDI-_MULT_NOM_20200107093418_20200107093835_4000M_V0001_Tbb云顶亮温（Channel12）')
    plt.savefig(dstfig)