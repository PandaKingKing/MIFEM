import os
import cv2
import json
import numpy as np
import matplotlib
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages

rcParams['font.family'] = 'SimHei'  # 设置中文字体
rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题）
matplotlib.use('Agg')
from matplotlib import pyplot as plt


def save_blurry_list(path, blurry_list):
    """
    保存视频整体模糊度列表
    :param path: 保存路径
    :param blurry_list: 模糊度信息列表
    :return:
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(blurry_list))


class DrawSpeedAndDistance:

    def __init__(self, path_dir):
        """

        :param path_dir: 保存路径（文件夹）
        """
        self.path_dir = path_dir

    def draw(self, bug):
        """
        绘制图像并保存成pdf
        :param bug: 微生物信息
        :return: None
        """
        speed_list, distance_list = bug.speed_and_distance_data()
        cls_name = bug.cls()
        save_dir = os.path.join(self.path_dir, cls_name)
        pdf_path = f'{save_dir}/{bug.track_id}.pdf'
        os.makedirs(save_dir, exist_ok=True)
        with PdfPages(pdf_path) as pdf:
            # As many times as you like, create a figure fig and save it:
            fig = plt.figure()
            plt.ylim(0, 10)
            plt.title('速度/时间图(像素点/帧)')
            plt.xlabel('帧')
            plt.ylabel('速度')
            plt.plot(range(len(speed_list)), speed_list)
            pdf.savefig(fig)
            plt.close()
            fig = plt.figure()
            plt.ylim(0, 1000)
            plt.title('距离/时间图(像素点/帧)')
            plt.xlabel('帧')
            plt.ylabel('距离')
            plt.plot(range(len(distance_list)), distance_list)
            pdf.savefig(fig)
            plt.close()


class SaveText:

    def __init__(self, path_dir):
        """

        :param path_dir: 保存路径(文件夹)
        """
        self.path_dir = path_dir

    def save(self, bug):
        """

        :param bug: 大虫子信息
        :return: None
        """
        cls_name = bug.cls()
        save_path = os.path.join(self.path_dir, cls_name)
        os.makedirs(save_path, exist_ok=True)
        with open(f'{save_path}/{bug.track_id}.txt', 'w', encoding="utf-8") as f:
            f.write(f"first_frame(bug_id): {bug.first_frame}\tbug_type: {bug.cls()}\n"
                    f"detection_sequence : {bug.detection_sequence}\nblurry_list : {bug.blurry_list}\n")


class DrawBigProtozoaImage:

    def __init__(self, save_path):
        """

        :param path_dir: 保存路径(文件夹)
        """
        self.save_path = save_path

    def save(self, bug_cls, bug_id, image):
        """
        保存大虫子截图
        :param bug_cls: 类别文件夹
        :param bug_id: 追踪id
        :param image: 图像
        :return: None
        """
        save_dir = os.path.join(self.save_path, bug_cls)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'{bug_id}.jpg')
        cv2.imwrite(save_path, image)


class DrawArColorImage:

    def __init__(self, save_path):
        """

        :param path_dir: 保存路径(文件夹)
        """
        self.save_path = save_path
        self.dir = 'Ar'

    def save(self, bug_id, image, color):
        """
        保存Ar颜色图片
        :param bug_id: 追踪id
        :param image: 图像
        :param color: 颜色
        :return: 图片存储路径
        """
        save_dir = os.path.join(self.save_path, self.dir)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'{bug_id}-color.jpg')
        color_image = np.ones_like(image)
        color_image[:, :, :] = color
        cv2.imwrite(save_path, color_image)
        return save_path


class DrawArFlawImage:

    def __init__(self, save_path):
        """

        :param path_dir: 保存路径(文件夹)
        """
        self.save_path = save_path
        self.dir = 'Ar'

    def save(self, bug_id, effect_drawing):
        """
        Ar缺陷度效果图
        :param bug_id: 追踪id
        :param effect_drawing: 效果图
        :return: None
        """
        save_dir = os.path.join(self.save_path, self.dir)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'{bug_id}-flow.jpg')
        cv2.imwrite(save_path, effect_drawing)
