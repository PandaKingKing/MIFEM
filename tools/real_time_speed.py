import math


def cal_distance(point1, point2):
    """
    计算两点间距离
    :param point1: 第一个点
    :param point2: 第二个点
    :return:
    """

    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def total_distance(trajectory_list):
    """
    计算移动距离
    :param trajectory_list: 轨迹点列表
    :return:
    """
    distance = sum([cal_distance(trajectory_list[i - 1], trajectory_list[i]) for i in range(1, len(trajectory_list))])
    return distance


def linear_velocity(trajectory_list):
    """
    计算平均移动速度
    :param trajectory_list: 轨迹点列表
    :return: 平均移动速度v1
    """

    distance = total_distance(trajectory_list)
    try:
        v1 = distance / len(trajectory_list)
    except ZeroDivisionError:
        v1 = 0
    return v1


def cal_angle(point1, point2, point3):
    """
    计算转角
    :param point1: 第一个点
    :param point2: 第二个点
    :param point3: 第三个点
    :return: 转角度数
    """
    c, a, b = cal_distance(point2, point1), cal_distance(point2, point3), cal_distance(point1, point3)
    try:
        cos_b = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
        w = 180 - round(math.acos(cos_b) * 180 / math.pi, 2)
    except ValueError:
        w = 0
    except ZeroDivisionError:
        w = 0
    return w


def angular_velocity(trajectory_list):
    """
    计算平均角速度
    :param trajectory_list: 轨迹列表
    :return: 平均角速度w1
    """
    w_list = [cal_angle(trajectory_list[i - 2], trajectory_list[i - 1], trajectory_list[i]) for i in
              range(2, len(trajectory_list))]

    try:
        w1 = sum(w_list) / len(w_list)
    except ZeroDivisionError:
        w1 = 0
    return w1
