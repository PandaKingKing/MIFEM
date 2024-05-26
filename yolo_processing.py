from yolo_detect.yolo import YoloDetector
from multiprocessing import Lock

# import logging

# 配置日志记录
# logging.basicConfig(level=logging.INFO, filename='app_frame.log', filemode='a',
#                     format='%(asctime)s - %(levelname)s - %(message)s')

lock = Lock()


class YoloProcessing:
    """
    大虫子进程类
    """

    def __init__(self, sign_dict, yolo_result_queue, yolo_input_queue, frame_input_queue):
        """

        :param sign_dict: 进程通信标记
        :param yolo_result_queue: yolo结果队列
        :param yolo_input_queue: yolo输入队列
        :param frame_input_queue: 帧差法输入队列
        """
        self.sign_dict = sign_dict
        self.yolo_result_queue = yolo_result_queue
        self.yolo_input_queue = yolo_input_queue
        self.frame_input_queue = frame_input_queue
        self.yolo_input_list = []  # yolo输入数据储存列表

    def start(self):
        """
        进程开启接口
        :return:
        """
        yolo_detector = YoloDetector()
        while True:
                self._get_data()
            # try:
                if len(self.yolo_input_list) > 0:
                    frame_index, frame, blurry, blurry_text = self.yolo_input_list.pop(0)
                    frame_index, outputs, others = yolo_detector.detect(frame_index, frame)
                    if frame_index % 2 == 0:
                        cls_list = [other.cls for other in others]
                        # logging.info(f'帧差法输入：{frame_index}, {outputs}, {cls_list}')
                        self._set_frame_input_queue((frame_index, frame, blurry, blurry_text, outputs, others))
                    self._set_result_queue((frame_index, frame, outputs, others, blurry, blurry_text))
                    # # 指定文件夹路径和文件名
                    # folder_path = '/root/home/MIFEM/result'
                    # file_name = 'yolo_result.txt'
                    # if not os.path.exists(folder_path):
                    #     # 创建文件夹（如果不存在）
                    #     os.makedirs(folder_path, exist_ok=True)

                    # # 构建完整的文件路径
                    # file_path = os.path.join(folder_path, file_name)

                    # # 将数据保存到文本文件
                    # with open(file_path, 'a') as f:
                    #     f.write(f'frame_index: {frame_index}\n')
                    #     f.write(f'outputs: {outputs}\n')

                else:
                    if not self.sign_dict['video_input_sign']:
                        continue
                    else:
                        break
            # except:
            #     print('yolo检测器出了一点问题，但是没有影响。')
        # 更改完成标志
        lock.acquire()
        self.sign_dict['yolo_detect_sign'] = True
        print('yolo detect finish')
        lock.release()

    def _get_data(self):
        """
        获取输入数据
        :return:
        """
        lock.acquire()
        if not self.yolo_input_queue.empty():
            self.yolo_input_list.append(self.yolo_input_queue.get(timeout=10))
        lock.release()

    def _set_frame_input_queue(self, result):
        """
        向帧差法输入队列放入数据
        :param result: 待放入的数据
        :return:
        """
        lock.acquire()
        self.frame_input_queue.put(result)
        lock.release()

    def _set_result_queue(self, result):
        """
        向yolo结果队列放入数据
        :param result: 待放入的数据
        :return:
        """
        lock.acquire()
        self.yolo_result_queue.put(result)
        lock.release()
