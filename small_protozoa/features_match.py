import numpy as np
import cv2
import threading

orb = cv2.ORB_create()


def create(src, result):
    """
    用于加速的函数
    :param src: 图像
    :param result: 结果
    :return: None
    """
    result[0], result[1] = orb.detectAndCompute(src, None)


def calc_translation(src1, src2, method='orb'):
    """
    位移矢量的计算
    :param src1: 前一帧
    :param src2: 当前帧
    :param method: 计算方法(不用动)
    :return: (位移矢量，前一阵灰度图，当前帧灰度图)
    """
    translation = ()
    try:
        MIN_MATCH_COUNT = 10
        if len(src1.shape) > 2:
            src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
        if len(src2.shape) > 2:
            src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        if method == 'sift':
            sift = cv2.SIFT_create()
            kp1, des1 = sift.detectAndCompute(src1, None)
            kp2, des2 = sift.detectAndCompute(src2, None)
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        else:
            # orb = cv2.ORB_create()
            #
            # kp1, des1 = orb.detectAndCompute(src1, None)
            # kp2, des2 = orb.detectAndCompute(src2, None)
            result1 = [0, 0]
            result2 = [0, 0]
            t1 = threading.Thread(target=create, args=(src1, result1))
            t2 = threading.Thread(target=create, args=(src2, result2))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            (kp1, des1), (kp2, des2) = result1, result2

            FLANN_INDEX_LSH = 6
            index_params = dict(algorithm=FLANN_INDEX_LSH,
                                table_number=6,
                                key_size=12,
                                multi_probe_level=2)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        good = []
        for m in matches:
            if len(m) == 2:
                if m[0].distance < 0.7 * m[1].distance:
                    good.append(m[0])
        if len(good) > MIN_MATCH_COUNT:

            # x_t = np.median([(kp2[m.trainIdx].pt[0] - kp1[m.queryIdx].pt[0]) for m in good])
            x_t = np.mean([(kp2[m.trainIdx].pt[0] - kp1[m.queryIdx].pt[0]) for m in good])
            # y_t = np.median([(kp2[m.trainIdx].pt[1] - kp1[m.queryIdx].pt[1]) for m in good])
            y_t = np.mean([(kp2[m.trainIdx].pt[1] - kp1[m.queryIdx].pt[1]) for m in good])

            H = np.array([[1, 0, x_t],
                          [0, 1, y_t]])
            translation = (x_t, y_t)

            src1 = cv2.warpAffine(src1, H, src1.shape[::-1])

        else:
            pass

    except Exception as e:
        print('My Exception: ', e)

    return translation, src1, src2
