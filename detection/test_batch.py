# 对指定目录下的视频/图片进行批处理（去模糊）
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
import csv
from pathlib import Path

from deblur import image_pre, video_pre

# 以下参数需要自行斟酌修改
work_dir = Path("D:/pz/tcp")  # 视频/文件目录
todo = "video"  # 处理视频或是单个图片
blur_th = -2.0  # 模糊度阈值
std_th = 15.0  # 标准差阈值
vis = True  # 是否可视化
save_img = False  # 是否保存图片
save_csv = False  # 是否保存CSV
save_root = work_dir / "deblur_new"  # 图片存储路径

if todo == "video":
    # 视频处理
    gap = 150  # 抽帧间隔帧数
    for video_path in work_dir.glob('*.mp4'):
        print('----------Video: ' + video_path.name + '----------')
        video_pre(video_path, gap, blur_th, std_th, vis=vis, save_img=save_img, save_csv=save_csv, save_root=save_root)
        print('\n')

elif todo == "image":
    # 单个图片处理
    crop = 0.12  # 裁去边框的比例
    save_dir = save_root / time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    save_dir.mkdir(parents=True, exist_ok=True)
    res_f = (save_dir / 'pre_res.csv').open('w', encoding="UTF8", newline="")
    csv_writer = csv.writer(res_f)
    csv_writer.writerow(['name', 'save', 'blur', 'std'])
    for img_path in work_dir.glob('.jpg'):
        print('----------Image: ' + img_path.name + '----------')
        img = cv2.imread(str(img_path))
        flag, blur, std = image_pre(img, crop, blur_th, std_th, vis=vis, save=save_img, save_path=img_path)
        csv_writer.writerow([img_path.name, flag, blur, std])
        print('\n')
    res_f.close()
else:
    print("Wrong string is got in parameter `todo`\n")
