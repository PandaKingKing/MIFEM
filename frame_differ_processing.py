from small_protozoa.small_protozoa_detect import FrameDifferDetector
from multiprocessing import Lock

lock = Lock()


class FrameDifferProcessing:
    """
    小虫子检测进程
    """

    def __init__(self, sign_dict, frame_input_queue, frame_result_queue):
        """

        :param sign_dict: 进程通信标记
        :param frame_input_queue: 帧差法输入队列
        :param frame_result_queue: 帧差法结果队列
        """
        self.sign_dict = sign_dict
        self.frame_input_queue = frame_input_queue
        self.frame_result_queue = frame_result_queue
        self.frame_input_list = []

    def start(self):
        """
        开始进程
        :return:
        """
        small_protozoa_detect = FrameDifferDetector()
        while not self.sign_dict['frame_detect_sign']:
            self._get_data()
            # try:
            if len(self.frame_input_list) > 0:
                frame_index, frame, blurry, blurry_text, outputs, others = self.frame_input_list.pop(0)
                # 检测
                result = small_protozoa_detect.detect(blurry, frame_index, frame, outputs, others)
                self._set_result_queue((*result, blurry, blurry_text))
            else:
                if not self.sign_dict['yolo_detect_sign']:
                    continue
                else:
                    break
            # except:
            #     print('帧差法检测器出了一些问题，但是没有影响。')
        lock.acquire()
        self.sign_dict['frame_detect_sign'] = True
        print('frame differ finish')
        lock.release()

    def _get_data(self):
        """
        获取输入数据
        :return:
        """
        lock.acquire()
        if not self.frame_input_queue.empty():
            self.frame_input_list.append(self.frame_input_queue.get())
        lock.release()

    def _set_result_queue(self, result):
        """
        向帧差法结果队列放入数据
        :param result: 需要放入的数据
        :return:
        """
        lock.acquire()
        self.frame_result_queue.put(result)
        lock.release()
