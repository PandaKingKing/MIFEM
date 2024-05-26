from .really_bug import *
from writer.write_to_others import (DrawBigProtozoaImage, DrawArColorImage, DrawArFlawImage, DrawSpeedAndDistance,
                                    SaveText)


class ReallyBugRecord:
    BUG_NAMES = ['Gs', 'Mo', 'Do', 'Eu', 'Ne', 'Ar', 'SmallProtozoa']

    def __init__(self, path_dir, video_name, fps, frames):
        """

        :param path_dir: 路径管理器对象
        :param video_name: 视频名称
        :param fps: 帧率
        :param frames: 视频总帧数
        """
        self.path_dir = path_dir
        self.base_dir = self.path_dir.screenshot_dir
        self.bug_numbers = {name: 0 for name in self.BUG_NAMES}

        # 微生物与对应实体类的映射列表
        self.class_map = {'Ar': Ar, "Do": Do, 'Mo': Mo, 'Ne': Ne, 'Eu': Eu, 'Gs': Gs, 'SmallProtozoa': SmallProtozoa}

        self.bug_dead_or_live = None
        self.bug_record = None
        self.gs_area_list = None
        self.ar_colors_list = None

        self.video_path, self.fps, self.frames = video_name, fps, frames
        self.draw_speed_distance = DrawSpeedAndDistance(self.path_dir.speed_distance_picture_dir)
        self.save_text = SaveText(self.path_dir.txt_dir)
        self.draw_screenshot = DrawBigProtozoaImage(self.base_dir)
        self.draw_color = DrawArColorImage(self.base_dir)
        self.draw_flaw = DrawArFlawImage(self.base_dir)

    def allocation(self, bug_list):
        """
        分配器
        :param bug_list: 记录的微生物信息
        :return: None
        """
        for abstract_bug in bug_list:
            cls_name = abstract_bug.cls()
            bug_type = self.class_map[cls_name]
            if cls_name == 'SmallProtozoa':
                if abstract_bug.detect():
                    self.bug_numbers[cls_name] += 1
                    bug = SmallProtozoa(abstract_bug)
                    self.bug_record[cls_name].append(bug.message())
                    # 绘制速度移动距离图
                    self.draw_speed_distance.draw(abstract_bug)
            else:

                if bug_type.detect(abstract_bug.detection_sequence):
                    self.bug_numbers[cls_name] += 1

                    bug = bug_type(abstract_bug)
                    if cls_name == 'Gs':
                        self.gs_area_list.append(bug.area_average)
                    else:
                        self.bug_dead_or_live[cls_name][bug.alive] += 1

                    self.bug_record[cls_name].append(bug.message())
                    # 绘制截图
                    self.draw_screenshot.save(cls_name, abstract_bug.track_id, abstract_bug.screenshot)

                    if cls_name == 'Ar':
                        color_path = self.draw_color.save(abstract_bug.track_id, abstract_bug.screenshot, bug.color)
                        self.draw_flaw.save(abstract_bug.track_id, bug.effect_drawing)
                        self.ar_colors_list.append(color_path)

                    # 绘制速度移动距离图
                    self.draw_speed_distance.draw(abstract_bug)
                    # 保存文本
                    self.save_text.save(abstract_bug)

    def set_bug_dead_or_live(self, bug_dead_or_live):
        """
        设置大虫子死活信息储存对象
        :param bug_dead_or_live: 大虫子死活信息储存对象
        :return: None
        """
        self.bug_dead_or_live = bug_dead_or_live

    def set_bug_record(self, bug_record):
        """
        设置微生物各项数据储存对象
        :param bug_record:
        :return:
        """
        self.bug_record = bug_record

    def set_gs_area_list(self, gs_area_list):
        """
        设置Gs面积储存对象
        :param gs_area_list:
        :return:
        """
        self.gs_area_list = gs_area_list

    def set_ar_colors_list(self, ar_colors_list):
        """
        设置Ar颜色图片路径储存对象
        :param ar_colors_list:
        :return:
        """
        self.ar_colors_list = ar_colors_list
