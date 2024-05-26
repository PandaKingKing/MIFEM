from video.video_handle import VideoHandle
from multiprocessing import Lock

lock = Lock()


class VideoProcessing:
    """
    视频进程类
    """

    def __init__(self, sign_dict, video_queue):
        """

        :param sign_dict: 进程通信标记
        :param video_queue: 视频结果数据队列
        """
        self.sign_dict = sign_dict
        self.video_display = self.sign_dict['video_display']
        self.video_save = self.sign_dict['video_save']
        self.video_queue = video_queue
        self.video_queue_list = []
        self.handle = VideoHandle()

    def start(self):
        """
        开始进程
        :return:
        """

        while True:
            self._get_data()
            try:
                if len(self.video_queue_list) > 0:
                    image, blurry_text, yolo_frame_index, differ_frame_index, bug_list, \
                        total_bug_numbers = self.video_queue_list.pop(0)
                    if self.video_display or self.video_save:
                        frame = self.handle.draw_background(image, blurry_text, yolo_frame_index, differ_frame_index,
                                                            bug_list, total_bug_numbers)
                    if self.video_display:
                        self.handle.display(frame)
                    if self.video_save:
                        self.handle.save(frame)
                else:
                    if not self.sign_dict['manager_sign']:
                        continue
                    else:
                        break
            except:
                print('视频处理器出了点问题，但是没有影响。')
        lock.acquire()
        self.sign_dict['video_manager_sign'] = True
        print('video manager finish')
        lock.release()

    def _get_data(self):
        """
        获取输入数据
        :return:
        """
        lock.acquire()
        if not self.video_queue.empty():
            self.video_queue_list.append(self.video_queue.get())
        lock.release()

    def set_fps(self, fps):
        """
        设置视频帧率
        :param fps: 帧率
        :return:
        """
        self.handle.set_fps(fps)

    def set_video_save_path(self, video_save_path):
        """
        设置视频保存路径
        :param video_save_path: 视频保存路径
        :return:
        """
        self.handle.set_video_save_path(video_save_path)

    def set_video_message(self, video_message):
        """
        设置视频信息
        :param video_message: 视频信息(视频名称, 总帧数, 帧率)
        :return:
        """
        self.handle.set_video_message(video_message)
