import numpy as np
import cv2
import matplotlib.pyplot as plt


def cal_blur(src, size=200):
    """
    计算图像模糊度

    Parameters
    ----------
    src: ndarray
        输入的图像
    size: int, optional
        FFT频谱中去掉低频分量的范围

    Returns
    -------
    blur_value: float
        返回模糊度数值，该值越小说明图像越模糊
    """
    if len(src.shape) > 2:
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        gray = src.copy()
    # blur_value = cv2.Laplacian(gray, cv2.CV_64F).var()

    h, w = gray.shape
    h_dft, w_dft = cv2.getOptimalDFTSize(h), cv2.getOptimalDFTSize(w)
    # src_dft = np.zeros((h_dft, w_dft))
    # src_dft[:h, :w] = gray
    cx, cy = int(w_dft / 2), int(h_dft / 2)
    dft = np.fft.fft2(gray, (h_dft, w_dft))  # flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # print(dft_shift.shape)
    dft_shift[cy - size:cy + size, cx - size:cx + size] = 0
    dft_shift = np.fft.ifftshift(dft_shift)
    recon = np.fft.ifft2(dft_shift)
    magnitude = 20 * np.log(np.abs(recon))  # cv2.magnitude(recon[:, :, 0], recon[:, :, 1]))
    blur_value = np.mean(magnitude)
    return blur_value


if __name__ == "__main__":
    # img = cv2.imread("sample/sample6.jpg")
    # blur = cal_blur(img)
    # print(f"{blur=:.2f}")
    #
    # cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    # cv2.imshow("image", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    for i in range(4):
        blur_img = cv2.imread(f"sample/blur{i + 1}.jpg")
        norm_img = cv2.imread(f"sample/sample{i + 4}.jpg")
        blur1 = cal_blur(blur_img)
        blur2 = cal_blur(norm_img)
        plt.subplot(2, 4, i + 1)
        plt.imshow(blur_img)
        plt.title(f"blur1={blur1:.2f}")
        plt.subplot(2, 4, i + 5)
        plt.imshow(norm_img)
        plt.title(f"blur2={blur2:.2f}")

    plt.show()
