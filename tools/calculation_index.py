import math
from .ar_flaw import ar_flaw
from .real_time_speed import linear_velocity, angular_velocity
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def cal_translation_v1(center_point_list):
    """
    平均移动速度 v1
    :param center_point_list: 轨迹列表
    :return: 移动速度v1
    """
    v1 = linear_velocity(center_point_list)
    return round(v1, 2)


def cal_translation_w1(center_point_list):
    """
    平均角速度 w1
    :param center_point_list: 轨迹列表
    :return: 角度苏w1
    """
    w1 = angular_velocity(center_point_list)
    return round(w1, 2)


def cal_average_area(image, bbox_list):
    """
    计算微生物面积
    :param image:
    :param bbox_list:
    :return: 微生物面积
    """
    area_list = []
    for bbox in bbox_list:
        x1, y1, x2, y2 = bbox
        area = (x2 - x1) * (y2 - y1)
        area_list.append(area)
    if len(area_list) > 0:
        area = round(sum(area_list) / len(area_list), 2)
    else:
        area = 0
    # height, width = image.shape[:2]
    # area = height * width
    return area


def cal_ar_color(image, binary, top_k=5):
    """
    计算Ar颜色
    :param image: Ar图像
    :param binary: Ar所在区域
    :param top_k: 通道前top-k个融合
    :return: 代表Ar颜色的像素点
    """
    image_chanel1 = image[:, :, 0]
    image_chanel2 = image[:, :, 1]
    image_chanel3 = image[:, :, 2]
    record_count1 = {
        index: 0 for index in range(200)
    }
    record_count2 = {
        index: 0 for index in range(200)
    }
    record_count3 = {
        index: 0 for index in range(200)
    }
    for i in range(image_chanel1.shape[0]):
        for j in range(image_chanel1.shape[1]):
            if binary[i][j] != 255:
                continue
            if image_chanel1[i][j] < 160 and image_chanel2[i][j] < 160 and image_chanel3[i][j] < 180:
                record_count1[image_chanel1[i][j]] += 1
                record_count2[image_chanel2[i][j]] += 1
                record_count3[image_chanel3[i][j]] += 1

    chanel1_list = sorted(record_count1.items(), key=lambda item: item[1], reverse=True)[:top_k]
    chanel2_list = sorted(record_count2.items(), key=lambda item: item[1], reverse=True)[:top_k]
    chanel3_list = sorted(record_count3.items(), key=lambda item: item[1], reverse=True)[:top_k]
    channel1_sum = sum([count for value, count in chanel1_list])
    channel2_sum = sum([count for value, count in chanel2_list])
    channel3_sum = sum([count for value, count in chanel3_list])
    chanel1 = sum(
        [chanel1_list[i][0] * chanel1_list[i][1] / channel1_sum for i in range(len(chanel1_list))])
    chanel2 = sum(
        [chanel2_list[i][0] * chanel2_list[i][1] / channel2_sum for i in range(len(chanel2_list))])
    chanel3 = sum(
        [chanel3_list[i][0] * chanel3_list[i][1] / channel3_sum for i in range(len(chanel3_list))])
    image_color = (chanel1, chanel2, chanel3)
    return image_color


def cal_ar_flaw(image):
    """
    Ar缺陷度
    :param image: 图像
    :return: (是否是完整的，缺陷度信息，缺陷度图像，效果图，Ar面积)
    """
    area_percent, binary, bad_image, effect_drawing, ar_area = ar_flaw(image)
    return bad_image, f'{area_percent * 100: .2f}%', binary, effect_drawing, ar_area


def dead_or_alive(v1, center_point_list, speed_threshold=2, distance_threshold=200):
    """
    微生物死或生（依靠速度判断）
    :param v1: 平均移动速度
    :param center_point_list: 中心点列表
    :param speed_threshold: 移动速度阈值
    :param distance_threshold: 移动距离阈值
    :return: 死或生
    """

    distance_list = []
    for i in range(1, len(center_point_list)):
        point1, point2 = center_point_list[i - 1], center_point_list[i]
        d = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
        distance_list.append(d)
    total_distance = sum(distance_list)
    #**************************************************
    avg_area = cal_average_area(bbox_list, detection_sequence)
    if avg_area > 9000:
        alive = 'live' if max_speed >= SPEED_THRESHOLD or total_distance >= DISTANCE_THRESHOLD else 'die'
    elif avg_area > 6000:
        alive = 'live' if max_speed >= SPEED_THRESHOLD-1 or total_distance >= DISTANCE_THRESHOLD/2 else 'die'
    elif avg_area > 3000:
        alive = 'live' if max_speed >= SPEED_THRESHOLD-1 or total_distance >= DISTANCE_THRESHOLD/4 else 'die'
    #**************************************************
    #alive = 'live' if v1 >= speed_threshold or total_distance >= distance_threshold else 'die'
    return alive


def cal_distance(per_location, location):
    """
    计算移动距离
    :param per_location:
    :param location:
    :return:
    """
    ori_center_x = (per_location[0] + per_location[2]) / 2
    ori_center_y = (per_location[1] + per_location[3]) / 2

    left_bottom_x, left_bottom_y = per_location[0], per_location[3]

    offset_x = ori_center_x - left_bottom_x
    offset_y = ori_center_y - left_bottom_y

    predict_center_x = location[0] + offset_x
    predict_center_y = location[3] + offset_y

    center_x = (location[0] + location[2]) / 2
    center_y = (location[1] + location[3]) / 2

    distance = math.sqrt((predict_center_x - center_x) ** 2 + (predict_center_y - center_y) ** 2)
    distance = distance if distance >= 2 else 0  # 过滤

    return distance

def cal_speed_list(distance_list, speed_frame=5):
    """
    获取移动速度列表
    :param distance_list:
    :param speed_frame:
    :return:
    """
    # 计算每帧的移动速度
    # speed_list = []
    # for index, distance in enumerate(distance_list):
    #     if index < speed_frame:
    #         speed = distance_list[:index] / (index + 1)
    #     else:
    #         speed = distance_list[index - speed_frame + 1:index + 1] / speed_frame
    #     speed_list.append(speed)
    speed_list = [
        sum(distance_list[:index]) / (index + 1) if index < speed_frame else
        sum(distance_list[index - speed_frame + 1:index + 1]) / speed_frame
        for index in range(len(distance_list))
    ]

    return speed_list

# ln 2023.12.29
def cal_distance_list1(bbox_list, detection_sequence):
    distance_list = []
    per_location = None
    consecutive_detections = 0  # 记录连续检测到物体的次数

    for bbox, is_detect in zip(bbox_list, detection_sequence):
        if is_detect:
            if consecutive_detections < 2:  # 连续两次检测到物体
                consecutive_detections += 1
                if len(distance_list) == 0:
                    per_location = bbox
                else:
                    distance_list.append(0)  # 未计算距离时，添加0到列表
                    per_location = bbox
            else:
                distance = cal_distance(per_location, bbox)
                distance_list.append(distance)
                per_location = bbox
        else:
            consecutive_detections = 0  # 未检测到物体，重置连续检测次数为0
            if len(distance_list) == 0:
                distance_list.append(0)
            else:
                distance_list.append(distance_list[-1])

    return distance_list



def cal_distance_list(bbox_list, detection_sequence):
    """

    :param bbox_list:
    :param detection_sequence:
    :return:
    """
    distance_list = []
    per_location = None
    # 计算每次移动的距离
    for bbox, is_detect in zip(bbox_list, detection_sequence):
        if is_detect:
            if len(distance_list) == 0:
                per_location = bbox
            else:
                distance = cal_distance(per_location, bbox)
                distance_list.append(distance)
                per_location = bbox
        else:
            if len(distance_list) == 0:
                distance_list.append(0)
            else:
                distance_list.append(distance_list[-1])

    return distance_list

SPEED_THRESHOLD1 = 1
DISTANCE_THRESHOLD1 = 2

def dead_alive1(first_frame, bbox_list, detection_sequence):
    distance_list = cal_distance_list(bbox_list, detection_sequence)
    speed_list = cal_speed_list(distance_list)
    logging.info(first_frame, distance_list)
    try:
        max_speed = max(speed_list)
        total_distance = sum(distance_list)
        # # **************************************
        # print("bbox_list:", bbox_list)
        # print("max_speed:", max_speed)
        # print("total_distance:", total_distance)
        # # **************************************
        alive = 'live' if max_speed >= SPEED_THRESHOLD1 or total_distance >= DISTANCE_THRESHOLD1 else 'die'
    except:
        alive = 'die'
    return alive

# ln 2023.12.29
def dead_alive(first_frame, bbox_list, detection_sequence):
    count = 0
    alive = 'die'
    distance_list = cal_distance_list1(bbox_list, detection_sequence)
    logging.info(f'{first_frame}, {distance_list}')
    for i in range(len(distance_list)):
        distance = distance_list[i]
        if distance > DISTANCE_THRESHOLD1:
            count += 1
        if count > 3:
            alive = 'live'
            return alive
    return alive


def area_iou(per_location, location):
    """
    根据面积变化判断伸缩情况
    :param per_location: 上一课点的位置信息
    :param location: 当前点的位置信息
    :return: 伸缩状态
    """

    x11, y11, x12, y12 = per_location
    x21, y21, x22, y22 = location

    x12 -= x11
    y12 -= y11

    x22 -= x21
    y22 -= y21
    area_old = x12 * y12
    area_new = x22 * y22
    area_overlap = min(x12, x22) * min(y12, y22)
    area_threshold = 0

    if x22 < x12 and y22 < y12:
        area_loss = area_old - area_new
    elif x22 > x12 and y22 > y12:
        area_loss = area_new - area_old
    elif x22 >= x12 and y22 <= y12:
        top_loss = area_old - area_overlap
        right_loss = area_new - area_overlap

        area_loss = right_loss - top_loss / 2
        area_threshold = top_loss / 2
    elif x22 <= x12 and y22 >= y12:  # 向上伸展
        top_loss = area_new - area_overlap
        right_loss = area_old - area_overlap

        area_loss = top_loss - right_loss / 2
        area_threshold = right_loss / 2
    elif x22 == x12 and y22 == y12:
        area_loss = area_new - area_old  # 不动
    else:
        raise Exception(f'未知异常 x12: {x12} y12{y12} x22{x22} y22{y22}')

    if area_loss < 0:
        state = 'contraction'
    elif area_loss > area_threshold:
        state = 'extend'
    else:
        state = 'static'
    return state


def cal_state_list(bbox_list, detection_sequence):
    """
    计算状态
    :param bbox_list: 检测框信息
    :param detection_sequence: 检测序列
    :return: 伸缩状态列表
    """
    state_list = []
    per_location = None
    for bbox, is_detect in zip(bbox_list, detection_sequence):
        if is_detect:
            if len(state_list) == 0 and per_location is None:
                per_location = bbox
            else:
                state = area_iou(per_location, bbox)
                if state == 'static':
                    if len(state_list) > 0:
                        state_list.append(state_list[-1])
                else:
                    state_list.append(state)
                per_location = bbox
        else:
            if len(state_list) > 0:
                state_list.append(state_list[-1])
    # print(state_list)
    return state_list


def cal_v2(bbox_list, detection_sequence, method='area'):
    """
    计算伸缩速度
    :param bbox_list: 检测框信息
    :param detection_sequence: 检测序列
    :param method: 计算方法 area: 面积变化率
    :return: 伸缩速度v2
    """
    state_list = cal_state_list(bbox_list, detection_sequence)
    if method == 'area':
        v2_list = v2_area(state_list, bbox_list)
    elif method == 'center_point':
        raise Exception(f'{method} has remove')
    else:
        raise Exception(f'please choice right method, {method} is not found')

    try:
        v2 = sum(v2_list) / len(v2_list) / 2
    except ZeroDivisionError:
        v2 = 0
    return v2


def v2_area(state_list, bbox_list):
    """
    计算面积变化率
    :param state_list: 伸缩状态列表
    :param bbox_list: 检测框信息
    :return: 面积变化率列表
    """
    flag = False
    frames = 0
    v2_list = []
    area_list = []
    for index, (state, bbox) in enumerate(zip(state_list, bbox_list)):
        frames += 1
        if bbox is None:
            continue
        area = abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])
        area_list.append(area)
        if index == 0:
            continue
        if state != state_list[index - 1]:
            if flag is True:
                areas = 0
                for area_index in range(1, len(area_list)):
                    areas += abs(area_list[area_index] - area_list[area_index - 1])
                v2 = areas / frames
                v2_list.append(v2)
                area_list = []
                frames = 0
                flag = False
            else:
                flag = True
    return v2_list
