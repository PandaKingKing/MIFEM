import os
import time
from pathlib import Path


class PathDir:
    """
    单个视频的路径管理器
    """

    def __init__(self, save_dir, video_name, video_input_dir=None):
        if video_input_dir is None:
            self.video_input_path = 'real-time'
            video_name = 'real-time.mp4'
        else:
            self.video_input_path = str(Path(video_input_dir) / video_name)
        # self.video_dir = self.mkdirs(save_dir / video_name / 'video')  # 视频保存路径（文件夹）
        # self.video_path = f'{self.video_dir}/{video_name.split(".")[0]}_result.mp4'  # 视频保存文件路径（具体路径）
        self.video_path = self.mkdirs(save_dir / video_name / 'images')  # 视频保存路径（文件夹）

        self.speed_distance_picture_dir = self.mkdirs(save_dir / video_name / 'speed-distance-picture')  # 速度图保存路径
        self.screenshot_dir = self.mkdirs(save_dir / video_name / 'screenshot')  # 微生物截图保存路径
        self.txt_dir = self.mkdirs(save_dir / video_name / 'text')  # 微生物其他信息保存路径
        self.execl_dir = self.mkdirs(save_dir / video_name / 'execl')  # execl指标保存路径（文件夹）
        self.execl_path = f'{self.execl_dir}/{video_name.split(".")[0]}_result.xlsx'  # execl指标保存路径（具体路径）
        self.json_dir = self.mkdirs(save_dir / video_name / 'json')  # JSON路径（文件夹）
        self.json_path = f'{self.json_dir}/{video_name.split(".")[0]}_result.json'  # JSON路径（具体路径）
        self.blurry_path = f'{save_dir / video_name}/{video_name.split(".")[0]}_blurry.json'  # 模糊度序列路径

    @staticmethod
    def mkdirs(dir_path):
        dir_path = str(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path


class PathManager:
    """
    路径管理器
    """

    def __init__(self, video_dir, output_dir):
        """

        :param video_dir: 视频所在目录
        :param output_dir: 输出目录
        """
        self.video_dir = video_dir
        self.output_dir = output_dir
        self._path_list = []  # 路径对象列表
        self.init()

    def init(self):
        """
        初始化所有路径对象
        :return:
        """
        local_time = time.localtime()
        dirname = f'{local_time.tm_year}-{local_time.tm_mon}-{local_time.tm_mday}'
        save_dir = Path(self.output_dir) / dirname

        for video_name in os.listdir(self.video_dir):
            path_dir = PathDir(save_dir, video_name, self.video_dir)
            self._path_list.append(path_dir)

    def items(self):
        """
        所有路径对象接口
        :return: 路径对象列表
        """
        return self._path_list


if __name__ == '__main__':
    p = PathManager(r'E:\MicrobialDetection\input', './output')
