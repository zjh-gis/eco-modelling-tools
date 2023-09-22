#!/usr/bin/env python
# -*- coding: utf-8 -*
'''
Created on Feb 6, 2017
@author: zjh
效率提高指出:预先将图像进行thumbtail处理
分布式比较各个图像,其中当前和同一时期的相似性更大,设定优先级
排序时使用mapreduce
还可以综合多种similar比较方法的相似度值,取最终的平均值
不同的similar计算方法也可以并行进行计算
'''
from PIL import Image
from numpy import average, linalg, dot
import os

def get_thumbnail(image, size=(128,128), greyscale=False):
    #get a smaller version of the image - makes comparison much faster/easier
    image = image.resize(size, Image.ANTIALIAS)
    if greyscale:
     #convert image to greyscale
        image = image.convert('L')
    return image

'''
待补充的方法:aHash (also called Average Hash or Mean Hash). This approach crushes the image into a grayscale 8x8 image and sets the 64 bits in the hash based on whether the pixel's value is greater than the average color for the image.
pHash (also called "Perceptive Hash"). This algorithm is similar to aHash but use a discrete cosine transform (DCT) and compares based on frequencies rather than color values.
source: https://github.com/tistaharahap/images-dhash/blob/master/dhash/dhash.py
'''

#余弦相似度
def image_similarity_vectors_via_numpy(filepath1, filepath2):
# source: http://www.syntacticbayleaves.com/2008/12/03/determining-image-similarity/
    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)
        
    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)

    images = [image1, image2]
    vectors = []
    norms = []
    for image in images:
         vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
            vectors.append(vector)
            norms.append(linalg.norm(vector, 2))
        a, b = vectors
        a_norm, b_norm = norms

    # If we did not resize the images to be equal, we would get an error here
     # ValueError: matrices are not aligned
    res = dot(a / a_norm, b / b_norm)#余弦值
    return res

#直方图
def image_similarity_histogram_via_pil(filepath1, filepath2):
#source: https://github.com/petermat/image_similarity/blob/master/image_similarity.py
    import math
    import operator
    from functools import reduce

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)
    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)

    h1 = image1.histogram()
    h2 = image2.histogram()

    rms = math.sqrt(reduce(operator.add,  list(map(lambda a,b: (a-b)**2, h1, h2)))/len(h1) )
    return rms

#汉明距离比较对应位置上不同值的个数,多用于字符串,在图片比较中权重应比其他方法小
def image_similarity_greyscale_hash_code(filepath1, filepath2):
    # source: http://blog.safariflow.com/2013/11/26/image-hashing-with-python/

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    image1 = get_thumbnail(image1, greyscale=True)
    image2 = get_thumbnail(image2, greyscale=True)

    code1 = image_pixel_hash_code(image1)
    code2 = image_pixel_hash_code(image2)
    # use hamming distance to compare hashes
    res = hamming_distance(code1,code2)
    return res

def hamming_distance(s1, s2):
    len1, len2= len(s1),len(s2)
    if len1!=len2:
    #  "hamming distance works only for string of the same length, so i'll chop the longest sequence"
        if len1>len2:
            s1=s1[:-(len1-len2)]
        else:
            s2=s2[:-(len2-len1)]
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])

if __name__ == '__main__':
    image0_path = "/root/workspace/dataservice/imagesimilarity/data/20161231-1303_ch1_lbt.fy2.bmp"
    data_path = "/root/workspace/dataservice/imagesimilarity/data/"
    files = os.listdir(data_path)
    sim = []
    for i in range(len(files)):
        image1_path = data_path + files[i]
        sim.append((image_similarity_vectors_via_numpy(image0_path, image1_path),image1_path))
        sim.sort()
    for j in range(len(sim)):
        print( 'the image is: %s and the similarity is: %s')%(sim[j][1],sim[j][0])
    max_sim = sim[len(sim)-1][0]   
    max_sim_image = sim[len(sim)-1][1]
    print( 'the most similar image is: %s and the similarity is: %s')%(max_sim_image,max_sim)


