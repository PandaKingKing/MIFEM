import numpy as np
import sys
from pathlib import Path
import torch
import json
import os
import logging

torch.backends.cudnn.enabled = False
root = Path(__file__).parent
sys.path.append(str(root))
from yolov5.utils.augmentations import letterbox
from yolov5.utils.general import non_max_suppression
from DeepSORT.deepsort import DeepSORT
from clustering import merge_prediction_box

yolo_path = str(root / 'yolov5')
conf_path = str(root / 'conf_config.json')
sys.path.append(yolo_path)


# logging.basicConfig(level=logging.INFO, filename='log/app_record.log', filemode='a',
#                     format='%(asctime)s - %(levelname)s - %(message)s')

class YoloDetector:
    """
    yolo 检测器 + 追踪
    """

    # yolo 配置
    BASE_CONF_THRESHOLD = 0.25  # 基础置信度
    IOU_THRESHOLD = 0.45
    CLASSES = None
    AGNOSTIC_NMS = False
    MAX_DET = 1000

    def __init__(self):
        """
        建立追踪对象
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.detector = torch.load(r'.\yolo_detect\weights\best5.pt', map_location=self.device)['model'].float()
        self.detector.to(self.device).eval()
        self.conf_dict = None
        self._init_config(conf_path)
        self.half = self.device.type != 'cpu'
        if self.half:
            self.detector.half()
        self.deepsort = DeepSORT()

    def _init_config(self, config_path=None):
        """
        初始化置信度配置文件
        :param config_path: 置信度配置文件路径
        :return:
        """
        with open(config_path, 'r') as f:
            json_data = json.loads(f.read())
            self.conf_dict = json_data

    # 调用函数保存预测框信息到指定文件夹

    @torch.no_grad()
    def detect(self, frame_index, frame):
        """
        yolo检测
        :param frame_index: 帧数
        :param frame: 待检测的图片
        :return: 预测框信息, 其他信息(微生物类别,数量)
        """
        img = self._numpy2tensor(frame)
        pred = self.detector(img)[0]
        # Apply NMS and filter object other than person (cls:0)
        pred = non_max_suppression(pred, self.BASE_CONF_THRESHOLD, self.IOU_THRESHOLD, classes=self.CLASSES,
                                   agnostic=self.AGNOSTIC_NMS, max_det=self.MAX_DET)

        det = self._conf_filter(pred[0])
        det, bug_nums = merge_prediction_box(det, 0)  # 对Gs 进行聚类（0代表GS的类别）
        outputs, others = self.deepsort.image_track(det, bug_nums, frame, img.shape[2:], frame.shape,
                                                    frame_index)  # 对预测结果进行追踪
        cls_list = [other.cls for other in others]
        logging.info(f'yolo检测:{outputs}, {cls_list}')
        return frame_index, outputs, others

    def _conf_filter(self, detection):
        """
        置信度过滤
        :param detection: 待过滤的检测框
        :return: 过滤完成的检测框
        """

        filter_list = []
        # print("self.detector.names:", self.detector.names)
        self.detector.names = {0: 'Gs', 1: 'Mo', 2: 'Do', 3: 'Eu', 4: 'Ne', 5: 'Ar'}
        for cls, key in self.detector.names.items():
            if self.conf_dict is None:
                conf = 0.25
            else:
                conf = self.conf_dict[key]
            index = (detection[:, 5] == cls) * (detection[:, 4] >= conf)
            filter_list.append(detection[index])
        result = torch.cat(filter_list)
        return result

    def _numpy2tensor(self, frame, img_size=640):
        """
        numpy to tensor
        :param frame: numpy格式的图片
        :param img_size: 转换后图片的大小
        :return: 装换后的图片
        """
        img = letterbox(frame, new_shape=img_size)[0]
        # Convert
        img = np.ascontiguousarray(img[:, :, ::-1].transpose(2, 0, 1))
        # numpy to tensor
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        return img
