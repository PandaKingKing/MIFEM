import cv2
import numpy as np
from copy import deepcopy
import os


class VideoHandle:
    """
    视频显示与保存
    """

    def __init__(self):
        self.video_type = 'mp4v'
        self.fps = 17

        self.save_path = None
        self.background = None
        self.title_height = 70
        self.penal_width = 1000
        self.video_width = 1824
        self.video_message = None

        self.video_writer = None
        self.window_init = False
        self.background_init = False

        self.frame_count = None

    def set_fps(self, fps):
        """
        设置视频帧率
        :param fps: 帧率
        :return: None
        """
        self.fps = fps

    def set_video_save_path(self, video_save_path):
        """
        设置视频保存路径
        :param video_save_path: 视频保存路径
        :return: None
        """
        self.save_path = video_save_path

    def set_video_message(self, video_message):
        """
        设置视频信息
        :param video_message: 视频信息(视频名称, 总帧数, 帧率)
        :return: None
        """
        self.video_message = video_message

    def display(self, frame):
        """
        显示视频
        :param frame: 需要显示的图像
        :return: None
        """

        if not self.window_init:
            cv2.namedWindow('display window', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('display window', frame.shape[1] // 2, frame.shape[0] // 2)
            self.window_init = True
        cv2.imshow('display window', frame)
        cv2.waitKey(1)

    def save1(self, frame):
        """
        保存视频
        :param frame: 需要保存的图像
        :return: None
        """

        if self.video_writer is None:

            if self.save_path is None:
                raise Exception('please input video save_dir!!!')
            fourcc = cv2.VideoWriter_fourcc(*self.video_type)
            self.video_writer = cv2.VideoWriter(self.save_path, fourcc, self.fps, (frame.shape[1], frame.shape[0]))
        self.video_writer.write(frame)

    def save(self, frame):
        """
        保存视频帧为图片
        :param frame: 需要保存的图像帧
        :return: None
        """
        if self.save_path is None:
            raise Exception('Please provide a save directory for the images!')

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        if self.frame_count is None:
            self.frame_count = 0

        image_name = f"frame_{self.frame_count}.jpg"
        image_path = os.path.join(self.save_path, image_name)

        cv2.imwrite(image_path, frame)
        self.frame_count += 1

    def init_background(self, frame):
        """
        初始化显示面板
        :param frame: 要显示的数据
        :return: None
        """

        self.background = np.zeros_like(frame)
        self.video_width = self.background.shape[1]
        self.background.resize(
            (self.background.shape[0] + self.title_height, self.background.shape[1] + self.penal_width, 3))
        self.background += 255

    def draw_background(self, image, blurry_text, yolo_frame_index, differ_frame_index, bug_list, total_bug_numbers):
        """
        绘制图像
        :param image: 视频数据
        :param blurry_text: 模糊度信息
        :param yolo_frame_index: yolo检测帧数
        :param differ_frame_index: 帧差法检测帧数
        :param bug_list: 当前需要统计的微生物
        :param total_bug_numbers: 微生物总体数量
        :return: 绘制好的图像
        """

        if not self.background_init:
            self.init_background(image)

        self.background[:self.title_height, :] = 255
        self.draw_title(self.background[:self.title_height, :], yolo_frame_index, differ_frame_index, blurry_text)
        self.background[self.title_height:, self.video_width:] = 255
        self.draw_penal(self.background[self.title_height:, self.video_width:], bug_list, total_bug_numbers)
        self.background[self.title_height:, :self.video_width] = image

        return deepcopy(self.background)

    @staticmethod
    def draw_penal(penal, bug_list, total_bug_numbers):
        """
        绘制数据面板
        :param penal: 数据显示区域
        :param bug_list: 当前需要统计的微生物
        :param total_bug_numbers: 微生物总体数量
        :return: None
        """

        cv2.putText(penal, 'Group characteristics', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)

        total_number_text = [
            '{:<20}'.format('Total numbers'),
            '{:<20}'.format(f'Arcellinida: {total_bug_numbers["Ar"]:0>3}'),
            '{:<20}'.format(f'Digononta: {total_bug_numbers["Do"]:0>3}'),
            '{:<20}'.format(f'Monogononta: {total_bug_numbers["Mo"]:0>3}'),
            '{:<20}'.format(f'Nematoda: {total_bug_numbers["Ne"]:0>3}'),
            '{:<20}'.format(f'Peritrichida: {total_bug_numbers["Gs"]:0>3}'),
            '{:<20}'.format(f'Aspidisca: {total_bug_numbers["Eu"]:0>3}'),
            '{:<20}'.format(f'Small protozoa: {total_bug_numbers["SmallProtozoa"]:0>3}')
        ]
        bug_numbers = {
            'Ar': 0,
            "Do": 0,
            'Mo': 0,
            'Ne': 0,
            'Eu': 0,
            'Gs': 0,
            'SmallProtozoa': 0
        }

        for text_index, text in enumerate(total_number_text):
            cv2.putText(penal, text, (10, 30 * (text_index + 3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)

        cv2.putText(penal, 'Individual characteristics--Small protozoa', (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), thickness=2)

        # cv2.putText(penal, 'MIC', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
        cv2.putText(penal, 'Linear', (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
        cv2.putText(penal, 'velocity', (10, 480), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
        cv2.putText(penal, 'Angular', (10, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
        cv2.putText(penal, 'velocity', (10, 580), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)
        width = 150
        start = 100
        counter = 0
        for bug in bug_list:
            if bug.detection_sequence[-1]:
                bug_numbers[bug.cls()] += 1
                if bug.cls() == 'Ar' or bug.cls() == 'Gs':
                    continue
                counter += 1
                bug_name = f'{bug.cls() if bug.cls() != "SmallProtozoa" else "Sp"} {bug.track_id}'
                cv2.putText(penal, bug_name, (start + width * counter, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                            thickness=2)
                cv2.putText(penal, str(round(bug.linear_velocity(), 2)), (start + width * counter, 460),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                            thickness=2)
                cv2.putText(penal, str(round(bug.angular_velocity(), 2)), (start + width * counter, 560),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                            thickness=2)

        live_number_text = [
            '{:<20}'.format('Live numbers'),
            '{:<20}'.format(f'Arcellinida: {bug_numbers["Ar"]:0>3}'),
            '{:<20}'.format(f'Digononta: {bug_numbers["Do"]:0>3}'),
            '{:<20}'.format(f'Monogononta: {bug_numbers["Mo"]:0>3}'),
            '{:<20}'.format(f'Nematoda: {bug_numbers["Ne"]:0>3}'),
            '{:<20}'.format(f'Peritrichida: {bug_numbers["Gs"]:0>3}'),
            '{:<20}'.format(f'Aspidisca: {bug_numbers["Eu"]:0>3}'),
            '{:<20}'.format(f'Small protozoa: {bug_numbers["SmallProtozoa"]:0>3}'),
        ]
        for text_index, text in enumerate(live_number_text):
            cv2.putText(penal, text, (penal.shape[1] // 2 + 10, 30 * (text_index + 3)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 0), thickness=2)

    def draw_title(self, title, yolo_frame_index, differ_frame_index, blurry_text):
        """
        绘制标题面板
        :param title: 视频信息显示区域
        :param yolo_frame_index: yolo检测帧数
        :param differ_frame_index: 帧差法检测帧数
        :param blurry_text: 模糊度信息
        :return: None
        """
        instant_frame_number = min(yolo_frame_index, differ_frame_index)
        video_name, total_frame, frame_rate = self.video_message
        total_frame = instant_frame_number if total_frame is None else total_frame
        left_title_text = f'Video name: {video_name} Total frame: {total_frame} Frame rate: {frame_rate}'
        cv2.putText(title, left_title_text, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                    thickness=2)
        right_title_text = f'Instant frame number {instant_frame_number} Blurry: {blurry_text}'
        cv2.putText(title, right_title_text, (title.shape[1] // 2 + 50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                    thickness=2)
