import numpy as np
import cv2
import math
from .features_match import calc_translation
from copy import deepcopy
from .tracker import Tracker
from .bugs_filter import BBoxFilter


class FrameDifferDetector:    
    NOISY_LIST = [(912, 608, 150), (1132, 718, 50), (800, 80, 50), (510, 1080, 50), (1650, 560, 50), (1400, 1130, 100), (96, 366, 50), (294, 33, 50), (381, 218, 50), (1368, 718, 50), (1518, 905, 50), (1575, 1052, 50), (1666, 487, 50), (1612, 85, 50), (1195, 970, 50), (1378, 670, 50)]  # 屏幕噪点 (x, y, r)

    def __init__(self):

        self.per_frame = None  # 前一帧
        self.tracker = Tracker()  # 管理器
        self.bbox_filter = BBoxFilter()  # 大虫子过滤器

    @staticmethod
    def calc_distance(point1, point2):
        """
        计算两点间距离
        :param point1: 第一个点
        :param point2: 第二个点
        :return: 距离
        """
        distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
        return distance

    @classmethod
    def filter_screen_noisy(cls, center_point):
        """
        过滤屏幕噪点
        :param center_point: 待检测的点
        :return: 过滤后的点
        """

        near_noisy_point = False
        for noisy in cls.NOISY_LIST:
            *noisy_point, distance_threshold = noisy
            distance = cls.calc_distance(center_point, noisy_point)
            if distance <= distance_threshold:
                near_noisy_point = True
                break

        return near_noisy_point

    def cluster(self, location_list, threshold=50):
        """
        散点聚类
        :param location_list:  需要聚类的点的信息
        :param threshold:  聚类距离阈值
        :return:
        """
        result_list = []
        while len(location_list) > 0:
            x1, y1, x2, y2 = location_list.pop()
            left, right, top, bottom = x1, x2, y1, y2
            temp_list = []
            all_points = [(x1, y1, x2, y2)]
            while len(location_list) > 0:
                temp_x1, temp_y1, temp_x2, temp_y2 = location_list.pop()
                temp_center_point = ((temp_x1 + temp_x2) / 2, (temp_y1 + temp_y2) / 2)
                find = False
                for point in all_points:
                    center_point = ((point[0] + point[2]) / 2, (point[1] + point[3]) / 2)
                    distance = self.calc_distance(center_point, temp_center_point)
                    if distance <= threshold:
                        left = min(left, temp_x1)
                        right = max(right, temp_x2)
                        top = min(top, temp_y1)
                        bottom = max(bottom, temp_y2)
                        find = True
                        break
                if not find:
                    temp_list.append((temp_x1, temp_y1, temp_x2, temp_y2))
            location_list = temp_list
            result_list.append((left, top, right, bottom))

        return result_list

    def frame_differ(self, per_frame_gary, frame_gary):
        """
        魔改版帧差法
        :param per_frame_gary: 前一帧
        :param frame_gary: 当前帧
        :return: 可能为运动目标的区域信息
        """

        # 帧差法
        diff = cv2.absdiff(per_frame_gary, frame_gary)
        diff_stat = np.median(diff)

        if diff_stat > 2:
            return []
        diff = cv2.GaussianBlur(diff, (5, 5), 0)

        ret, binary = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

        ksize1, ksize2 = (3, 3)
        kernel1 = np.ones((ksize1, ksize1), np.float64)

        binary = cv2.morphologyEx(binary, cv2.MORPH_ERODE, kernel1)

        kernel2 = np.ones((ksize2, ksize2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel2, iterations=10)

        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) >= 20:
            return []

        # 初步过滤
        location_list = []
        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            x1, y1, x2, y2 = x, y, x + w, y + h
            center_point = ((x1 + x2) / 2, (y1 + y2) / 2)
            area = (x2 - x1) * (y2 - y1)
            if 100 < area < 10000 and not self.filter_screen_noisy(center_point):
                location_list.append((x1, y1, x2, y2))

        # 散点聚类
        if location_list:
            location_list = self.cluster(location_list)

        # 最终结果
        point_list = [(int((location[0] + location[2]) / 2), int((location[1] + location[3]) / 2),
                       (location[2] - location[0]) * (location[3] - location[1])) for location in location_list]

        return point_list

    def detect(self, blurry, frame_index, frame, outputs):
        """
        小虫子检测
        :param blurry: 当前帧是否模糊
        :param frame_index: 帧数
        :param frame: 图像
        :param outputs: 大虫子检测框
        :return: (帧数, 显示图像, 过期点列表, 位移矢量, 当前帧的显示信息)
        """

        # 初始化
        if self.per_frame is None:
            self.per_frame = frame
            frame_height, frame_width, _ = frame.shape
            self.bbox_filter.set_width(frame_width)
            self.bbox_filter.set_height(frame_height)
            self.bbox_filter.update_bbox(outputs)
            return frame_index, frame, [], None, []

        # 模糊帧不检测
        if blurry:
            self.per_frame = frame
            self.bbox_filter.update_bbox(outputs)
            return frame_index, frame, [], None, []

        translation, img1, img2 = calc_translation(self.per_frame, frame)

        # 位移矢量计算有误
        if len(translation) == 0:
            self.per_frame = frame
            self.bbox_filter.update_bbox(outputs)
            return frame_index, frame, [], None, []

        # 帧差法
        message_list = self.frame_differ(img1, img2)

        # 大虫子过滤
        self.bbox_filter.update_bbox(outputs, translation)
        message_list = self.bbox_filter.filter(message_list)

        # 数据更新
        self.tracker.update(frame_index, message_list, translation)

        # 显示处理
        show_image = deepcopy(frame)
        for track in self.tracker.display_tracks():
            track.draw(show_image)

        self.per_frame = frame
        clear_list = self.tracker.clear()

        return frame_index, show_image, clear_list, translation, self.tracker.display_tracks()
