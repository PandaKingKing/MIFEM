import cv2
import math
import numpy as np
from copy import deepcopy


class Ellipse:
    """
    椭圆（Ar的拟合形状）
    """

    def __init__(self, center_x, center_y, a, b):
        """

        :param center_x: 图像中的中心点横坐标
        :param center_y: 图像中的中心点纵坐标
        :param a: x坐标轴上的轴长
        :param b: y坐标轴上的轴长
        """
        self.center_x = center_x
        self.center_y = center_y
        self.a = a
        self.b = b

    def in_elliptic(self, x, y):
        """
        判断点是否在椭圆内
        :param x: 横坐标
        :param y: 纵坐标
        :return: 是否在椭圆内(True：在，False：不在)
        """
        inside = False

        real_x = self.center_x - x
        real_y = y - self.center_y
        try:
            pred_y = math.sqrt((1 - ((real_x ** 2) / (self.a ** 2))) * (self.b ** 2))
        except:
            pred_y = -1
        if abs(real_y) <= pred_y:
            inside = True

        return inside

    def is_bounder(self, x, y):
        """
        判断点是否在椭圆边界上
        :param x: 待判断点横坐标
        :param y: 待判断点纵坐标
        :return: 是否在椭圆边界内(True：在，False：不在)
        """
        real_x = self.center_x - x
        real_y = y - self.center_y

        bounder = False

        try:
            pred_y = math.sqrt((1 - ((real_x ** 2) / (self.a ** 2))) * (self.b ** 2))
        except:
            return bounder
        if pred_y - 1.5 <= abs(real_y) <= pred_y + 1.5:
            bounder = True

        return bounder

    def area(self):
        """
        椭圆面积接口
        :return: 椭圆面积
        """
        elliptic_area = math.pi * self.a * self.b
        return elliptic_area


def bound_dfs(image, point_list, ellipse):
    """
    图像生成
    :param image: Ar截图
    :param point_list: 边界点列表
    :param ellipse: Ar区域
    :return:
    """
    temp = deepcopy(image)
    rows = len(image)
    cols = len(image[0])
    for point in point_list:
        stack = [point]
        while stack:
            cur_i, cur_j = stack.pop(0)
            if cur_i < 0 or cur_j < 0 or cur_i == rows or cur_j == cols:
                continue
            if temp[cur_i][cur_j] != 0:
                continue

            if ellipse.in_elliptic(cur_j, cur_i):
                temp[cur_i][cur_j] = 1
                for offset_i, offset_j in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                    next_i, next_j = cur_i + offset_i, cur_j + offset_j
                    stack.append((next_i, next_j))

    for row in range(rows):
        for col in range(cols):
            if ellipse.in_elliptic(col, row) and temp[row][col] == 0:
                image[row][col] = 255


def dfs(matrix, image):
    """
    计算缺陷度
    :param matrix: 映射矩阵
    :param image: 图像
    :return: (Ar缺陷度,Ar缺陷度图像,Ar面积)
    """
    imGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows = len(matrix)
    cols = len(matrix[0])

    max_area, box_location = 0, [0, 0, 0, 0]
    for row in range(rows):
        for col in range(cols):
            if matrix[row][col] != 1:
                continue
            location = [float('inf'), float('inf'), -1, -1]
            stack = [(row, col)]
            cur = 0
            while stack:
                cur_i, cur_j = stack.pop()
                if cur_i < 0 or cur_j < 0 or cur_i == rows or cur_j == cols or matrix[cur_i][cur_j] != 1:
                    continue
                cur += 1
                if cur_i < location[0]:
                    location[0] = cur_i
                if cur_i > location[2]:
                    location[2] = cur_i
                if cur_j < location[1]:
                    location[1] = cur_j
                if cur_j > location[3]:
                    location[3] = cur_j
                matrix[cur_i][cur_j] = 0
                for offset_i, offset_j in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                    next_i, next_j = cur_i + offset_i, cur_j + offset_j
                    stack.append((next_i, next_j))
            if cur > max_area:
                max_area = cur
                box_location = location
    center_x = (box_location[3] + box_location[1]) // 2
    center_y = (box_location[2] + box_location[0]) // 2
    cv2.rectangle(image, (box_location[1], box_location[0]), (box_location[3], box_location[2]), (0, 255, 0), 2)
    cv2.ellipse(image, (center_x, center_y),
                (int(box_location[3] - box_location[1]) // 2, int(box_location[2] - box_location[0]) // 2), 0, 0, 360,
                (0, 0, 255), 2)

    ellipse = Ellipse(center_x, center_y, int(box_location[3] - box_location[1]) // 2,
                      int(box_location[2] - box_location[0]) // 2)
    point_list = []
    for i in range(imGray.shape[0]):
        for j in range(imGray.shape[1]):
            if ellipse.in_elliptic(j, i):
                if ellipse.is_bounder(j, i):
                    point_list.append((i, j))
            else:
                imGray[i][j] = 0

    bound_dfs(imGray, point_list, ellipse)
    k_size = 3
    kernel1 = np.ones((k_size, k_size), np.float64)
    binary = cv2.morphologyEx(imGray, cv2.MORPH_ERODE, kernel1)
    ar_area = np.sum(binary) / 255
    ellipse_area = ellipse.area()
    area_percent = round(1 - ar_area / ellipse_area, 2)
    return area_percent, binary, ar_area


def flaw(image, bad_percent, channels):
    """
    计算缺陷度
    :param image: 图像
    :param bad_percent: 缺陷度百分比
    :param channels: 图像通道阈值
    :return: (缺陷度百分比, 缺陷度图像, 是否缺陷, Ar面积)
    """
    image_channel_one = image[:, :, 0]
    image_chanel_two = image[:, :, 1]
    image_chanel_three = image[:, :, 2]
    area_matrix = []
    for i in range(image_channel_one.shape[0]):
        matrix_row = []
        for j in range(image_channel_one.shape[1]):
            if image_channel_one[i][j] < channels[0] and image_chanel_two[i][j] < channels[1] and \
                    image_chanel_three[i][j] < channels[2]:
                matrix_row.append(1)
                image_channel_one[i][j] = 255
                image_chanel_two[i][j] = 255
                image_chanel_three[i][j] = 255
            else:
                matrix_row.append(-1)
                image_channel_one[i][j] = 0
                image_chanel_two[i][j] = 0
                image_chanel_three[i][j] = 0
        area_matrix.append(matrix_row)

    area_percent, binary, ar_area = dfs(area_matrix, image)
    return area_percent, binary, area_percent > bad_percent, ar_area


def ar_flaw(image):
    """
    Ar缺陷度
    :param image: Ar图像
    :return: (缺陷度百分比, 缺陷度图像, 是否缺陷, 效果图, Ar面积)
    """
    flaw_image = deepcopy(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    light_or_shade = np.median(gray)
    if light_or_shade < 140:
        bad_percent, channels = 0.1, (160, 160, 180)
    else:
        bad_percent, channels = 0.2, (200, 200, 200)

    area_percent, binary, bad_image, ar_area = flaw(flaw_image, bad_percent, channels)
    src_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    temp = np.ones_like(image)
    temp.resize((src_rgb.shape[0], 2, 3))
    temp[:, :, :] = (255, 0, 0)
    effect_drawing = np.hstack((image, temp, flaw_image, temp, src_rgb))
    return area_percent, binary, bad_image, effect_drawing, ar_area
