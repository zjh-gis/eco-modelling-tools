def gen_params(u_llx, u_lly, u_urx, u_ury, res_value, res_unit, x_task, y_task):
    import math
    from rasterio.warp import transform_bounds
    # 输入：
    # u_llx：用户指定的左下角经度
    # u_lly：用户指定的左下角纬度
    # u_urx：用户指定的右上角经度
    # u_ury：用户指定的右上角纬度
    # res_m：分辨率
    # x_task：水平任务数
    # y_task：垂直任务数
    # 输出：
    # params：拆分后的参数列表
    # reduce_kwargs：栅格数据计算结果参数
    if res_unit not in ['meter', 'degree']:
        raise ValueError("res_unit必须是'meter'或'degree'")

    bounds = [u_llx, u_lly, u_urx, u_ury]
    if res_unit == 'meter':
        bxmin, bymin, bxmax, bymax = transform_bounds(4326, 3857, *bounds)
        xsize = math.ceil((bxmax - bxmin)/res_value)
        ysize = math.ceil((bymax - bymin)/res_value)
        xres_deg = (u_urx-u_llx)/xsize
        yres_deg = (u_ury-u_lly)/ysize
    elif res_unit == 'degree':
        xsize = math.ceil((u_urx-u_llx)/res_value)
        ysize = math.ceil((u_ury-u_lly)/res_value)
        xres_deg=res_value
        yres_deg=res_value

    # 最后输出的空间范围比用户指定的空间范围要大，大的距离小于一个像素的宽度
    final_xmax = u_llx+xres_deg*xsize
    final_ymax = u_lly+yres_deg*ysize
    final_xmin = u_llx
    final_ymin = u_lly

    params = [{} for _ in range(x_task*y_task)]
    task_xsize = int(xsize/x_task)
    task_ysize = int(ysize/y_task)
    for j in range(y_task):
        for i in range(x_task):
            task_xmin = final_xmin+task_xsize*i*xres_deg
            task_ymax = final_ymax-task_ysize*j*yres_deg
            # task_ymin = final_ymin+task_ysize*j*yres_deg
            xoff = task_xsize*i
            yoff = task_ysize*j
            w = task_xsize
            h = task_ysize
            if i == x_task-1:
                w = xsize-task_xsize*i
            if j == y_task-1:
                h = ysize - task_ysize*j
            params[i+j*x_task][(i, j)] = [task_xmin, task_ymax-yres_deg*h, task_xmin +
                                          xres_deg*w, task_ymax, xres_deg, yres_deg, xoff, yoff]
    reduce_kwargs = {'llx': final_xmin, 'lly': final_ymin, 'urx': final_xmax,
                     'ury': final_ymax, 'x_res': xres_deg, 'y_res': yres_deg, 'xsize': xsize, 'ysize': ysize}
    return params, reduce_kwargs


def region_read(input_file, xmin, ymin, xmax, ymax, x_res, y_res, band_idx, output_srs):
    from osgeo import gdal
    # # 输入文件路径
    # input_file = 'input.tif'
    # # 定义输出的投影坐标系（可以是EPSG代码或WKT）
    # output_srs = 'EPSG:4326'
    # # 定义输出的区域范围（xmin, ymin, xmax, ymax）
    output_extent = (xmin, ymin, xmax, ymax)
    # # 定义输出的分辨率
    # output_resolution = (x_res, y_res)
    # 使用gdal.Warp进行区域读取、重投影和重采样，并返回读取的数组
    try:
        output_ds = gdal.Warp('', input_file, format='MEM', dstSRS=output_srs,
                              outputBounds=output_extent, xRes=x_res, yRes=y_res,
                              resampleAlg=gdal.GRA_NearestNeighbour, options=['NUM_THREADS=ALL_CPUS'])
    # Available resampling methods:
    # near (default), bilinear, cubic, cubicspline, lanczos, average, rms,
    # mode,  max, min, med, Q1, Q3, sum.
        if output_ds is None:
            raise Exception("Failed to create output dataset.")

        # 将读取的数组转换为NumPy数组,读取第三个波段, band_idx=3
        output_band = output_ds.GetRasterBand(band_idx)
        if output_band is None:
            raise Exception(
                f"Band {band_idx} not found in the output dataset.")

        output_array = output_band.ReadAsArray()
        if output_array is None:
            raise Exception("Failed to read raster data.")

        return output_array
    except Exception as e:
        print("An error occurred:", str(e))
        return None
    finally:
        if output_ds is not None:
            # 关闭输出数据集
            output_ds = None
