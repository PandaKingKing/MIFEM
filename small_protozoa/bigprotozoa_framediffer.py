import logging
import os
import json
import time
import torch
import cv2
import numpy as np

# from blur_demo import calculate_blur_score

# 配置日志记录
logging.basicConfig(level=logging.INFO, filename='log/app_record.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Bp_frame:
    OFFSET = 5
    iou_thresh = 0.8
    area_thresh = 0.1
    edge_thresh = 0.2

    def __init__(self):
        self.record = {}  # 记录对应track_id大虫子检测框内的小虫子数量
        # self.cls = {}
        self.cls = {
            'Gs': {},
            'Mo': {},
            'Do': {},
            'Eu': {},
            'Ne': {},
            'Ar': {}
        }
        self.cls1 = {
            'Gs': {},
            'Mo': {},
            'Do': {},
            'Eu': {},
            'Ne': {},
            'Ar': {}
        }
        self.blur = {}  # 记录被检测总帧数以及对应帧大虫子的模糊度_2024.2.28
        self.file_path = None  # 活性json文件
        self.blur_path = None  # 模糊度json文件
        self.pre_outputs = torch.empty((0, 5))  # 记录上一帧轮虫输出结果
        self.cur_outputs = torch.empty((0, 5))  # 记录当前帧轮虫输出结果
        self.frame_index = None  # 记录上一帧索引

    def bp_frame_differ(self, frame_index, messages, outputs, others, frame):
        """
        统计大虫子边界框内小虫子的数量
        :param messege 小虫子中心点坐标,面积
        :param outputs 边界框坐标,大虫子id
        :param others 大虫子类别
        :param frame 图像
        """
        filter_path = r'.\output'
        txt_path = r'.\output\record_1.txt'
        local_time = time.localtime()
        dirname = f'{local_time.tm_year}-{local_time.tm_mon}-{local_time.tm_mday}'
        root_path = os.path.join(filter_path, dirname)
        file_path = self.search_path(root_path, txt_path)
        # file_name = os.path.basename(file_name) + '_activity.json'
        # blur_file = os.path.basename(file_name) +'_blur_frame.json'
        # file_name = 'activity.json'
        # blur_file = 'blur_frame.json'
        if file_path:
            file_name = os.path.basename(file_path) + '_activity.json'
            blur_file = os.path.basename(file_path) + '_blur_frame.json'
            self.file_path = os.path.join(file_path, file_name)
            self.blur_path = os.path.join(file_path, blur_file)

        for message in messages:
            if message:
                x, y, small_area = message[0], message[1], message[2]
            else:
                x, y = -1, -1
            self.inside(x, y, small_area, outputs, others)

        # if self.frame_index:
        #     pass
        # else:
        #     self.frame_index = frame_index 

        # 2024.2.28
        self.blur_record(outputs, others, frame_index, frame)

        self.pre_outputs = self.cur_outputs
        self.cur_outputs = outputs

        self.area_rate(self.pre_outputs, self.cur_outputs)
        # self.frame_index = frame_index

        if self.file_path:
            with open(self.file_path, 'w') as file:
                json.dump(self.cls, file, indent=4)

        if self.blur_path:
            with open(self.blur_path, 'w') as file1:
                json.dump(self.cls1, file1, indent=4)

    # 2024.2.28
    def blur_record(self, outputs, others, frame_index, frame):
        """
        记录被检测总帧数以及对应帧大虫子的模糊度
        :param outputs 大虫子输出结果
        :param others 大虫子类别
        :param frame_index 当前帧索引
        """
        type_mapping = {
            'Gs': 0,
            'Mo': 1,
            'Do': 2,
            'Eu': 3,
            'Ne': 4,
            'Ar': 5
        }
        blur_score = 0
        cls_list = [other.cls for other in others]
        for output, other in zip(outputs, cls_list):
            x1, y1, x2, y2, track_id = output.tolist()

            blur_score = self.calculate_blur_score(frame, x1, y1, x2, y2)

            # 初始化以及记录检测帧数
            if track_id in self.blur and "total_frame" in self.blur[track_id]:
                self.blur[track_id]["total_frame"] += 1
            else:
                self.blur[track_id] = {"total_frame": 1}

                # ln 2024.3.12 活性平均计数
                self.blur[track_id]["average_activity"] = -1

            self.blur[track_id][frame_index] = blur_score

            cls = [key for key, values in type_mapping.items() if values == int(other)]
            for key in cls:
                if key in self.cls:
                    self.cls1[key][track_id] = self.blur[track_id]
                    # print("1", self.cls1[key][track_id]["average_activity"])
                    if track_id in self.cls[key]:
                        self.cls1[key][track_id]["average_activity"] = \
                            (self.cls[key][track_id]["total_activity"] * 10) / self.blur[track_id]["total_frame"]
                else:
                    self.cls1[key] = {track_id: self.blur[track_id]}

    def _detect_blur_fft(self, image, size=60):
        """
        计算模糊度
        :param image: 图像
        :return: (模糊度值, 是否模糊)
        """
        h, w = image.shape[:2]
        (cX, cY) = (int(w / 2.0), int(h / 2.0))

        fft = np.fft.fft2(image)
        fft_shift = np.fft.fftshift(fft)

        fft_shift[cY - size:cY + size, cX - size:cX + size] = 0
        fft_shift = np.fft.ifftshift(fft_shift)
        recon = np.fft.ifft2(fft_shift)

        magnitude = 20 * np.log(np.abs(recon))
        mean = np.mean(magnitude)

        return mean

    def calculate_blur_score(self, image, x, y, x1, y1):
        # 提取矩形框内的区域
        roi = image[y:y1, x:x1]
        # 转换为灰度图像
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # 计算模糊度值
        mean = self._detect_blur_fft(gray_roi)

        return mean

    def inside(self, x, y, area, outputs, others):
        """
        记录轮虫内小虫子个数
        :param x 待检测点横坐标
        :param y 待检测点纵坐标
        :param small_area 小虫子面积
        :return:
        """
        type_mapping = {
            'Gs': 0,
            'Mo': 1,
            'Do': 2,
            'Eu': 3,
            'Ne': 4,
            'Ar': 5
        }
        cls_list = [other.cls for other in others]
        for output, other in zip(outputs, cls_list):
            logging.info(f'大虫子：{output}, {int(other)}')
            x1, y1, x2, y2, track_id = output.tolist()
            if track_id not in self.record:
                self.record[track_id] = {}
            if "total_activity" not in self.record[track_id]:
                self.record[track_id]["total_activity"] = 0
                self.record[track_id]["small_area"] = []
            if x1 - self.OFFSET <= x <= x2 + self.OFFSET and y1 - self.OFFSET <= y <= y2 + self.OFFSET:
                if track_id in self.record:
                    self.record[track_id]["total_activity"] += 1
                    self.record[track_id]["small_area"].append(area)

                # else:
                #     self.record[track_id] = 1
                # cls = [key for key, values in type_mapping.items() if values == int(other.cls)]
                # self.cls.update({key: self.record for key in cls})

            cls = [key for key, values in type_mapping.items() if values == int(other)]
            for key in cls:
                if key in self.cls:
                    self.cls[key][track_id] = self.record[track_id]
                else:
                    self.cls[key] = {track_id: self.record[track_id]}
                logging.info(f'字典{self.cls}')

    def is_same(self, pre_frame, cur_frame):
        """
        根据上一帧与当前帧的iou判断轮虫运动形式
        :param pre_frame 前一帧轮虫输出结果
        :param cur_frame 当前帧轮虫输出结果 
        """
        for output2 in cur_frame:
            for output1 in pre_frame:
                x1, y1, x2, y2, track_id1 = output1.tolist()
                x3, y3, x4, y4, track_id2 = output2.tolist()
                if track_id1 == track_id1:
                    # print("task_id1", track_id1)
                    inter_area = max(0, min(x2, x4) - max(x1, x3)) * max(0, min(y2, y4) - max(y1, y3))
                    # 计算并集面积
                    box1_area = (x2 - x1) * (y2 - y1)
                    box2_area = (x4 - x3) * (y4 - y3)
                    union_area = box1_area + box2_area - inter_area
                    # 计算重叠面积比例
                    iou = inter_area / union_area
                    # print("task_id2", track_id2, iou, iou < self.iou_thresh)
                    if iou < self.iou_thresh:
                        # print("task_id2", track_id2, iou)
                        if track_id2 not in self.record:
                            self.record[track_id2]["total_activity"] = 0
                            self.record[track_id2]["small_area"] = []
                        # print("1111", self.record[track_id2])

                        self.record[track_id2]["total_activity"] += 10
                        # print("2222", self.record[track_id2])

    def area_rate(self, pre_frame, cur_frame):
        """
        判断当前帧轮虫面积变化率
        :param pre_frame 前一帧轮虫输出结果
        :param cur_frame 当前帧轮虫输出结果 
        """
        for output2 in cur_frame:
            for output1 in pre_frame:
                x1, y1, x2, y2, track_id1 = output1.tolist()
                x3, y3, x4, y4, track_id2 = output2.tolist()
                if (x1 + y1) != 0 and (x2 + y2) != 0 and (x3 + y3) != 0 and (x4 + y4) != 0 and \
                        track_id1 == track_id2:
                    # print("task_id1", track_id1)
                    # 计算并集面积
                    box1_area = (x2 - x1) * (y2 - y1)
                    box2_area = (x4 - x3) * (y4 - y3)
                    area_diff = abs(box2_area - box1_area)
                    # 计算面积变化率
                    rate = area_diff / box2_area

                    # print("面积变化率", track_id2, rate, box1_area, box2_area)
                    if rate > self.area_thresh:
                        # print("task_id2", track_id2, iou)
                        if track_id2 not in self.record:
                            self.record[track_id2] = {}
                            self.record[track_id2]["total_activity"] = 0
                            self.record[track_id2]["small_area"] = []
                        # logging.info(f"当前帧{self.record[track_id2]}")
                        if track_id2 in self.cls['Mo'] or track_id2 in self.cls['Do']:
                            # ln 2024.3.18 根据面积面积变化率加权计算活性 
                            if rate < 0.5:
                                self.record[track_id2]["total_activity"] += (rate * 50)
                            else:
                                self.record[track_id2]["total_activity"] += 25

    def search_path(self, root_folder, txt_file):
        # 检查txt文件是否存在，如果不存在则创建一个新的txt文件
        if not os.path.exists(txt_file):
            with open(txt_file, 'w') as f:
                pass

        with open(txt_file, 'r') as f:
            traversed_folders = f.read().splitlines()

        for folder_name in os.listdir(root_folder):
            folder_path = os.path.join(root_folder, folder_name)

            if folder_path in traversed_folders:
                continue

            if os.path.isdir(folder_path):
                images_folder = os.path.join(folder_path, 'images')

                if os.path.exists(images_folder) and images_folder not in traversed_folders and len(
                        os.listdir(images_folder)) > 0:
                    parent_folder = os.path.dirname(images_folder)
                    with open(txt_file, 'a') as f:
                        f.write(images_folder + '\n')
                    return parent_folder
