# 对指定路径下的所有目录，每个目录下分别进行图片批处理（去模糊）
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
import csv

from deblur import image_pre

# 以下参数需要学长自行斟酌修改
vis = False  # 是否可视化
save = True  # 是否写入图片
crop = 0.12  # 裁去边框的比例
# img_dict = {'class': ['BN', 'Cr', 'Cu', 'OH', 'H'],
#             'blur_th': [14.2] * 4 + [-15.44],
#             'std_th': [25.52] * 4 + [9.7]}
img_dict = {'class': ['others', 'H'],
            'blur_th': [14.2, -15.44],
            'std_th': [25.52, 9.7]}

for i in range(len(img_dict['class'])):
    work_dir = "F:/code_pz/images/" + img_dict['class'][i] + "/"  # 工作路径
    save_dir = work_dir + "deblur_res/"  # 图片存储路径
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    else:
        print("Directory has already existed!")
        continue
    res_f = open(save_dir + 'pre_res.csv', 'w', encoding="UTF8", newline="")
    csv_writer = csv.writer(res_f)
    csv_writer.writerow(['name', 'save', 'blur', 'std'])
    for dir in os.listdir(work_dir):
        # print(img_dir)
        if os.path.isdir(work_dir + dir) and dir.isnumeric():
            # print('yes')
            img_dir = work_dir + dir + "/"  # + dir + "_image/"
            imgs = os.listdir(img_dir)
            # print(len(imgs))
            # save_dir = save_dir + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + "/"
            # if not os.path.exists(save_dir):
            #     os.mkdir(save_dir)
            for img_name in imgs:
                if img_name.split('.')[-1] in ['jpg', 'png']:  # 支持的图片文件格式
                    print('----------<' + img_dict['class'][i] + '>Image: ' + img_name + '----------')
                    img = cv2.imread(img_dir + img_name)
                    flag, blur, std = image_pre(img, crop, img_dict['blur_th'][i], img_dict['std_th'][i], vis=vis,
                                                save=save, save_path=save_dir + img_name)
                    csv_writer.writerow([img_name, flag, blur, std])
                    print('--------------------\n')
    res_f.close()
