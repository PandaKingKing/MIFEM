import math
from copy import deepcopy
from tools.real_time_speed import linear_velocity, angular_velocity


class AbstractBug:
    """
    大虫子预测信息
    """
    SURVIVAL_TIME = 200  # 信息存在时间(单位/帧)
    SCREENSHOT_SAVE_TIME = 30  # 大虫子截图保存时间 min(SCREENSHOT_SAVE_TIME, 最后被检测到的一帧)

    def __init__(self, frame_index, track_id):
        """

        :param frame_index: 出现的第一帧
        :param track_id:追踪id
        """
        self.track_id = track_id  # 追踪id
        self.first_frame = frame_index  # 出现的第一帧
        self.first_frame = f'{self.first_frame}(id: {self.track_id})'
        self.screenshot = None  # 截图
        self.bbox_list = []  # 预测框信息
        self.detection_sequence = []  # 检测序列
        self.cls_dict = {}  # 类别字典
        self.bug_nums_list = []  # 聚簇数量
        self.survival_time = self.SURVIVAL_TIME  # 信息存在时间(单位/帧)
        self.blurry_list = []  # 模糊度列表
        self.center_point_list = []  # 中心点列表(跟随位移矢量更新)
        self.trajectory_list = []  # 大虫子最终轨迹

    def update(self, bbox=None, cls=None, blurry=None, bug_nums=None, translation=None):
        """
        更新大虫子信息
        :param bbox: 预测框信息
        :param cls: 类别
        :param bug_nums: 聚簇数量
        :param blurry: 是否模糊
        :param translation: 位移矢量
        :return: None
        """
        self.survival_time -= 1  # 存在时间减一
        # 添加各种信息
        self.blurry_list.append(blurry)  # 当前帧的模糊度
        self._update_translation(translation)

        if bbox:
            self.detection_sequence.append(1)  # 是否被检测到
            self.bbox_list.append(bbox)
            if cls not in self.cls_dict:
                self.cls_dict[cls] = 0
            self.cls_dict[cls] += 1
            self.bug_nums_list.append(bug_nums)
            x1, y1, x2, y2 = bbox
            self.center_point_list.append(((x1 + x2) / 2, (y1 + y2) / 2))
            self.trajectory_list = deepcopy(self.center_point_list)
        else:
            self.detection_sequence.append(0)  # 是否被检测到
            self.bbox_list.append(self.bbox_list[-1])

    def is_update_screenshot(self):
        """
        是否更新大虫子截图
        :return: 是否更新(True: 更新, False: 不更新)
        """
        is_update = True if sum(self.detection_sequence) <= self.SCREENSHOT_SAVE_TIME else False

        return is_update

    def update_screenshot(self, screenshot):
        """
        更新大虫子截图
        :param screenshot: 新的大虫子截图
        :return: None
        """
        self.screenshot = screenshot

    def alive(self):
        """
        大虫子信息是否存在(移出屏幕)
        :return: 是否存在(存在为True,不存在为False)
        """

        is_alive = True if self.survival_time > 0 else False
        if not is_alive:
            while self.detection_sequence[-1] == 0:
                self.detection_sequence.pop()

            length = len(self.detection_sequence)
            self.bbox_list = self.bbox_list[:length]
            self.blurry_list = self.blurry_list[:length]
            self.center_point_list = self.center_point_list[:length]
            self.trajectory_list = self.trajectory_list[:length]

        return is_alive

    def cls(self):
        """
        判别大虫子类别（默认被检测数量最多的）
        :return:　数量最多的大虫子类别英文名称
        """

        cls_name = sorted(self.cls_dict, key=self.cls_dict.get, reverse=True)[0]
        return cls_name

    def linear_velocity(self):
        """
        实时移动速度接口
        :return: 实时移动速度v1
        """

        v1 = linear_velocity(self.trajectory_list)
        return v1

    def angular_velocity(self):
        """
        实时角速度接口
        :return: 实时移动速度w1
        """

        w1 = angular_velocity(self.trajectory_list)
        return w1

    def speed_and_distance_data(self):
        """
        绘制平均速度与路程图像的数据接口
        :return: (速度列表，路程列表)
        """

        speed_list, distance_list = [], []
        for i in range(1, len(self.trajectory_list)):
            point1, point2 = self.trajectory_list[i - 1], self.trajectory_list[i]
            distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
            if len(distance_list) > 0:
                distance_list.append(distance_list[-1] + distance)
            else:
                distance_list.append(distance)
            speed = distance_list[-1] / i
            speed_list.append(speed)
        return speed_list, distance_list

    def transfer(self):
        """
        信息返回接口
        :return:　返回大虫子的所有信息(被检测到的第一帧，截图，聚簇数量，检测框列表，检测序列，中心点轨迹)
        """

        return [self.first_frame, self.screenshot, self._bug_number(), self.bbox_list, self.detection_sequence,
                self.trajectory_list]

    def _update_translation(self, translation):
        """
        使用位移矢量更新数据点
        :param translation: 位移矢量
        :return: None
        """
        if translation:
            for i in range(len(self.center_point_list)):
                self.center_point_list[i] = (int(self.center_point_list[i][0] + translation[0]),
                                             int(self.center_point_list[i][1] + translation[1]))

    def _bug_number(self):
        """
        计算大虫子聚簇数量
        :return: 大虫子聚簇数量
        """

        bug_number = math.ceil(sum(self.bug_nums_list) / len(self.bug_nums_list))
        return bug_number
