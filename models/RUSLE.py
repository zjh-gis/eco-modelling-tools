import dboxmr
from copy import deepcopy

class split_class(object):
    def erosivity(self, z, p, k, sdii):
        import numpy as np

        try:
            if z is None or p is None or k is None or sdii is None:
                raise ValueError("Input value for R factor is None.")
            
            r_out = np.zeros(z.shape,dtype=float)
            r_out[p==-9999]= np.nan
            r_out[p <= 850.]= (0.0483*p**1.61)[p <= 850.]
            r_out[p > 850.] = (587.8-1.219*p+0.004105*p**2)[p > 850.]

            #气候分区的命名方式为字母缩写组合, 字母缩写意义为B：干旱区Arid, C：温和区Temperate, D：寒冷区Cold, W：沙漠区Desert, S：干旱草原Steppe, k：Cold, f：Without dry season, w：Dry Winter, a：Hot Summer, b：Warm Summer
            #BWk
            r_out[(k== 5)&(sdii!= -9999)]=(0.809*p**0.957 + 0.000189*sdii**6.285)[(k== 5)&(sdii!= -9999)]
            r_out[(k== 5)&(sdii== -9999)&(p<= 850)]=(0.0483*p**1.61)[(k== 5)&(sdii== -9999)&(p<= 850)]
            r_out[(k== 5)&(sdii== -9999)&(p> 850)]=(587.8-1.219*p+0.004105*p**2)[(k== 5)&(sdii== -9999)&(p> 850)]
            
            # r_out[(k== 6)&(sdii== -9999)]=(np.exp(-8.164+2.455*np.log(p)))[(k== 6)&(sdii== -9999)]
            # r_out[(k== 6)&(sdii!= -9999)]=(np.exp(-7.72+1.595*np.log(p)+2.068*np.log(sdii)))[(k== 6)&(sdii!= -9999)]

            #BSk
            r_out[(k== 7)&(sdii== -9999)]=(np.exp(5.52+1.33*np.log(p)-(0.977*np.log(z))))[(k== 7)&(sdii== -9999)]
            r_out[(k== 7)&(sdii!= -9999)]=(np.exp(0.0793+0.887*np.log(p)+1.892*np.log(sdii)-(0.429*np.log(z))))[(k== 7)&(sdii!= -9999)]
            # r_out[(k== 7)&(z >= 200)&(sdii== -9999)]=(np.exp(5.52+1.33*np.log(p)-(0.977*np.log(z))))[(k== 7)&(z >= 200)&(sdii== -9999)]
            # r_out[(k== 7)&(z >= 200)&(sdii!= -9999)]=(np.exp(0.0793+0.887*np.log(p)+1.892*np.log(sdii)-(0.429*np.log(z))))[(k== 7)&(z >= 200)&(sdii!= -9999)]
            # r_out[(k== 7)&(z < 200)&(sdii== -9999)]=(np.exp(5.52+1.33*np.log(p)-(0.977*np.log(200.))))[(k== 7)&(z < 200)&(sdii== -9999)]
            # r_out[(k== 7)&(z < 200)&(sdii!= -9999)]=(np.exp(0.0793+0.887*np.log(p)+1.892*np.log(sdii)-(0.429*np.log(200.))))[(k== 7)&(z < 200)&(sdii!= -9999)]
            
            # r_out[(k== 9)] = (98.35+0.0003549*p**1.987)[(k== 9)]

            #Cfa
            r_out[(k== 14)&(sdii== -9999)]=(np.exp(3.378+0.852*np.log(p)-(0.191*np.log(z))))[(k== 14)&(sdii== -9999)]
            r_out[(k== 14)&(sdii!= -9999)]=(np.exp(0.524+0.462*np.log(p)-(0.106*np.log(z))+1.97*np.log(sdii)))[(k== 14)&(sdii!= -9999)]
            # r_out[(k== 14)&(z>= 4.5)&(sdii== -9999)]=(np.exp(3.378+0.852*np.log(p)-(0.191*np.log(z))))[(k== 14)&(z>= 4.5)&(sdii== -9999)]
            # r_out[(k== 14)&(z >= 4.5)&(sdii!= -9999)]=(np.exp(0.524+0.462*np.log(p)-(0.106*np.log(z))+1.97*np.log(sdii)))[(k== 14)&(z >= 4.5)&(sdii!= -9999)]
            # r_out[(k== 14)&(z< 4.5)&(sdii== -9999)]=(np.exp(3.378+0.852*np.log(p)-(0.191*np.log(4.5))))[(k== 14)&(z< 4.5)&(sdii== -9999)]
            # r_out[(k== 14)&(z <4.5)&(sdii!= -9999)]=(np.exp(0.524+0.462*np.log(p)-(0.106*np.log(4.5))+1.97*np.log(sdii)))[(k== 14)&(z <4.5)&(sdii!= -9999)]
            
            # r_out[(k== 15)&(z >=75)&(sdii== -9999)]=(np.exp(5.267 + 0.839 * np.log(p) - (0.635 * np.log(z))))[(k== 15)&(z >=75)&(sdii== -9999)]
            # r_out[(k== 15)&(z <75)&(sdii== -9999)] = (np.exp(5.267 + 0.839 * np.log(p) - (0.635 * np.log(75.))))[(k== 15)&(z <75)&(sdii== -9999)]
            # r_out[(k== 15)&(sdii!= -9999)] = (np.exp(-4.853 + 0.676 * np.log(p) + 3.34 * np.log(sdii)))[(k== 15)&(sdii!= -9999)]
            # r_out[(k== 17)&(sdii== -9999)] = (np.exp(7.49 - 0.0512 * np.log(p) - (0.272 * np.log(z))))[(k== 17)&(sdii== -9999)]
            # r_out[(k== 17)&(sdii!= -9999)] = (np.exp(8.602 - 0.963 * np.log(sdii) - (0.247 * np.log(z))))[(k== 17)&(sdii!= -9999)]
            # r_out[(k== 18)] =(np.exp(2.166 + 0.494 * np.log(p)))[(k== 18)]
            # r_out[(k== 19)&(sdii== -9999)] =(np.exp(4.416 + 0.0594 * np.log(p)))[(k== 19)&(sdii== -9999)]
            # r_out[(k== 19)&(sdii!= -9999)] =(np.exp(6.236 - (0.869 * np.log(sdii))))[(k== 19)&(sdii!= -9999)]

            # Dwa
            r_out[(k== 21)] =(np.exp(-0.572 + 1.238 * np.log(p)))[(k== 21)]
            
            #Dwb
            r_out[(k== 22)&(sdii== -9999)] =(np.exp(1.882 + 0.819 * np.log(p)))[(k== 22)&(sdii== -9999)]
            r_out[(k== 22)&(sdii!= -9999)] =(np.exp(-1.7 + 0.788 * np.log(p) + 1.824 * np.log(sdii)))[(k== 22)&(sdii!= -9999)]
            # r_out[(k== 25)&(sdii== -9999)] =(np.exp(-2.396 + 1.5 * np.log(p)))[(k== 25)&(sdii== -9999)]
            # r_out[(k== 25)&(sdii!= -9999)] =(np.exp(-1.99 + 0.737 * np.log(p) + 2.033 * np.log(sdii)))[(k== 25)&(sdii!= -9999)]
            
            #Dfb
            r_out[(k== 26)&(sdii== -9999)]=(np.exp(1.96 + 1.084 * np.log(p) - (0.34 * np.log(z))))[(k== 26)&(sdii== -9999)]
            r_out[(k== 26)&(sdii!= -9999)]=(np.exp(-0.5 + 0.266 * np.log(p) - (0.131 * np.log(z)) + 3.1 * np.log(sdii)))[(k== 26)&(sdii!= -9999)]
            # r_out[(k== 26)&(z>= 65)&(sdii== -9999)]=(np.exp(1.96 + 1.084 * np.log(p) - (0.34 * np.log(z))))[(k== 26)&(z>= 65)&(sdii== -9999)]
            # r_out[(k== 26)&(z >= 65)&(sdii!= -9999)]=(np.exp(-0.5 + 0.266 * np.log(p) - (0.131 * np.log(z)) + 3.1 * np.log(sdii)))[(k== 26)&(z >= 65)&(sdii!= -9999)]
            # r_out[(k== 26)&(z< 65)&(sdii== -9999)]=(np.exp(1.96 + 1.084 * np.log(p) - (0.34 * np.log(65.))))[(k== 26)&(z< 65)&(sdii== -9999)]
            # r_out[(k== 26)&(z <65)&(sdii!= -9999)]=(np.exp(-0.5 + 0.266 * np.log(p) - (0.131 * np.log(65.)) + 3.1 * np.log(sdii)))[(k== 26)&(z <65)&(sdii!= -9999)]
            # r_out[(k== 27)&(sdii== -9999)] =(np.exp(-3.263 + 1.576 * np.log(p)))[(k== 27)&(sdii== -9999)]
            # r_out[(k== 27)&(sdii!= -9999)]=(np.exp(-1.259 + 3.862 * np.log(sdii)))[(k== 27)&(sdii!= -9999)]
            # r_out[(k== 29)]=(np.exp(-3.945 + 1.54 * np.log(p)))[(k== 29)]
            # r_out[(k== 30)]=(np.exp(16.39 - 1.286 * np.log(p)))[(k== 30)]
            # r_out[(k== 31)&(sdii== -9999)] =(np.exp(-10.66 + 2.43 * np.log(p)))[(k== 31)&(sdii== -9999)]
            # r_out[(k== 31)&(sdii!= -9999)]=(np.exp(21.44 + 1.293 * np.log(p) - (10.579 * np.log(sdii))))[(k== 31)&(sdii!= -9999)]
            # r_out[(k== 32)]=(np.exp(16.39-1.286*np.log(p)))[(k== 32)]

            r_out[r_out == -9999.] = np.nan
            return r_out
        
        except Exception as e:
            print("An error occurred:", str(e))
            return None

        
    def R_cal(self, minx, miny, maxx, maxy, xres_deg, yres_deg, **kwargs):
        import numpy as np
        import tools

        climate_file = kwargs['climatev']
        k = tools.region_read(climate_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 1, 'EPSG:4326')
        if k is not None:
        # 将数组转换为 NumPy 数组并进行进一步处理
            k_np = np.array(k)
            k = k_np.astype(float)
            k[k < 0.] = np.nan

        precip_file = kwargs['precip']
        precip = tools.region_read(precip_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 1, 'EPSG:4326')
        if precip is not None:
            precip_np = np.array(precip)
            precip = precip_np.astype(float)
            precip[precip <= 0.] = np.nan
            precip[(0. < precip) & (precip < 1.)] = 1.

        # SDII (simple precipitation index data) is the sum of precip on wet days (precip>1mm) divided by the number of wet days in a period
        sdii_file = kwargs['SDII']
        sdii =  tools.region_read(sdii_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 1, 'EPSG:4326')

        elev_file = kwargs['ELEV']
        elev = tools.region_read(elev_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 1, 'EPSG:4326')
        if elev is not None:
            elev_np = np.array(elev)
            elev = elev_np.astype(float)
            elev[elev < 0.] = np.nan
            elev[(0. <= elev) & (elev < 0.001)] = 0.001

        r = self.erosivity(elev, precip, k, sdii)  # shape(kols*rows)
        return r

    def K_cal(self, minx, miny, maxx, maxy, xres_deg, yres_deg, **kwargs):
        import numpy as np
        import tools

        sand_file = kwargs['sand']
        silt_file = kwargs['silt']
        clay_file = kwargs['clay']
        oc_file = kwargs['oc']

        sand_t = tools.region_read(
            sand_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 3, 'EPSG:4326')
        silt_t = tools.region_read(
            silt_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 3, 'EPSG:4326')
        clay_t = tools.region_read(
            clay_file, minx, miny, maxx, maxy, xres_deg, yres_deg, 3, 'EPSG:4326')
        oc_t = tools.region_read(oc_file, minx, miny, maxx,
                                maxy, xres_deg, yres_deg, 3, 'EPSG:4326')

        # 如果分辨率相同，则直接计算
        Kepic = (0.2+0.3*(np.exp(-0.0256*sand_t*(1-(silt_t/100))))) * ((silt_t/(clay_t+silt_t))**0.3) * (1-((0.25*oc_t) /
                                                                                                            (oc_t+np.exp(3.72-2.95*oc_t)))) * (1-(0.7*(1-sand_t/100))/((1-sand_t/100)+np.exp(-5.51+22.9*(1-sand_t/100))))
        K = (-0.01383+0.51571*Kepic)*0.1317

        return K

        # return {'array': K, 'tileid': tile_id,'gt':gt,'xsize':xsize, 'ysize':ysize}
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
            # 数据的有效值范围为-2000到10000，使用时，需乘以0.0001
            ndvi_all.append(ndvi*0.01)

        # ndvi_all = np.asarray(ndvi_all).reshape(12, ndvi.shape[0], ndvi.shape[1])
        ndvi_all = np.stack(ndvi_all, axis=0)
        ndvi_max = np.nanmax(ndvi_all, axis=0)

        # C = np.zeros([lulc.shape[0], lulc.shape[1]])
        C = np.ones_like(lulc)
        C = C.astype(float)

        # senlin
        C[(lulc == 1) & (ndvi_max < 10)] = 0.1
        C[(lulc == 1) & (ndvi_max >= 10) & (ndvi_max < 30)] = 0.08
        C[(lulc == 1) & (ndvi_max >= 30) & (ndvi_max < 50)] = 0.06
        C[(lulc == 1) & (ndvi_max >= 50) & (ndvi_max < 70)] = 0.02
        C[(lulc == 1) & (ndvi_max >= 70) & (ndvi_max < 90)] = 0.004
        C[(lulc == 1) & (ndvi_max >= 90)] = 0.001

        # guancong
        C[(lulc == 2) & (ndvi_max < 10)] = 0.4
        C[(lulc == 2) & (ndvi_max >= 10) & (ndvi_max < 30)] = 0.22
        C[(lulc == 2) & (ndvi_max >= 30) & (ndvi_max < 50)] = 0.14
        C[(lulc == 2) & (ndvi_max >= 50) & (ndvi_max < 70)] = 0.085
        C[(lulc == 2) & (ndvi_max >= 70) & (ndvi_max < 90)] = 0.040
        C[(lulc == 2) & (ndvi_max >= 90)] = 0.011

        # caodi
        C[(lulc == 3) & (ndvi_max < 10)] = 0.45
        C[(lulc == 3) & (ndvi_max >= 10) & (ndvi_max < 30)] = 0.24
        C[(lulc == 3) & (ndvi_max >= 30) & (ndvi_max < 50)] = 0.15
        C[(lulc == 3) & (ndvi_max >= 50) & (ndvi_max < 70)] = 0.09
        C[(lulc == 3) & (ndvi_max >= 70) & (ndvi_max < 90)] = 0.043
        C[(lulc == 3) & (ndvi_max >= 90)] = 0.011

        C[lulc == 4] = 0  # shidi

        tmp = 0.221-0.595*np.log(ndvi_max)  # nongtian, using method for handi
        C[lulc == 5] = tmp[lulc == 5]

        # yuandi
        # C[(lulc==5)&(ndvi_max<10)]=0.42
        # C[(lulc==5)&(ndvi_max>=10)&(ndvi_max<30)]=0.23
        # C[(lulc==5)&(ndvi_max>=30)&(ndvi_max<50)]=0.14
        # C[(lulc==5)&(ndvi_max>=50)&(ndvi_max<70)]=0.089
        # C[(lulc==5)&(ndvi_max>=70)&(ndvi_max<90)]=0.042
        # C[(lulc==5)&(ndvi_max>=90)]=0.011

        C[lulc == 6] = 0.01  # chengzhen
        C[lulc == 7] = 0.7  # huangmo
        C[lulc == 8] = 0.7  # qita

        C[C > 1] = 1
        return C

        # return {'array': C, 'tileid': tile_id, 'gt': gt, 'xsize': xsize, 'ysize': ysize}

    def doit(self, data, subtask=None, **kwargs):
        import tools 

        # tile_id = list(data.keys())[0]
        t_llx, t_lly, t_urx, t_ury, xres_deg, yres_deg, xoff, yoff = list(data.values())[0]

        try:
            LS_file = kwargs['LS']
            LS = tools.region_read(LS_file, t_llx, t_lly, t_urx,
                                t_ury, xres_deg, yres_deg, 1, 'EPSG:4326')

            if LS is None:
                raise ValueError("LS data is None.")

            C = self.C_cal(t_llx, t_lly, t_urx, t_ury,
                        xres_deg, yres_deg, **kwargs)
            
            if C is None:
                raise ValueError("C data is None.")

            K = self.K_cal(t_llx, t_lly, t_urx, t_ury,
                        xres_deg, yres_deg, **kwargs)

            if K is None:
                raise ValueError("K data is None.")
            
            R = self.R_cal(t_llx, t_lly, t_urx, t_ury,
                        xres_deg, yres_deg, **kwargs)

            if R is None:
                raise ValueError("R data is None.")

            # 将小于等于0的元素置为0
            R[R <= 0] = 0
            K[K <= 0] = 0
            C[C <= 0] = 0
            LS[LS <= 0] = 0
            
            # 进一步处理数据
            # 计算乘积 E = R * K * C * LS
            E = R*K*C*LS

            return {'array': E,  'xoff': xoff, 'yoff': yoff}
            
        except ValueError as ve:
            print("ValueError:", ve)
        except Exception as e:
            print("An error occurred:", str(e))

       

    '''
    入口函数
    '''

    def __call__(self, data, **kwargs):
        return self.doit(data, **kwargs)


'''
map/reduce 函数实现，会自动序列化到集群内部执行
kwargs 必须存在
    map_kwargs 或 reduce_kwargs 的全局参数会传入
    subtask 子任务信息
'''


def merge_func(data, **kwargs):
    import rasterio
    from rasterio.crs import CRS
    from rasterio.windows import Window
    llx = kwargs['llx']
    lly = kwargs['lly']
    urx = kwargs['urx']
    ury = kwargs['ury']
    transform = rasterio.transform.from_bounds(llx, lly, urx, ury, width=kwargs['xsize'], height=kwargs['ysize'])
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
        return  data[0]['array']
        
    except ValueError as ve:
        print("ValueError:", ve)
    except TypeError as te:
        print("TypeError:", te)
    except Exception as e:
        print("An error occurred:", str(e))  

    # import concurrent.futures
    # def write_chunk(chunk):
    #     array, xoff, yoff = chunk
    #     ysize, xsize = array.shape
    #     dst.write(array, window=Window(xoff, yoff, xsize, ysize), indexes=1)
    # with rasterio.open(kwargs['outfile'], 'w', driver='GTiff', width=kwargs['xsize'], height=kwargs['ysize'], count=1, dtype=dtype, crs=crs, transform=transform) as dst:
    #     chunks=[]
    #     for task in data:
    #         array = task['array']
    #         xoff = task['xoff']
    #         yoff = task['yoff']
    #         chunks.apend((array, xoff, yoff))
    #          # Multi-threaded processing
    #         with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    #             executor.map(write_chunk, chunks)

    
def main(u_llx, u_lly, u_urx, u_ury, res_m, map_kwargs, output):
    x_task = 2
    y_task = 2

    import tools
    params, reduce_kwargs = tools.gen_params(
        u_llx, u_lly, u_urx, u_ury, res_m, x_task, y_task)

    client = dboxmr.Client("10.0.82.52:6600")
    reduce_kwargs["outfile"] = output

    params1 = deepcopy(params)

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


if __name__ == '__main__':
    # 根据用户输入的上下文信息
    u_llx = 72.1
    u_lly = 18.1
    u_urx = 140.1
    u_ury = 54.1
    # u_llx=72.1;u_lly=18.1;u_urx=92.1;u_ury=36.1
    # u_llx=72.1;u_lly=36.1;u_urx=92.1;u_ury=54.1
    # u_llx=92.1;u_lly=18.1;u_urx=115.1;u_ury=36.1
    # u_llx=92.1;u_lly=36.1;u_urx=115.1;u_ury=54.1
    # u_llx=115.1;u_lly=18.1;u_urx=140.1;u_ury=36.1
    # u_llx=115.1;u_lly=36.1;u_urx=140.1;u_ury=54.1

    res_m = 1000
    year = 2010

    map_kwargs = {'sand': '/mnt/mfs31/RUSLE_K/SAND1.tif', 'silt': '/mnt/mfs31/RUSLE_K/SILT1.tif',
                  'clay': '/mnt/mfs31/RUSLE_K/CLAY1_clipped.tif', 'oc': '/mnt/mfs31/RUSLE_K/OC1.tif',
                  'LS':'/mnt/mfs31/RUSLE_LS/china_ls_900m.tif',
                  'climatev': '/mnt/mfs31/RUSLE_R/CLIMATEVNETCDF_1000m.tif', 'precip': '/mnt/mfs31/RUSLE_R/pre_2001_2013_1000m/P_total_2010.tif',
                  'SDII': '/mnt/mfs31/RUSLE_R/pre_2001_2013_1000m/SDII_2010.tif', 'ELEV': '/mnt/mfs31/RUSLE_R/ELEVNETCDF_1000m.tif',
                  'lulc': '/mnt/mfs31/data/landcover/l1_lc2010_cn90.tif', 'ndvi':  '/mnt/mfs31/data/ndvi/2010/MOD13A3_A2010%s_1kmMonthNDVI.tif'}
    output = '/mnt/mfs31/tmp/test_ndvimax.tif'
    main(u_llx, u_lly, u_urx, u_ury, res_m, map_kwargs, output)
