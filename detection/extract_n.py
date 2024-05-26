import numpy as np
import os
import random
import shutil

from extract import xml2im, xml_stat, prepare_data

wd = 'E:/dataset/trainval/'
xml_path = wd + 'VOC2007/Annotations/'
img_path = wd + 'VOC2007/JPEGImages/'
filenames = os.listdir(xml_path)
total = len(filenames)
num_objs = xml_stat(xml_path, filenames)
nc = len(num_objs)
print(f'Total number of images: {total}')
for k in num_objs.keys():
    print(f'{k}:{num_objs[k]}个')
print('-------------------------------\n')

for i in range(1, 5):
    n = int(total * i / 5)
    print(f'Number of extracted images: {n}')
    th_arr = i / 6 * np.array(list(num_objs.values()))
    print(f'Threshold of each class: {th_arr.tolist()}')

    wd_n = wd + f'Extract_{n}/'
    if not os.path.exists(wd_n):
        os.mkdir(wd_n)
    else:
        print('Directory has already existed!')
        print('-------------------------------\n')
        continue

    if not os.path.exists(wd_n + 'VOC2007/'):
        os.mkdir(wd_n + 'VOC2007/')

    new_xml_path = wd_n + 'VOC2007/Annotations/'
    if not os.path.exists(new_xml_path):
        os.mkdir(new_xml_path)

    new_img_path = wd_n + 'VOC2007/JPEGImages/'
    if not os.path.exists(new_img_path):
        os.mkdir(new_img_path)

    while True:
        file_n = random.sample(filenames, n)
        # print(len(file_n)); break
        num_objs_n = xml_stat(xml_path, file_n)
        num_arr = np.array(list(num_objs_n.values()))
        # print(num_arr); break
        if len(num_objs_n) < nc:
            continue
        if (num_arr > th_arr).all():
            print('Result of Extracted Images:')
            for k in num_objs_n.keys():
                print(f'{k}:{num_objs_n[k]}个')

            print('Start copying the images and xmls to target directory...')
            for f in file_n:
                shutil.copy(xml_path + f, new_xml_path + f)
            xml2im(img_path, new_xml_path, new_img_path)
            print('Copying finished')
            break

    print('Start generating Labels for YOLO...')
    prepare_data(wd_n)
    print('Generating finished')
    print('-------------------------------\n')