import math
from .track import Track
from copy import deepcopy


class Tracker:
    TRACKING_DISTANCE_THRESHOLD = 120  # 追踪距离阈值(单位/像素)

    def __init__(self):
        self._counter = 0  # 小虫子总数量
        self.track_dict = {}  # 小虫子记录字典
        self.display_tracks_list = []  # 当前检测到的小虫子

    @staticmethod
    def tracking_distance(ori_point, new_point, translation):
        """
        计算追踪距离
        :param ori_point: 已存在的点
        :param new_point: 未分配的点
        :param translation: 位移矢量
        :return: 追踪距离
        """
        distance = math.sqrt(
            (ori_point[0] + translation[0] - new_point[0]) ** 2 + (ori_point[1] + translation[1] - new_point[1]) ** 2)
        return distance

    def clear(self):
        """
        过期点小虫子清除
        :return: 过期小虫子列表
        """
        clear_list = [self.track_dict.pop(track_id) for track_id, track in list(self.track_dict.items()) if
                      track.dead()]
        return clear_list

    def update(self, frame_index, message_list, translation):
        """
        更新小虫子信息
        :param frame_index: 帧数
        :param message_list: 小虫子信息列表
        :param translation: 位移矢量
        :return: None
        """
        # 清空监测到的小虫子列表
        self.display_tracks_list.clear()

        # 就近匹配
        queue = []
        for track_id, track in self.track_dict.items():
            if track.missing():
                continue
            for message_index, (x, y, area) in enumerate(message_list):
                distance = self.tracking_distance(track.base_point, (x, y), translation)
                if distance <= self.TRACKING_DISTANCE_THRESHOLD:
                    queue.append((track_id, message_index, distance))
        queue.sort(key=lambda item: item[2])

        message_index_set = set(index for index in range(len(message_list)))
        track_id_set = set(self.track_dict.keys())

        # 就近匹配更新
        while queue:
            track_id, message_index, distance = queue.pop(0)
            if track_id not in track_id_set or message_index not in message_index_set:
                continue
            track = self.track_dict[track_id]
            message = message_list[message_index]
            track_id_set.remove(track_id)
            message_index_set.remove(message_index)
            track.update(message, translation)
            self.display_tracks_list.append(track)

        # 更新已存在但是未匹配成功的对象
        for track_id in track_id_set:
            track = self.track_dict[track_id]
            track.update(translation=translation)

        # 初始化新找到的追踪对象
        for message_index in message_index_set:
            message = message_list[message_index]
            self._counter += 1
            track_id = self._counter
            track = Track(track_id, message, frame_index)
            self.track_dict[track_id] = track
            # self.display_tracks_list.append(track)  这行没必要了

    def display_tracks(self):
        """
        当前检测到的小虫子
        :return: 小虫子信息列表
        """

        display_tracks = deepcopy(
            [display_track for display_track in self.display_tracks_list if display_track.display()])
        return display_tracks
