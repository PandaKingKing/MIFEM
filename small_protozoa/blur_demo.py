import cv2
import numpy as np


def _detect_blur_fft(image, size = 60):
    """
    计算模糊度
    :param image: 图像
    :return: (模糊度值, 是否模糊)
    """
    h, w = image.shape[:2]
    (cX, cY) = (int(w / 2.0), int(h / 2.0))

    fft = np.fft.fft2(image)
    fft_shift = np.fft.fftshift(fft)

    fft_shift[cY - size:cY + size, cX - size:cX + size] = 0
    fft_shift = np.fft.ifftshift(fft_shift)
    recon = np.fft.ifft2(fft_shift)

    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)

    return mean


def calculate_blur_score(image, x, y, x1, y1):
    # 提取矩形框内的区域
    roi = image[y:y1, x:x1]
    # 转换为灰度图像
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # 计算模糊度值
    mean= _detect_blur_fft(gray_roi)

    return mean

if __name__ == '__main__':
    # 示例图像
    image = cv2.imread('/root/home/MIFEM/output/2024-2-27/1_345.mp4/images/frame_34.jpg')
    # 矩形框的坐标
    x, y, x1, y1 = 766, 664, 827, 719
    # 计算模糊度
    blur_score= calculate_blur_score(image, x, y, x1, y1)
    print(f"Blur score of the region: {blur_score}")
