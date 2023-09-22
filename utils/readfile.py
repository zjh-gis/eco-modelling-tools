import csv
import numpy
def read_csv():
    # Load CSV (using python)
    
    filename = 'pima-indians-diabetes.data.csv'
    raw_data = open(filename,'rb')
    reader=csv.reader(raw_data,delimiter=',',quoting=csv.QUOTE_NONE)
    x=list(reader)
    data=numpy.array(x).astype('float')
    print(data.shape)

binfile=open('/mnt/data/eco-center/gutan/sampledata/soillasa.bin','rb')
print(binfile)

def read_nc():
    import netCDF4 as nc
    import numpy as np
    filename = '2017-06-15_2017-06-17.nc' # .nc文件名
    f = nc.Dataset(filename) 
    all_vars = f.variables.keys() #获取所有变量名称
    print(len(all_vars)) #长度为18
    all_vars_info = f.variables.items() #获取所有变量信息
    print(type(all_vars_info)) #输出为： odict_items 。这里将其转化为 list列表
    print(len(all_vars_info)) #长度为18
    all_vars_info = list(all_vars_info) #此时每个变量的信息为其中一个列表

    #step2： 查看.nc文件的单个变量，及该变量的全部信息(维度大小，单位等)
    #我们要查看 ’u‘的信息
    var = 'u'
    var_info = f.variables[var] #获取变量信息
    var_data = f[var][:] #获取变量的数据
    print(var_info)
    print(var_data.shape)
    #很方便转化为array数组
    print(type(var_data)) # .nc文件的变量数组都为Masked array
    var_data = np.array(var_data) #转化为np.array数组
    #step3： 列表形式记录所有变量信息
    ###最直接的办法，获取每个变量的缩写名字，标准名字(long_name),units和shape大小。这样很方便后续操作
    all_vars_name = []
    all_vars_long_name = []
    all_vars_units = []
    all_vars_shape = []
    for key in f.variables.keys():
        all_vars_name.append(key)
        all_vars_long_name.append(f.variables[key].long_name)
        all_vars_units.append(f.variables[key].units)
        all_vars_shape.append(f.variables[key].shape)

    f.close() #关闭文件。如果文件关闭后，再使用f.variabels.items()等操作是行不通的。

    #step1： 创建一个文件
    f_w = nc.Dataset('hecheng.nc','w',format = 'NETCDF4') #创建一个格式为.nc的，名字为 ‘hecheng.nc’的文件
    #step2： 写入一些基本的信息

    #time纬度为12。注意，第2个参数 表示维度，但是必须是 integer整型，也就是只能创建一个基础单一维度信息。
    #如果后面要创建一个变量维度>1，则必须由前面的单一维度组合而来。后面会介绍。
    #确定基础变量的维度信息。相对与坐标系的各个轴(x,y,z)
    f_w.createDimension('time',12)
    f_w.createDimension('level',37)
    f_w.createDimension('lat',161)
    f_w.createDimension('lon',177)
    ##创建变量。参数依次为：‘变量名称’，‘数据类型’，‘基础维度信息’
    f_w.createVariable('time',np.int,('time'))
    f_w.createVariable('level',np.int,('level'))
    f_w.createVariable('lat',np.float32,('lat'))
    f_w.createVariable('lon',np.float32,('lon'))
    #写入变量time的数据。维度必须与定义的一致。
    time = np.array([0,6,12,18,0,6,12,18,0,6,12,18])
    f_w.variables['time'][:] = time
    #新创建一个多维度变量，并写入数据，
    f_w.createVariable( 'u', np.float32, ('time','level','lat','lon'))
    var_data = np.ones(shape=(12,37,161,177), dtype = np.float32)
    f_w.variables[var][:] = var_data

    f_w.close()

import netCDF4 as nc
h08file = os.path.join(config.data_path, 'h08/202007/31/03/NC_H08_20200731_0330_L2CLP010_FLDK.02401_02401.nc')
ds = nc.Dataset(h08file, 'r')
true_arr = ds.variables['CLTYPE'][:].data
y_true = true_arr[200:1101, 100:1101]

# 读取hdf文件
import h5py
fy4afile = os.path.join(config.data_path, 'fy4a/20200731/FY4A-_AGRI--_N_REGC_1047E_L1-_FDI-_MULT_NOM_20200731033000_20200731033417_4000M_V0001.HDF')
filename = fy4afile.split('/')[-1].split('.')[0]
fy = h5py.File(os.path.join('/tmp', '%s_CLT2.hdf' % filename), 'r')
pred_arr = fy['FY4CLT'][()]
y_pred = pred_arr[99:, 300:-99]
# 写入hdf文件
dst_hdf = os.path.join(config.results_path,'%s_CLT.hdf'%filename)
#HDF5的写入：    
f = h5py.File(dst_hdf,'w')   #创建一个h5文件，文件指针是f  
f['FY4CLT'] = pred_arr                 #将数据写入文件的主键'FY4CLT'下面    
f.close() 

from struct import *
import cPickle as pickle
import os

def mpfread(folderpath):
    # read mpf file, eg, filepath = '/root/workspace/dataservice/olhwb/dataset/OLHWDB1.1trn/1001.mpf'
    # return array containing label and vector
    files_name = os.listdir(folderpath)
    files_num = len(files_name)
    sample = []
    print "folder name",folderpath
    
    for num in range(files_num):
        if folderpath.endswith('/'):
            filepath = folderpath + files_name[numi]   
        else:
            filepath = folderpath + '/' + files_name[num]
        print "the current file is:" , filepath
        f = open(filepath,'rb')
            
        # read header file
        header_size, = unpack('i', f.read(4))
        format_code, = unpack('8s', f.read(8))
        llustr_size = header_size - 62
        illustration_text, = unpack('%ss'% llustr_size, f.read(llustr_size))
        code_type, = unpack('20s', f.read(20))
        code_length, = unpack('h', f.read(2))
        data_type, = unpack('20s', f.read(20))
        sample_num, = unpack('i', f.read(4))
        dim, = unpack('i', f.read(4))
        
        print "the header file has been read"
        # read Sample Records        
        for i in range(sample_num):
            label, = unpack('%ss'% code_length, f.read(code_length))
            if label[0]=='F' and label[1]=='F':
                continue
            vector = []
            for j in range(dim):
                element, = unpack('b', f.read(1))
                vector.append(element)
            if label == '\xb3\xb9' or label == '\xd5\xba':
                sample.append({'label':label, 'vector':vector})
        print num
    
    return sample
#     # save training data in sample.txt in ascii code
    with open(folderpath+'sample.txt', 'w') as fp:
        pickle.dump(sample, fp)

#if __name__ == '__main__':
    #read training data
#     mpfread("/root/workspace/dataservice/olhwb/dataset/OLHWDB1.1tst")
    
    # read testing data
    #mpfread('/root/workspace/dataservice/olhwb/dataset/OLHWDB1.1trn')

    