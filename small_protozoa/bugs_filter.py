class BBox:
    SERVAL_TIME = 80  # 检测框存活时间(单位/帧)
    OFFSET = 5  # 检测影响的边缘区域(单位/像素)

    def __init__(self, track_id, x1, y1, x2, y2):
        """

        :param track_id: 检测框唯一标识
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        """
        self.track_id = track_id
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2
        self.serval_time = self.SERVAL_TIME

    def inside(self, x, y):
        """
        判断一个点是否在检测框区域内
        :param x: 待检测点横坐标
        :param y: 待检测点纵坐标
        :return:
        """
        in_bbox = False
        if self.left - self.OFFSET <= x <= self.right + self.OFFSET and \
                self.top - self.OFFSET <= y <= self.bottom + self.OFFSET:
            in_bbox = True
        return in_bbox

    def out_of_screen(self):
        """
        检测框是否已经移出屏幕
        :return: False: 未移出屏幕，True: 已经移出屏幕
        """
        not_in_screen = False
        if self.serval_time <= 0 or self.right <= 0 or self.bottom <= 0:
            not_in_screen = True
        return not_in_screen

    def update_location(self, x1, y1, x2, y2):
        """
        更新检测框的坐标(检测框被追踪到的情况下)
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        self.serval_time -= 1
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2

    def update_translation(self, translation):
        """
        更新检测框的坐标(检测框未被追踪到的情况下)
        :param translation: 位移矢量
        :return:
        """
        self.serval_time -= 1
        self.left += translation[0]
        self.right += translation[0]
        self.top += translation[1]
        self.bottom += translation[1]


class BBoxFilter:
    """
    大虫子检测框过滤
    """

    def __init__(self):
        self.width = 1824  # 屏幕宽度
        self.height = 1216  # 屏幕高度
        self.edge = 10  # 屏幕左右边框裁剪距离(单位/像素)
        self.bbox_dict = {}  # 检测框记录字典

    def set_width(self, width):
        """
        设置图像宽度
        :param width: 图像宽度
        :return:
        """
        self.width = width

    def set_height(self, height):
        """
        设置图像高度
        :param height: 图像高度
        :return:
        """
        self.height = height

    def update_bbox(self, outputs, translation=None):
        """
        更新检测框信息
        :param outputs: 新的检测框信息
        :param translation: 位移矢量
        :return:
        """

        # 更新追踪到的检测框
        bbox_id_set = set()
        for output in outputs:
            x1, y1, x2, y2, track_id = output.tolist()
            if track_id not in self.bbox_dict:
                self.bbox_dict[track_id] = BBox(track_id, x1, y1, x2, y2)
            else:
                self.bbox_dict[track_id].update_location(x1, y1, x2, y2)
            bbox_id_set.add(track_id)

        # 更新微追踪到的检测框
        if translation:
            for track_id, bbox in self.bbox_dict.items():
                if track_id not in bbox_id_set:
                    bbox.update_translation(translation)

    def filter(self, message_list):
        """
        使用检测框过滤小虫子
        :param message_list: 检测信息列表
        :return: 过滤后的小虫子
        """
        tracks = []
        for message in message_list:
            x, y = message[0], message[1]
            in_bbox = False
            for track_id, bbox in self.bbox_dict.items():
                if bbox.inside(x, y):
                    in_bbox = True
                    break
            if not in_bbox and not self._near_the_edge(x, y):
                tracks.append(message)
        return tracks

    def clear(self):
        """
        清除移出屏幕的检测框
        :return:
        """
        clear_list = [track_id for track_id, bbox in self.bbox_dict.items() if bbox.out_of_screen()]
        for bbox_id in clear_list:
            self.bbox_dict.pop(bbox_id)

    def _near_the_edge(self, x, y):
        """
        边缘裁剪
        :param x: 横坐标
        :param y: 纵坐标(目前不考虑裁剪上下，为后续可能留的口)
        :return: 是否靠近边缘(True: 靠近 False: 不靠近)
        """
        near = True if x <= self.edge or x >= (self.width - self.edge) else False
        return near
