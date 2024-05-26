import numpy as np
import cv2
import imutils


class BlueDetector:
    """
    模糊度检测
    详见 https://github.com/SrikanthIITB/Fast-Fourier-Transform-FFT-for-blur-detection-in-images-and-video
    """

    def __init__(self, size=60, threshold=10):
        self.size = size
        self.threshold = threshold

    def _detect_blur_fft(self, image):
        """
        计算模糊度
        :param image: 图像
        :return: (模糊度值, 是否模糊)
        """
        h, w = image.shape
        (cX, cY) = (int(w / 2.0), int(h / 2.0))

        fft = np.fft.fft2(image)
        fft_shift = np.fft.fftshift(fft)

        fft_shift[cY - self.size:cY + self.size, cX - self.size:cX + self.size] = 0
        fft_shift = np.fft.ifftshift(fft_shift)
        recon = np.fft.ifft2(fft_shift)

        magnitude = 20 * np.log(np.abs(recon))
        mean = np.mean(magnitude)

        return mean, mean <= self.threshold

    def detect(self, frame):
        """
        模糊度检测接口
        :param frame: 图像
        :return: (是否模糊,模糊度文本信息,模糊度值)
        """
        frame = imutils.resize(frame, width=500)

        # convert the frame to grayscale and detect blur in it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean, blurry = self._detect_blur_fft(gray)
        text = f"Blurry ({mean:.4f})" if blurry else f"Not Blurry ({mean:.4f})"

        return blurry, text, round(float(mean), 2)
