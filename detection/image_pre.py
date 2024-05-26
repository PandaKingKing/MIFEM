import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

from .cal_blur import cal_blur


def image_pre(src, crop=0, blur_th=9, std_th=20, vis=False, save=False, save_path='./result.jpg'):
    """
    对单张图片进行标准化预处理与筛选

    Parameters
    ----------
    src: ndarray
        输入图片
    crop: float, optional
        裁去边框的比例
    blur_th: float, optional
        模糊度阈值，保留模糊度大于该阈值的输入
    std_th: float, optional
        图像标准差阈值，用于剔除全白或全黑的图像
    vis: bool, optional
        是否可视化
    save: bool, optional
        是否保存
    save_path: Path or str, optional
        保存路径

    Returns
    -------
    return: (bool, float, float)
        图片是否达标的标志`flag`、模糊度计算结果`blur`、标准差计算结果`std`
    """
    flag, save_path = False, str(save_path)
    h, w = src.shape[:2]
    img = src[int(crop * h):int((1 - crop) * h), int(crop * w):int((1 - crop) * w)]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) > 2 else img.copy()
    blur = cal_blur(gray)
    std = gray.std()

    if blur > blur_th and std > std_th:
        flag = True
        if save:
            # cv2.imwrite(save_path + f"pic{valid}.jpg", frame)
            cv2.imencode('.jpg', src)[1].tofile(save_path)

    if vis:
        cv2.namedWindow("origin", cv2.WINDOW_NORMAL)
        cv2.imshow("origin", src)
        print(f"blur={blur:.2f}, std={std:.2f}")
        cv2.putText(img, f"blur={blur:.2f}", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        cv2.putText(img, f"std={std:.2f}", (300, 600), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        cv2.namedWindow("cropped", cv2.WINDOW_NORMAL)
        cv2.imshow("cropped", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print('*', end='')
    return flag, blur, std


if __name__ == "__main__":
    img = cv2.imread("sample/sample8.jpg")
    image_pre(img, vis=True)
