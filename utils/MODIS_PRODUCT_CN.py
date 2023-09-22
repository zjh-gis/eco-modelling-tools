'''
Created on Jan 27, 2015

@author: root
'''

import tempfile, sys, re
import os, subprocess

def run(cmd):
    print "\n", cmd
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

cutline = "/mnt/gscloud/MODIS_PRODUCT_CN/apps/chinaboundry/china_4326.shp"
te = 73.4, 3.8, 134.8, 53.6

hh = range(23, 30)
vv = range(3 , 8)


def main(root_file, out_path, prod_level):
    tmpfolder = tempfile.mkdtemp(dir="/dev/shm")
    try:
        root_dir = os.path.dirname(root_file)
        root_date = os.path.basename(root_dir).replace(".", "")

        out_path = os.path.join(out_path, root_date[:4])
        
        print out_path
        
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        #                            MODND1D.20001231.CN.NDVI.V1.TIF

        # dst_files = os.path.join(out_path, "%s.%s.CN.NDVI.V2.TIF" % (prod_level, root_date,))
        dst_files = [
                     os.path.join(out_path, "%s.%s.CN.NDVI.V2.TIF" % (prod_level, root_date)),
                     os.path.join(out_path, "%s.%s.CN.QC.V2.TIF" % (prod_level, root_date))
                     ]

        if os.path.exists(dst_files[0]):
            print "file exists, ", dst_files[0]
            return

        cmds_comb = ["gdalwarp -t_srs EPSG:4326 -of HFA -tap -te", " ".join(map(str, te)) , "-tr 0.0059 0.0059 -dstnodata 0 -cutline", cutline ]
        hdffiles = filter(lambda a: a.endswith(".hdf"), os.listdir(root_dir))

        myhdffiles = []
        for filename in hdffiles:
            h, v = re.findall("h(\d+)v(\d+)", filename)[0]

            h = int(h)
            v = int(v)

            if h in hh and v in vv:
#                print "Not in China"
                myhdffiles.append(filename)

        hdffiles = myhdffiles

        print len(hdffiles), "files"
        if len(hdffiles) < 20:
            return
        else:

        # HDF4_EOS:EOS_GRID:"/mnt/gscloud/modis_land/data/MOLT/MOD09GA.005/2008/2008.02.28/MOD09GA.A2008059.h25v05.005.hdf":MODIS_Grid_500m_2D:sur_refl_b01_1

            def do_one(bandid):
                def _f0(afile):
                    return 'HDF4_EOS:EOS_GRID:"%s":MODIS_Grid_500m_2D:sur_refl_%s_1' % (os.path.join(root_dir, afile), bandid)  # b01
                # HDF4_EOS:EOS_GRID:"MOD09GA.A2016046.h24v03.005.hdf":MODIS_Grid_500m_2D:sur_refl_b01_1
                gfiles = map(_f0 , hdffiles)
                run_cmds = cmds_comb + gfiles
                ndvicn_file = os.path.join(tmpfolder, "ndvi_%s.img" % (bandid,))
                run_cmds.append(ndvicn_file)
                str_cmds = " ".join(run_cmds)
                run(str_cmds)

                return ndvicn_file

            b01 = do_one("b01")
            b02 = do_one("b02")

            # "gdalformula -expr "trunc( (band2-band1) / (band2+band1)  , -1, 1 )" -dstfile /dev/shm/o.img --band1=/dev/shm/tmpUGtBo_/ndvi_b01.img --band2=/dev/shm/tmpUGtBo_/ndvi_b02.img -ot Float3
            # ndvi_cmds = 'gdalformula -expr "trunc( avg( %s ) * 0.02 - 273.15, -1, 1 )" -dstfile %s -stat %s -ot Float32 -co COMPRESS=LZW'
            ndvi_file = os.path.join(tmpfolder, "ndvi.img")
            cmds = 'gdalformula -expr " or(((band2-band1) / (band2+band1)) <= -1, ((band2-band1) / (band2+band1)) >= 1) ? nodata: ( (band2-band1) / (band2+band1) ) " -co COMPRESS=LZW -stat -ot Float32 -dstfile %s --band1=%s --band2=%s' % (ndvi_file, b01, b02)
            
            run(cmds)
            # for i in range(4):
            # or(((band2-band1) / (band2+band1)) <= -1, ((band2-band1) / (band2+band1)) >= 1) ? nodata: ( (band2-band1) / (band2+band1) )

 
            def do_qc(afile):
                return 'HDF4_EOS:EOS_GRID:"%s":MODIS_Grid_500m_2D:QC_500m_1' % (os.path.join(root_dir, afile))
            gfiles = map(do_qc , hdffiles)
            run_cmds = cmds_comb + gfiles
            qc_file = os.path.join(tmpfolder, "qc.img")
            run_cmds.append(qc_file)
            str_cmds = " ".join(run_cmds)
            run(str_cmds)

            cmds = "gdal_translate -of GTiff -co 'COMPRESS=LZW' %s %s " % (ndvi_file, dst_files[0])
            run(cmds)
            cmds = "gdal_translate -of GTiff -co 'COMPRESS=LZW' %s %s " % (qc_file, dst_files[1]) 
            run(cmds)
            #for i in range(2):
            #    if os.path.exists(dst_files[i]):
            #        os.unlink(dst_files[i])

                #cmds = "gdal_translate -of GTiff -co 'COMPRESS=LZW' %s %s" % (out_files[i], dst_files[i])
                #run(cmds)

            # MODLT1D.20110622.CN.LTN.V1.TIF

    finally:
        run("rm -rf %s " % (tmpfolder ,))
        pass

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print sys.argv[0], "<a MOD09GA hdf file>"
        sys.exit(0)
    root_file = sys.argv[1]

#    root_file = "/mnt/gscloud/modis_land/data/MOLT/MOD09GA.005/2008/2008.02.28/MOD09GA.A2008059.h25v05.005.hdf"
#     root_file = "/mnt/gscloud/modis_land/data/MOLT/MOD11A1.005/2015/2015.01.05/MOD11A1.A2015005.h25v05.005.hdf"

    out_path = "/mnt/gscloud/MODIS_PRODUCT_CN/data/NDVI_V2"
    prod_level = "MODND1D"

    out_path = os.path.join(out_path, prod_level)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    print "root_file", root_file
    print "out_path", out_path
    main(root_file, out_path, prod_level)

