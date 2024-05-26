import math
import cv2
from copy import deepcopy
from tools.real_time_speed import linear_velocity, angular_velocity


class Track:
    SERVAL_TIME = 100  # 存活时间
    BUG_TYPE = 'SmallProtozoa'  # 小虫子类别
    MISSING_THRESHOLD = 15  # 追踪目标丢失阈值

    def __init__(self, track_id, message, start_frame=0):
        """
        初始化
        :param track_id: 追踪id
        :param message:  检测信息 (x, y, area)
        :param start_frame: 被检测到的第一帧
        """
        self.track_id = track_id
        self.start_frame = int(start_frame)
        self.start_frame = f'{self.start_frame}(id {self.track_id})'
        self.bug_type = self.BUG_TYPE
        self.serval_time = self.SERVAL_TIME
        self.missing_counter = 0
        self.base_point = (message[0], message[1])  # 预测基准点
        self.area_list = [message[2]]  # 面积列表
        self.detection_sequence = [1]  # 检测序列
        self.real_point_list = [self.base_point]  # 真实点序列
        self.trajectory_list = [self.base_point]  # 小虫子最终轨迹
        self.display_trajectory_list = [self.base_point]  # 展示点轨迹

    @classmethod
    def cls(cls):
        """
        小虫子类别接口
        :return: 小虫子类别
        """
        return cls.BUG_TYPE

    def update(self, message=None, translation=None):
        """
        更新小虫子信息
        :param message: 小虫子信息(x, y, area)
        :param translation: 位移矢量
        :return:
        """

        self.serval_time -= 1
        self.update_display_queue(translation)

        if message:
            self.detection_sequence.append(1)
            self.real_point_list.append((message[0], message[1]))
            self.base_point = (message[0], message[1])
            self.area_list.append(message[2])
            self.display_trajectory_list.append((message[0], message[1]))
            self.trajectory_list = deepcopy(self.display_trajectory_list)
            self.missing_counter = 0
        else:
            self.detection_sequence.append(0)
            if self.missing_counter < self.MISSING_THRESHOLD:
                self.base_point = (int(self.base_point[0] + translation[0]), int(self.base_point[1] + translation[1]))
                self.missing_counter += 1
            self.display_trajectory_list.append(self.base_point)

    def update_display_queue(self, translation=None):
        """
        更新用于显示的轨迹
        :param translation: 位移矢量
        :return:
        """

        if translation:
            for i in range(len(self.display_trajectory_list)):
                self.display_trajectory_list[i] = (
                    int(self.display_trajectory_list[i][0] + translation[0]),
                    int(self.display_trajectory_list[i][1] + translation[1]))

    def missing(self):
        """
        小虫子是否追踪失败
        :return: 是否追踪失败(True：追踪成功，False：追踪失败)
        """
        miss = True if self.missing_counter >= self.MISSING_THRESHOLD else False
        return miss

    def dead(self):
        """
        小虫子是否到期与到期后处理
        :return: 是否到期(True：到期，False：未到期)
        """
        die = False
        if self.serval_time <= 0:
            while len(self.detection_sequence) > 0 and self.detection_sequence[-1] == 0:
                self.detection_sequence.pop()
            length = len(self.detection_sequence)
            self.trajectory_list = self.trajectory_list[:length]
            self.display_trajectory_list = self.display_trajectory_list[:length]
            die = True
        return die

    def span(self):
        """
        跨度的计算
        :return: 跨度
        """
        span_list = [point[1] for point in self.display_trajectory_list[:-1]]
        if len(span_list) <= 1:
            return float('inf')
        return round(max(span_list) - min(span_list), 2)

    def display(self):
        """
        小虫子绘制(显示)条件
        :return: 是否绘制(显示)(True: 显示, False: 不显示)
        """

        display = True if self.detection_sequence.count(1) > 2 else False
        return display

    def draw(self, frame):
        """
        小虫子移动轨迹绘制
        :param frame: 需要绘制的图像
        :return:
        """

        if self.display():
            circle_color = (0, 0, 255)
            line_color = (0, 255, 0)
            # 绘制移动轨迹
            for i in range(1, len(self.display_trajectory_list)):
                cv2.line(frame, self.display_trajectory_list[i - 1], self.display_trajectory_list[i], line_color,
                         thickness=5)
            # 绘制当前位置
            x, y = self.display_trajectory_list[-1]
            cv2.circle(frame, (x, y), 10, circle_color, -1)
            # 绘制文本信息
            x = (x + 50) if x < 500 else (x - 100)
            y = (y + 30) if y < 500 else (y - 20)
            cv2.putText(frame, f'SP {self.track_id}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, circle_color, 2)

    def detect(self):
        """
        真实性检验
        :return: 是否真实(True:真实, False:虚假)
        """
        really = False

        if self.angular_velocity() <= 0 or self.detection_sequence.count(1) < 3:
            return False

        if self.detection_sequence.count(1) > 2 and self.span() <= 50:
            really = True
        elif self.detection_sequence.count(1) > 5 and self.span() <= 150:
            really = True
        elif self.detection_sequence.count(1) > 20 and self.span() <= 500:
            really = True

        return really

    def get_area(self):
        """
        平均面积接口
        :return: 面积
        """

        area = sum(self.area_list) / len(self.area_list)
        return area

    def linear_velocity(self):
        """
        实时移动速度接口
        :return: 移动速度
        """

        v1 = linear_velocity(self.trajectory_list)
        return v1

    def angular_velocity(self):
        """
        实时角速度接口
        :return: 角速度
        """

        w1 = angular_velocity(self.trajectory_list)
        return w1

    def transfer(self):
        """
        数据返回接口
        :return: (开始帧, 追踪id, 平均面积, 平均移动速度, 平均角速度)
        """
        return self.start_frame, self.track_id, self.get_area(), self.linear_velocity(), self.angular_velocity()

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
