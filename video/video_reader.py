import cv2
from copy import deepcopy


class VideoReader:
    """
    视频输入器
    """

    def __init__(self, video_path, start_frame=0, end_frame=50000):
        """

        :param video_path: 视频路径
        :param start_frame: 开始帧数(默认第0帧开始)
        :param end_frame: 结束帧数(默认播放整个视频)
        """
        self.video_path = video_path  # 视频路径
        self.video_name = video_path.split('\\')[-1]  # 名称

        self.cap = cv2.VideoCapture(self.video_path)  # 视频对象

        self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 总帧数
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 帧率
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 宽
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 高

        self.start_frame = start_frame  # 开始帧
        self.end_frame = min(self.total_frames, end_frame)  # 结束帧

        self.frame_index = 0  # 当前视频帧数

    def video_message(self):
        """
        视频信息接口
        :return: (视频名称，总帧数，帧率)
        """

        return self.video_name, self.total_frames, self.fps

    def frames(self):
        """
        视频数据接口
        :return: 视频帧序列生成器
        """
        return self

    def __iter__(self):
        """
        迭代器对象方法
        :return: 视频帧序列迭代器
        """

        while self.cap.isOpened():
            if self.frame_index >= self.start_frame or self.frame_index >= self.end_frame:
                break
            self.frame_index += 1
            self.cap.read()

        return self

    def __next__(self):
        """
        生成器对象方法
        :return: 视频帧
        """

        if not self.cap.isOpened():
            raise StopIteration
        ret, frame = self.cap.read()
        result = deepcopy(frame)
        del frame
        self.frame_index += 1
        if not ret or self.frame_index > self.end_frame:
            raise StopIteration
        return result
