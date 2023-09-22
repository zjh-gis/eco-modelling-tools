import dboxmr
from copy import deepcopy
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class split_class(object):

    def C_cal(self, minx, miny, maxx, maxy, xres_deg, yres_deg, **kwargs):
        import numpy as np
        import tools
        lulc_file = kwargs['lulc']
        ndvi_file = kwargs['ndvi']
        # MODND1T 中国 500M NDVI 旬合成产品

        lulc = tools.region_read(lulc_file, minx, miny, maxx,
                                 maxy, xres_deg, yres_deg, 1, 'EPSG:4326')

        ndvi_all = []
        for m in range(1, 13):
            file_in = ndvi_file % str(m).zfill(2)
            ndvi = tools.region_read(file_in, minx, miny, maxx,
                                     maxy, xres_deg, yres_deg, 1, 'EPSG:4326')

            ndvi_all.append(ndvi*0.0001)
        # ndvi_all = np.asarray(ndvi_all).reshape(12, ndvi.shape[0], ndvi.shape[1])
        ndvi_all = np.stack(ndvi_all, axis=0)
        ndvi_mean = np.nanmean(ndvi_all, axis=0)

        # C = np.zeros([lulc.shape[0], lulc.shape[1]])
        C = np.ones_like(lulc)  # 植被因子代表植被对土壤保护能力的大小，其值越小表明对土壤的保护能力越大，反之则越小。
        C = C.astype(float)
        # lindi  -0.1535 101 102 103 104 108 109
        lindi_cond = np.logical_or.reduce(
            [(lulc == 101), (lulc == 102), (lulc == 103), (lulc == 104), (lulc == 108), (lulc == 109)])
        C[lindi_cond] = np.exp(-0.1535*ndvi_mean)[lindi_cond]

        # guancong -0.0921 105 106 107 110
        guancong_cond = np.logical_or.reduce(
            [(lulc == 105), (lulc == 106), (lulc == 107), (lulc == 110)])
        C[guancong_cond] = np.exp(-0.0921*ndvi_mean)[guancong_cond]

        # caodi -0.1151 201 202 203 204 205 206 207 208
        caodi_cond1 = (lulc > 200) & (lulc < 300)
        caodi_cond2 = (lulc == 505) | (lulc == 506) | (lulc == 508)
        caodi_cond = np.logical_or(caodi_cond1, caodi_cond2)
        C[caodi_cond] = np.exp(-0.1151*ndvi_mean)[caodi_cond]

        # nongtian -0.0438
        nongtian_cond = np.logical_or.reduce(
            [(lulc == 402), (lulc == 403), (lulc == 501), (lulc == 502), (lulc == 504)])
        C = np.where(nongtian_cond, np.exp(-0.0438*ndvi_mean), C)

        # luodi -0.0768
        luodi_cond = np.logical_or.reduce(
            [(lulc == 1001), (lulc == 1002), (lulc == 1003)])
        C = np.where(luodi_cond, np.exp(-0.0768*ndvi_mean), C)

        # shadi -0.0658
        C[(lulc == 1005)] = np.exp(-0.0658*ndvi_mean)[(lulc == 1005)]

        C[C > 1] = 1

        return C

    def doit(self, data, subtask=None, **kwargs):
        import numpy as np
        import tools

        # tile_id = list(data.keys())[0]
        t_llx, t_lly, t_urx, t_ury, xres_deg, yres_deg, xoff, yoff = list(data.values())[
            0]

        WF_file = kwargs['WF']
        WF = tools.region_read(WF_file, t_llx, t_lly, t_urx,
                               t_ury, xres_deg, yres_deg, 1, 'EPSG:4326')

        EF_file = kwargs['EF']
        EF = tools.region_read(EF_file, t_llx, t_lly, t_urx,
                               t_ury, xres_deg, yres_deg, 1, 'EPSG:4326')

        SCF_file = kwargs['SCF']
        SCF = tools.region_read(SCF_file, t_llx, t_lly, t_urx,
                                t_ury, xres_deg, yres_deg, 1, 'EPSG:4326')

        K_file = kwargs['K']
        K = tools.region_read(K_file, t_llx, t_lly, t_urx,
                              t_ury, xres_deg, yres_deg, 1, 'EPSG:4326')

        C = self.C_cal(t_llx, t_lly, t_urx, t_ury,
                       xres_deg, yres_deg, **kwargs)

        z = kwargs['z']  # 最大风蚀出现距离

        Qmaxqian = 109.8*WF * EF * SCF * K
        Sqian = 150.71*(Qmaxqian**(-0.3711))
        SLqian = 2*z*Qmaxqian*np.exp(-(z/Sqian)**2)  # 为潜在风力侵蚀量

        Qmax = 109.8*WF * EF * SCF * K*C
        S = 150.71*(Qmax**(-0.3711))
        SL = 2*z*Qmax*np.exp(-(z/S)**2)  # 实际土壤侵蚀量

        SR = SLqian-SL  # SR 为固沙量
        SR[SR < 0] = 0

        return {'array': SR, 'xoff': xoff, 'yoff': yoff}

    def __call__(self, data, **kwargs):
        return self.doit(data, **kwargs)


def merge_func(data, **kwargs):
    import rasterio
    from rasterio.crs import CRS
    from rasterio.windows import Window
    llx = kwargs['llx']
    lly = kwargs['lly']
    urx = kwargs['urx']
    ury = kwargs['ury']
    transform = rasterio.transform.from_bounds(
        llx, lly, urx, ury, width=kwargs['xsize'], height=kwargs['ysize'])
    crs = CRS.from_epsg(4326)

    try:
        if data is None or len(data) == 0:
            raise ValueError("Data is None or empty.")

        first_data = data[0]
        if not isinstance(first_data, dict):
            raise TypeError("The first element in data is not a dictionary.")

        array_data = first_data.get('array')
        if array_data is None:
            raise ValueError("'array' key is missing or its value is None.")

        dtype = array_data.dtype
        # 在这里继续处理 dtype 和其他逻辑
        with rasterio.open(kwargs['outfile'], 'w', driver='GTiff', width=kwargs['xsize'], height=kwargs['ysize'], count=1, dtype=dtype, crs=crs, transform=transform) as dst:
            for task in data:
                array = task['array']
                xoff = task['xoff']
                yoff = task['yoff']
                ysize, xsize = array.shape
                dst.write(array, window=Window(
                    xoff, yoff, xsize, ysize), indexes=1)
        return data[0]['array']

    except ValueError as ve:
        print("ValueError:", ve)
    except TypeError as te:
        print("TypeError:", te)
    except Exception as e:
        print("An error occurred:", str(e))


def main(u_llx, u_lly, u_urx, u_ury, res_value, res_unit, map_kwargs):
    x_task = 2
    y_task = 2

    import tools
    try:
        params, reduce_kwargs = tools.gen_params(u_llx, u_lly, u_urx, u_ury, res_value,res_unit, x_task, y_task)
        client = dboxmr.Client("10.0.82.52:6600")
        reduce_kwargs["outfile"] = '/mnt/mfs31/tmp/test_rweq_4326.tif'

        params1 = deepcopy(params)
        print(params1)

        result = client.mapreduce(
            params1,
            split_class,
            merge_func,
            map_kwargs=map_kwargs,
            py_modules=[tools],
            # remove_lasy=True,
            title="soil erosion",
            timeout=1200,
            # timeout=120,
            priority=0,
            # favor_nodes=["group0"],
            # allow_other_nodes=False,
            reduce_kwargs=reduce_kwargs)
        print("soil erosion:", result.results)
        # 如果res_unit是'meter'或'degree'，继续执行其他操作
    except ValueError as e:
        print(e)  # 打印异常信息
     


if __name__ == '__main__':
    u_llx = 110
    u_lly = 30
    u_urx = 120
    u_ury = 35
    res_value = 1000
    res_unit='meter'
    year = 2015
    #  NDVI的有效值为-2000到10000，使用时，需乘以0.0001
    map_kwargs = {'WF': '/mnt/mfs31/data/RWEQ/WF.tif', 'EF': '/mnt/mfs31/data/RWEQ/EF.tif',
                  'SCF': '/mnt/mfs31/data/RWEQ/SCF.tif',  'K': '/mnt/mfs31/data/RWEQ/K.tif',
                  'lulc': '/mnt/mfs31/data/landcover/lcc2015_90m.tif',
                  'ndvi': '/mnt/mfs31/data/ndvi/2015/MOD13A3_A2015%s_1kmMonthNDVI.tif',
                  'z': 50}
    # WF 为气候侵蚀因子（kg/m）；K 为地表糙度因子；EF 为土壤侵蚀因子；SCF 为土壤结皮因子；C 为植被覆盖因子。z 为最大风蚀出现距离（m)
    main(u_llx, u_lly, u_urx, u_ury, res_value,res_unit, map_kwargs)
