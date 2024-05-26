import cv2
import numpy as np
import os
import csv
from pathlib import Path
from cal_area import cal_area


path = 'C:\\Users\\Zheng Pang\\Desktop\\model3\\yolov5\\test_image'
pic_list = os.listdir(path)
with open("area_res.csv", 'w', encoding="UTF8", newline="") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(["image name", "rate of the target area"])
    for pic in pic_list:
        img = cv2.imread(path + pic)
        rate = cal_area(img)
        csv_writer.writerow([pic, rate])
        print(pic + "---Done!\n")
