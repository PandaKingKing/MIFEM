import cv2
from copy import deepcopy


def draw_messages(frame, bug_list):
    """
    绘制大虫子检测信息
    :param frame: 需要绘制的视频帧
    :param bug_list: 被检测到的大虫子信息
    :return: 绘制好的图像
    """
    image = deepcopy(frame)

    for bug in bug_list:
        if bug.detection_sequence[-1]:
            cls = bug.cls()
            x1, y1, x2, y2 = bug.bbox_list[-1]
            label = f'{cls} {bug.track_id}'
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 3)  # 框
            cv2.putText(image, label, (x1 - 20, y1 - 10), cv2.FONT_ITALIC, 1, [0, 0, 255], 3)
    return image
