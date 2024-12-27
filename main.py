import multiprocessing
import signal
from pathlib import Path
from multiprocessing import Process, Queue, Lock
from video.video_reader import VideoReader
from video.images_video import images_to_video_recursive
from video_processing import VideoProcessing
from yolo_processing import YoloProcessing
from tools.blur_detector import BlueDetector
from tools.path_manager import PathManager, PathDir
from tools.frame_set import frame_set
from frame_differ_processing import FrameDifferProcessing
from manager_processing import ManagerProcessing
from big_microfauna.really_bug_record import ReallyBugRecord
from writer.write_to_execl import ExcelWriter, JSONWriter
from writer.write_to_others import save_blurry_list
import time
import threading
import os
import torch

lock = Lock()


def processing_forced_stop(sign_dict, processing_dict):
    """
    进程检测器（到时间进程未终止则强制杀死）
    :param sign_dict: 进程终止标志
    :param processing_dict: 进程终止标志所对应的进程l
    :return:
    """
    tack_id = sign_dict['task_id']
    if not sign_dict['finish']:
        print(f'任务{tack_id} 监测器执行')
        for key, p in processing_dict.items():
            lock.acquire()
            sign_dict[key] = True
            p.kill()
            lock.release()
        print(f'任务{tack_id} 监测器执行完毕')


if __name__ == '__main__':

    torch.multiprocessing.set_start_method('spawn', force=True)
    bd = BlueDetector(threshold=-10000)
    manager = multiprocessing.Manager()
    detect_type = 'video'  # video or real-time
    pwd = os.getcwd()
    video_display = False
    video_save = True

    error_video = []  # 需考量视频列表
    frame_interval = {}  # 视频对应检测帧区间

    # methods设置为manual表示手动设置，且人工选择是否设置起始帧、结束帧、检测帧数；auto表示自动处理；除manual、auto均为全帧检测,且帧参数均不生效
    methods = "auto"
    manual_option = "end_detect"
    start_index = 101  # 开始帧
    end_index = 300  # 结束帧980
    detect_index = 300  # 固定检测帧数

    # input_path = r'Z:\ROMIDAS0.3\ROMIDAS-NAS\D\123\impact video\pfoa'
    # output_path = r'Z:\ROMIDAS0.3\out\pfoa'
    input_path = r"Z:\ROMIDAS0.3\ROMIDAS-NAS\D\123\impact video\pfoa"
    output_path = r"Z:\ROMIDAS0.3\output_PFOA_1016"
    #input_path = r"Z:\ROMIDAS0.3\test_small"
    #output_path = r"Z:\ROMIDAS0.3\output_small"
    if detect_type == 'video':
        # path_manager = PathManager(f'{pwd}/input', f'{pwd}/output')
        path_manager = PathManager(input_path, output_path)

        for i, path_dir in enumerate(path_manager.items()):

            # 进程通信标志
            sign_dict = manager.dict({
                'task_id': i + 1,
                'finish': False,
                'video_display': video_display,
                'video_save': video_save,
                'video_input_sign': False,
                'yolo_detect_sign': False,
                'frame_detect_sign': False,
                'manager_sign': False,
                'video_manager_sign': False,
            })
            # 视频读入器
            video_reader = VideoReader(path_dir.video_input_path)
            # 进程通信队列
            yolo_result_queue = Queue(maxsize=100)
            frame_result_queue = Queue(maxsize=100)
            frame_input_queue = Queue(maxsize=100)
            yolo_input_queue = Queue(maxsize=100)
            video_queue = Queue(maxsize=100)

            # 设置进程

            # 设置视频管理器进程
            video_manager_processing = VideoProcessing(sign_dict, video_queue)
            video_manager_processing.set_fps(video_reader.fps)
            video_manager_processing.set_video_message(video_reader.video_message())
            video_manager_processing.set_video_save_path(path_dir.video_path)
            video_manager_p = Process(target=video_manager_processing.start)

            # 设置yolo检测器进程
            yolo_processing = YoloProcessing(sign_dict, yolo_result_queue, yolo_input_queue, frame_input_queue)
            yolo_p = Process(target=yolo_processing.start)

            # 设置帧差法检测器进程
            differ_processing = FrameDifferProcessing(sign_dict, frame_input_queue, frame_result_queue)
            differ_p = Process(target=differ_processing.start)

            # 数据存储对象
            bug_dead_or_live = manager.dict({
                'Ar': manager.dict({'die': 0, 'live': 0}),
                "Do": manager.dict({'die': 0, 'live': 0}),
                'Mo': manager.dict({'die': 0, 'live': 0}),
                'Ne': manager.dict({'die': 0, 'live': 0}),
                'Eu': manager.dict({'die': 0, 'live': 0}),
            })
            bug_record_dict = manager.dict({
                'Ar': manager.list(),
                "Do": manager.list(),
                'Mo': manager.list(),
                'Ne': manager.list(),
                'Eu': manager.list(),
                'Gs': manager.list(),
                "SmallProtozoa": manager.list(),
            })
            ar_colors_list = manager.list()
            gs_area_list = manager.list()

            # 初始化微生物记录器
            bug_record = ReallyBugRecord(path_dir, video_reader.video_name, video_reader.fps, video_reader.total_frames)
            bug_record.set_ar_colors_list(ar_colors_list)
            bug_record.set_gs_area_list(gs_area_list)
            bug_record.set_bug_dead_or_live(bug_dead_or_live)
            bug_record.set_bug_record(bug_record_dict)

            # 设置数据同步管理器进程
            manager_processing = ManagerProcessing(sign_dict, yolo_result_queue, frame_result_queue, video_queue,
                                                   bug_record)
            manager_p = Process(target=manager_processing.start)

            # 开启所有进程
            manager_p.start()
            yolo_p.start()
            video_manager_p.start()
            differ_p.start()

            # 开始输入数据
            video_start_time = time.time()
            print(f'第{i + 1}个视频 {video_reader.video_name} 开始时间: {time.ctime()}')
            blurry_list = []

            total_index = video_reader.total_frames
            frame_list1 = frame_set(methods, manual_option, start_index, end_index, detect_index, total_index,
                                    video_reader.video_name)
            print(frame_list1)
            if isinstance(frame_list1, list) and len(frame_list1) > 0:
                frame_interval[video_reader.video_name] = frame_list1

            for frame_index, frame in enumerate(video_reader):
                # time.sleep(0.005)

                # if frame_index % 200 == 0 and not video_display:
                # print(f'已经输入 {frame_index} 帧')
                # time.sleep(1)

                # blurry, blurry_text, blurry_mean = bd.detect(frame)
                # blurry_list.append(blurry_mean)
                # lock.acquire()
                # yolo_input_queue.put((frame_index, frame, blurry, blurry_text))
                # lock.release()

                if isinstance(frame_list1, list) and len(frame_list1) == 0:
                    blurry, blurry_text, blurry_mean = bd.detect(frame)
                    blurry_list.append(blurry_mean)
                    lock.acquire()
                    yolo_input_queue.put((frame_index, frame, blurry, blurry_text))
                    lock.release()

                    if frame_index % 200 == 0 and not video_display:
                        print(f'已经输入第 {frame_index} 帧')

                elif isinstance(frame_list1, list) and len(frame_list1) > 0:

                    if frame_list1[0] <= frame_index <= frame_list1[1]:
                        blurry, blurry_text, blurry_mean = bd.detect(frame)
                        blurry_list.append(blurry_mean)
                        lock.acquire()
                        yolo_input_queue.put((frame_index, frame, blurry, blurry_text))
                        lock.release()

                        if frame_index % 200 == 0 and not video_display:
                            print(f'已经输入第 {frame_index} 帧')

                elif isinstance(frame_list1, str):
                    if frame_list1 not in error_video:
                        error_video.append(frame_list1)

                else:
                    print("指定视频检测帧数有误")

            # 数据输入结束
            lock.acquire()
            sign_dict['video_input_sign'] = True
            lock.release()

            # 进程监测器字典
            processing_dict = {
                'yolo_detect_sign': yolo_p,
                'frame_detect_sign': differ_p,
                'manager_sign': manager_p,
                'video_manager_sign': video_manager_p,
            }
            # 开启进程监测器
            rest_length = max([yolo_input_queue.qsize(), frame_input_queue.qsize(), yolo_result_queue.qsize(),
                               frame_result_queue.qsize(), video_queue.qsize()])
            timer = threading.Timer(rest_length / 10, processing_forced_stop, args=(sign_dict, processing_dict))
            timer.start()
            # 等待所有开启的进程结束，如果到规定时间未结束，会直接杀死未结束的进程
            yolo_p.join()
            differ_p.join()
            video_manager_p.join()

            # 数据保存
            print('数据保存中')
            save_blurry_list(path_dir.blurry_path, blurry_list)
            print('模糊度列表保存完成')
            json_writer = JSONWriter(path_dir.json_path)
            json_writer.write(bug_record)
            print('json数据保存成功')
            try:
                excel_writer = ExcelWriter(path_dir.execl_path)
                excel_writer.write(bug_record)
                print('excel数据保存成功')
            except:
                print('xlwings库出现异常，excel数据保存失败')
            print('数据保存完成')
            video_end_time = time.time()
            print(f'第 {i + 1}个视频结束时间: {time.ctime()}')
            print(f'第 {i + 1}个视频检测时间: {video_end_time - video_start_time}')
            sign_dict['finish'] = True
    elif detect_type == 'real-time':

        classes_list = ['Gs', 'Mo', 'Do', 'Eu', 'Ne', 'Ar']
        path_dir = PathDir(Path(f'{pwd}/output'), 'real-time')
        video_name, fps, total_frames = 'real-time', 17.3, None
        video_message = (video_name, total_frames, fps)

        # 进程通信标志
        sign_dict = manager.dict({
            'task_id': 'real-time',
            'finish': False,
            'video_display': video_display,
            'video_save': video_save,
            'video_input_sign': False,
            'yolo_detect_sign': False,
            'frame_detect_sign': False,
            'manager_sign': False,
            'video_manager_sign': False,
        })
        # 进程通信队列
        yolo_result_queue = Queue()
        frame_result_queue = Queue()
        frame_input_queue = Queue()
        yolo_input_queue = Queue()
        video_queue = Queue()

        # 设置进程

        # 设置视频管理器进程
        video_manager_processing = VideoProcessing(sign_dict, video_queue)
        video_manager_processing.set_fps(fps)
        video_manager_processing.set_video_message(video_message)
        video_manager_processing.set_video_save_path(path_dir.video_path)
        video_manager_p = Process(target=video_manager_processing.start)

        # 设置yolo检测器进程
        yolo_processing = YoloProcessing(sign_dict, yolo_result_queue, yolo_input_queue, frame_input_queue)
        yolo_p = Process(target=yolo_processing.start)

        # 设置帧差法检测器进程
        differ_processing = FrameDifferProcessing(sign_dict, frame_input_queue, frame_result_queue)
        differ_p = Process(target=differ_processing.start)

        # 数据存储对象
        bug_dead_or_live = manager.dict({
            'Ar': manager.dict({'die': 0, 'live': 0}),
            "Do": manager.dict({'die': 0, 'live': 0}),
            'Mo': manager.dict({'die': 0, 'live': 0}),
            'Ne': manager.dict({'die': 0, 'live': 0}),
            'Eu': manager.dict({'die': 0, 'live': 0}),
        })
        bug_record_dict = manager.dict({
            'Ar': manager.list(),
            "Do": manager.list(),
            'Mo': manager.list(),
            'Ne': manager.list(),
            'Eu': manager.list(),
            'Gs': manager.list(),
            "SmallProtozoa": manager.list(),
        })
        ar_colors_list = manager.list()
        gs_area_list = manager.list()

        # 初始化微生物记录器
        bug_record = ReallyBugRecord(path_dir, video_name, fps, total_frames)
        bug_record.set_ar_colors_list(ar_colors_list)
        bug_record.set_gs_area_list(gs_area_list)
        bug_record.set_bug_dead_or_live(bug_dead_or_live)
        bug_record.set_bug_record(bug_record_dict)

        # 设置数据同步管理器进程
        manager_processing = ManagerProcessing(sign_dict, yolo_result_queue, frame_result_queue, video_queue,
                                               bug_record)
        manager_p = Process(target=manager_processing.start)

        # 开启所有进程
        manager_p.start()
        yolo_p.start()
        video_manager_p.start()
        differ_p.start()

        # 数据输入
        pass

    else:
        print('检测类型错误')
    # root_path = r".\output"
    # txt_path = r".\output\record.txt"
    root_path = output_path
    txt_path = os.path.join(output_path, "record.txt")
    # txt_path = r"Z:\ROMIDAS0.3\out\Cu2\record.txt"
    images_to_video_recursive(root_path, txt_path)
    print('finish')
    print("需重新考量的视频:", error_video)
    print("视频对应检测帧区间：", frame_interval)
    main_pid = os.getpid()
    os.kill(main_pid, signal.SIGINT)
