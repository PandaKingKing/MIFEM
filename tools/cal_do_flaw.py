import cv2
import math
import numpy as np
from copy import deepcopy


class Ellipse:

    def __init__(self, center_x, center_y, a, b):
        self.center_x = center_x
        self.center_y = center_y
        self.a = a
        self.b = b

    def in_elliptic(self, x, y):
        real_x = self.center_x - x
        real_y = y - self.center_y
        try:
            pred_y = math.sqrt((1 - ((real_x ** 2) / (self.a ** 2))) * (self.b ** 2))
        except:
            return False
        if abs(real_y) <= pred_y:
            return True
        else:
            return False

    def is_bounder(self, x, y):
        real_x = self.center_x - x
        real_y = y - self.center_y
        try:
            pred_y = math.sqrt((1 - ((real_x ** 2) / (self.a ** 2))) * (self.b ** 2))
        except:
            return False
        if pred_y - 1.5 <= abs(real_y) <= pred_y + 1.5:
            return True
        else:
            return False

    def area(self):

        return math.pi * self.a * self.b


def bound_dfs(image, point_list, ellipse):
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
    ksize = 3
    kernel1 = np.ones((ksize, ksize), np.float64)
    binary = cv2.morphologyEx(imGray, cv2.MORPH_ERODE, kernel1)
    circle_area = ellipse.area()
    area = np.sum(binary) / 255
    area_percent = round(1 - area / circle_area, 2)
    return area_percent, binary, ellipse


def flaw(image, channels):
    """
    计算缺陷度
    :param image:
    :param bad_percent:
    :param channels
    :return:
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

    area_percent, binary, ellipse = dfs(area_matrix, image)
    return area_percent, binary, ellipse


def cal_do_flaw(image):
    flaw_image = deepcopy(image)
    diff = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    light_or_shade = np.median(diff)
    if light_or_shade < 100:
        channels = (80, 80, 100)
    elif light_or_shade < 140:
        channels = (140, 140, 140)
    elif light_or_shade < 160:
        channels = (160, 160, 180)
    else:
        channels = (180, 180, 180)

    area_percent, binary, ellipse = flaw(flaw_image, channels)

    if light_or_shade < 100:
        flip = False
    elif light_or_shade < 140:
        flip = False if area_percent <= 0.4 else True
    elif light_or_shade < 160:
        flip = False
    else:
        flip = True

    if flip:
        for i in range(binary.shape[0]):
            for j in range(binary.shape[1]):
                if ellipse.in_elliptic(j, i):
                    if binary[i][j] == 255 and not ellipse.is_bounder(j, i):
                        binary[i][j] = 0
                    else:
                        binary[i][j] = 255
    area = np.sum(binary) / 255
    return area
