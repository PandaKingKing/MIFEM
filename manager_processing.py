from copy import deepcopy
from multiprocessing import Lock
from tools.drawer import draw_messages
from big_microfauna.abstract_bug_manager import AbstractBugManager

lock = Lock()


class ManagerProcessing:

    def __init__(self, sign_dict, yolo_result_queue, frame_result_queue, video_queue, bug_record):
        """

        :param sign_dict: 进程通信标记
        :param yolo_result_queue: 大虫子结果队列
        :param frame_result_queue: 小虫子结果队列
        :param video_queue: 结果图像数据队列
        :param bug_record:
        """

        self.sign_dict = sign_dict
        self.yolo_result_queue = yolo_result_queue
        self.frame_result_queue = frame_result_queue
        self.video_queue = video_queue

        self.yolo_result_list = []
        self.frame_result_list = []

        self.video_display = self.sign_dict['video_display']
        self.video_save = self.sign_dict['video_save']

        self.abstract_bug_manager = AbstractBugManager()
        self.bug_record = bug_record

    def start(self):
        """
        开始进程
        :return:
        """
        while True:
            self._get_data()
            try:
                if len(self.yolo_result_list) > 0 and len(self.frame_result_list) > 0:

                    yolo_frame_index, differ_frame_index = self.yolo_result_list[0][0], self.frame_result_list[0][0]
                    translation, bug_list = None, []

                    if yolo_frame_index < differ_frame_index:
                        yolo_frame_index, yolo_frame, outputs, others, blurry, \
                            blurry_text = self.yolo_result_list.pop(0)
                    elif yolo_frame_index > differ_frame_index:
                        differ_frame_index, differ_frame, differ_clear_list, translation, display_tracks, blurry, \
                            blurry_text = self.frame_result_list.pop(0)
                        bug_list.extend(display_tracks)
                    else:
                        yolo_frame_index, yolo_frame, outputs, others, blurry, \
                            blurry_text = self.yolo_result_list.pop(0)
                        differ_frame_index, differ_frame, differ_clear_list, translation, display_tracks, blurry, \
                            blurry_text = self.frame_result_list.pop(0)
                        bug_list.extend(display_tracks)

                    if yolo_frame_index <= differ_frame_index:
                        self.abstract_bug_manager.update(yolo_frame_index, yolo_frame, outputs, others, blurry,
                                                         translation)
                        clear_list = self.abstract_bug_manager.clear()
                        self.bug_record.allocation(clear_list)

                    if differ_frame_index <= yolo_frame_index:
                        # 帧间差分法数据处理(包含绘制)
                        self.bug_record.allocation(differ_clear_list)

                    # 图像绘制
                    if self.video_display or self.video_save:
                        bug_list.extend(self.abstract_bug_manager.display_tracks())
                        if yolo_frame_index < differ_frame_index:
                            image = draw_messages(yolo_frame, self.abstract_bug_manager.display_tracks())
                        else:
                            image = draw_messages(differ_frame, self.abstract_bug_manager.display_tracks())
                    if self.video_display or self.video_save:
                        self.video_queue.put((image, blurry_text, yolo_frame_index, differ_frame_index, bug_list,
                                              deepcopy(self.bug_record.bug_numbers)))

                else:
                    if not self.sign_dict['frame_detect_sign']:
                        continue
                    else:
                        break
            except:
                print('分配器出了点问题，但是没有影响。')
        lock.acquire()
        self.sign_dict['manager_sign'] = True
        print('manager finish')
        lock.release()

    def _get_data(self):
        """
        获取输入数据
        :return:
        """
        lock.acquire()
        if not self.yolo_result_queue.empty():
            self.yolo_result_list.append(self.yolo_result_queue.get(timeout=10))
        if not self.frame_result_queue.empty():
            self.frame_result_list.append(self.frame_result_queue.get(timeout=10))
        lock.release()
