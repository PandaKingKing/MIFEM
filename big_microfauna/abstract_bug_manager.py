from copy import deepcopy
from .abstract_bug import AbstractBug


class AbstractBugManager:
    """
    初步检测到的大虫子信息管理
    """
    NAMES = {0: 'Gs', 1: 'Mo', 2: 'Do', 3: 'Eu', 4: 'Ne', 5: 'Ar'}  # 微生物类别与名称映射（如果增加新的类别需要修改）

    def __init__(self):
        self.bug_dict = {}  # 所有的初级微生物信息
        self._display_list = []  # 当前需要显示的微生物信息

    @classmethod
    def _cls_to_english_name(cls, bug_cls):
        """
        微生物类别与英文名称的转换
        :param bug_cls: 微生物类别
        :return: 微生物类别对应的英文名称缩写
        """
        english_name = cls.NAMES.get(int(bug_cls))
        return english_name

    def update(self, frame_index, frame, outputs, others, blurry, translation=None):
        """

        :param frame_index: 帧数
        :param frame: 当前帧图象
        :param outputs: 检测结果信息, outputs中的每一项：(x1, y1, x2, y2, track_id)
        :param others:  与检测对应的其他信息
        :param blurry:  当前帧是否模糊
        :param translation: 位移矢量
        :return: None
        """
        boundary_boxs, track_ids, clss, bug_nums_list = self._parse_message(outputs, others)
        self._display_list.clear()

        # 添加新出现的微生物
        for track_id, bug_id in enumerate(track_ids):
            if bug_id not in self.bug_dict:
                self.bug_dict[bug_id] = AbstractBug(frame_index, bug_id)  # 添加新被检测到的微生物

        # 更新所有检测到的微生物的信息
        for bug_id, bug in self.bug_dict.items():
            if bug_id in track_ids:
                track_id = track_ids.index(bug_id)
                if bug.is_update_screenshot():
                    screenshot = deepcopy(frame[boundary_boxs[track_id][1]:boundary_boxs[track_id][3],
                                          boundary_boxs[track_id][0]:boundary_boxs[track_id][2]])
                    bug.update_screenshot(screenshot)
                bbox, cls, bug_nums = boundary_boxs[track_id], clss[track_id], bug_nums_list[track_id]
                bug.update(bbox, cls, bug_nums, blurry, translation)
                self._display_list.append(bug)
            else:
                bug.update(translation=translation)

    def clear(self):
        """
        清理过期的大虫子信息
        :return: 储存过期的大虫子的列表
        """
        clear_list = []
        for key, bug in list(self.bug_dict.items()):
            if not bug.alive():
                clear_list.append(self.bug_dict.pop(key))
        return clear_list

    def display_tracks(self):
        """
        需要显示的大虫子
        :return:
        """
        display_tracks = deepcopy(self._display_list)
        return display_tracks

    def _parse_message(self, outputs, others):
        """
        预测信息解析
        :param outputs: yolo预测信息
        :param others: 其他信息(类别, 聚簇数量)
        :return: 预测框列表, 追踪id列表, 类别列表, 聚簇数量列表
        """
        boundary_box_list, track_id_list, cls_list, bug_nums_list = outputs[:, :4].tolist(), outputs[:, 4].tolist(), [
            self._cls_to_english_name(other.cls) for other in others], [other.bug_nums for other in others]
        return boundary_box_list, track_id_list, cls_list, bug_nums_list
