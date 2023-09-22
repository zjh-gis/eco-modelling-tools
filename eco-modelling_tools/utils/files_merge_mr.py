import dboxmr
from copy import deepcopy
import os

from rasterio.warp import transform_bounds


# params = [[5000,5000,3,3],[1200,1200,3,3],[35000,4000,3,3]]
map_kwargs={'year':2010,'root':'/mnt/mfs31/RUSLE_C/ndvi/'}

params = [i for i in range(1, 13)]

reduce_kwargs={}


def m_reduce_func(data, **kwargs):
    return data


class m_map_class(object):
    def doit(self, data, subtask=None, **kwargs):
        year=kwargs['year']
        root = os.path.join(kwargs['root'],str(year))
        date='%s.%s.01'% (year,str(data).zfill(2) )
        path = os.path.join(root, date)
         #第一步合并d8的dem文件
        srcfiles1 = ''
        for file in os.listdir(path):
            # filename = 'HDF4_EOS:EOS_GRID:"/mnt/mfs31/RUSLE_C/ndvi/2015/2015.01.01/MOD13A3.A2015001.h21v03.006.2015295115824.hdf":MOD_Grid_monthly_1km_VI:"1 km monthly NDVI" '
            srcfiles1 = srcfiles1 + 'HDF4_EOS:EOS_GRID:"'+os.path.join(path, file)+'":MOD_Grid_monthly_1km_VI:"1 km monthly NDVI" '
            srcfiles1 = srcfiles1+' '
        cmd = 'gdalwarp  %s %s/MOD13A3_A%s%s_1kmMonthNDVI.tif' % (srcfiles1, root, str(year), str(data).zfill(2) )
        os.system(cmd)
        return cmd
        

    '''
    入口函数
    '''

    def __call__(self, data, **kwargs):
        return self.doit(data, **kwargs)

if __name__ == '__main__':
    # 建议使用 Client 类进行操作
    client = dboxmr.Client("10.0.82.52:6600")

    params1 = deepcopy(params)
    print(params1)
    result = client.mapreduce(
        params1,
        m_map_class, 
        m_reduce_func,
        map_kwargs=map_kwargs,
        # remove_lasy=True,
        title="test_basic_map",
        # timeout=600,
        timeout=120,
        priority=0,
        # favor_nodes=["group0"],
        # allow_other_nodes=False,
        reduce_kwargs=reduce_kwargs)
    print("test_basic:", result.results)
