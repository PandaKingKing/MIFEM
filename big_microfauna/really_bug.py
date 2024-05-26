import json
from tools.calculation_index import (cal_translation_v1, cal_translation_w1, cal_ar_color, cal_ar_flaw,
                                     cal_average_area, dead_or_alive, dead_alive, cal_v2)
from tools.cal_mo_flaw import cal_mo_flaw
from tools.cal_do_flaw import cal_do_flaw
from pathlib import Path

root = Path(__file__).parent
filter_path = str(root / 'filter_config.json')


def init_config(config_path='./filter_config.json'):
    """
    配置真实性检验阈值
    :param config_path: 配置文件路径
    :return: None
    """
    class_map = {
        'Ar': Ar,
        "Do": Do,
        'Mo': Mo,
        'Ne': Ne,
        'Eu': Eu,
        'Gs': Gs
    }
    with open(config_path, 'r') as f:
        json_data = json.loads(f.read())
        for class_name, value_dict in json_data.items():
            bug_class = class_map[class_name]
            bug_class.INTERVAL_FRAME_NUMBER = value_dict['INTERVAL_FRAME_NUMBER']
            bug_class.INTERVAL_NUM = value_dict['INTERVAL_NUM']
            bug_class.FRAME_THRESHOLD = value_dict['FRAME_THRESHOLD']
            bug_class.INTERVAL_THRESHOLD = value_dict['INTERVAL_THRESHOLD']


def exist_detect(detection_sequence, interval_frame_number=10, interval_num=5, frame_threshold=6, interval_threshold=3):
    """
    真实性检验
    :param detection_sequence: 检测序列
    :param interval_frame_number: 小区间长度
    :param interval_num: 大区间长度
    :param frame_threshold: 小区间阈值
    :param interval_threshold: 大区间阈值
    :return: 是否存在(True: 存在, False: 不存在)
    """
    exist = False
    queue = []
    for i in range(0, len(detection_sequence), interval_frame_number):
        frame_number = sum(detection_sequence[i:i + interval_frame_number])
        if frame_number >= frame_threshold:
            queue.append(True)
        else:
            queue.append(False)
        if len(queue) == interval_num:
            interval_number = sum(queue)
            if interval_number >= interval_threshold:
                exist = True
                break
            queue.pop(0)
    return exist


class Ar:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'flaw', 'die/live', 'color'
        :param bug:  初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        self.bad_image, self.flaw, self.binary, self.effect_drawing, ar_area = cal_ar_flaw(screenshot)
        self.color = cal_ar_color(screenshot, self.binary)
        self.area_average = ar_area
        self.alive = 'die' if self.bad_image else 'live'

    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return: (第一帧(id), 面积,缺陷度, 是否存活)
        """
        bug_message = [self.first_frame, self.area_average, self.flaw, self.alive]
        return bug_message


class Do:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'v1', 'w1', 'v2', 'die/live',
        :param bug: 初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        self.area_average = cal_do_flaw(screenshot)
        self.v1 = cal_translation_v1(trajectory_list)
        self.v2 = cal_v2(bbox_list, detection_sequence)
        self.w1 = cal_translation_w1(trajectory_list)
        # self.alive = dead_or_alive(self.v1, trajectory_list)
        self.alive = dead_alive(first_frame, bbox_list, detection_sequence) #lnnnnnn

    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return:  (第一帧(id), 面积,移动速度,角速度,伸缩速度,是否存活)
        """
        bug_message = [self.first_frame, self.area_average, self.v1, self.w1, self.v2, self.alive]
        return bug_message


class Mo:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'v1', 'w1', 'v2', 'die/live',
        :param bug: 初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        # self.area_average = cal_average_area(screenshot, bbox_list)
        self.area_average = cal_mo_flaw(screenshot)
        self.alive = bug
        self.v1 = cal_translation_v1(trajectory_list)
        self.w1 = cal_translation_w1(trajectory_list)
        self.v2 = cal_v2(bbox_list, detection_sequence)
        # self.alive = dead_or_alive(self.v1, trajectory_list)
        self.alive = dead_alive(first_frame, bbox_list, detection_sequence)


    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return: (第一帧(id), 面积,移动速度,角速度,伸缩速度,是否存活)
        """
        bug_message = [self.first_frame, self.area_average, self.v1, self.w1, self.v2, self.alive]
        return bug_message


class Ne:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'v1', 'w1', 'die/live',
        :param bug: 初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        self.area_average = cal_average_area(screenshot, bbox_list)
        self.v1 = cal_translation_v1(trajectory_list)
        self.w1 = cal_translation_w1(trajectory_list)
        self.alive = dead_or_alive(self.v1, trajectory_list)

    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return: (第一帧(id), 面积,移动速度,角速度, 是否存活)
        """
        bug_message = [self.first_frame, self.area_average, self.v1, self.w1, self.alive]
        return bug_message


class Eu:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'v1', 'w1', 'die/live',
        :param bug: 初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        self.area_average = cal_average_area(screenshot, bbox_list)
        self.v1 = cal_translation_v1(trajectory_list)
        self.w1 = cal_translation_w1(trajectory_list)
        self.alive = dead_or_alive(self.v1, trajectory_list)

    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return:  (第一帧(id), 面积,移动速度,角速度, 是否存活)
        """
        bug_message = [self.first_frame, self.area_average, self.v1, self.w1, self.alive]
        return bug_message


class Gs:
    INTERVAL_FRAME_NUMBER = 10
    INTERVAL_NUM = 5
    FRAME_THRESHOLD = 6
    INTERVAL_THRESHOLD = 3

    def __init__(self, bug):
        """
        'frame', 'area_average', 'number',
        :param bug: 初步检测到的大虫子
        """
        first_frame, screenshot, bug_number, bbox_list, detection_sequence, trajectory_list = bug.transfer()
        self.first_frame = first_frame
        self.number = bug_number
        self.area_average = cal_average_area(screenshot, bbox_list)

    @classmethod
    def detect(cls, detection_sequence):
        """
        真实性检验
        :param detection_sequence: 检测序列
        :return: 是否真实际存在(真实存在：True，虚假存在：False)
        """
        is_exist = exist_detect(detection_sequence, cls.INTERVAL_FRAME_NUMBER, cls.INTERVAL_NUM, cls.FRAME_THRESHOLD,
                                cls.INTERVAL_THRESHOLD)
        return is_exist

    def message(self):
        """
        数据接口
        :return: (第一帧(id), 面积,聚簇数量)
        """
        bug_message = [self.first_frame, self.area_average, self.number]
        return bug_message


class SmallProtozoa:

    def __init__(self, bug):
        """
        'frame', 'area_average', 'v1', 'w1'
        :param bug: 初步检测到的小虫子
        """

        first_frame, track_id, area, v1, w1 = bug.transfer()

        self.first_frame = first_frame
        self.area_average = area
        self.v1 = v1
        self.w1 = w1

    def message(self):
        """
        数据接口
        :return: (第一帧(id), 面积,移动速度,角速度)
        """
        return [self.first_frame, self.area_average, self.v1, self.w1]


init_config(filter_path)
