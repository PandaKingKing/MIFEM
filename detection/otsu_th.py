import numpy as np
import cv2
import matplotlib.pyplot as plt


def otsu_th(src,
            w=0.3,
            max_th=170,
            vis=False):
    bins = np.arange(256)
    hist = cv2.calcHist([src], [0], None, [256], [0, 256])
    hist_norm = hist.ravel() / hist.max()
    Q = hist_norm.cumsum()
    fn_min = np.inf
    thresh = -1
    l = np.nonzero(hist_norm)[0][0]
    u = np.nonzero(hist_norm)[0][-1]
    m = np.sum(bins * hist_norm) / np.sum(hist_norm)
    m_norm = (m - l) / (u - l)
    print(f'{m_norm=:.2f}')
    # if m_norm < 0.4:
    #     weight = w * m_norm
    # elif m_norm > 0.7:
    #     weight = max(1 - w2 * (1 - m_norm), 0)
    # else:
    #     weight = 0.5
    weight = 0.5
    for i in range(1, 256):
        p1, p2 = np.hsplit(hist_norm, [i])  # 概率
        q1, q2 = Q[i], Q[255] - Q[i]  # 对类求和
        if q1 == 0 or q2 == 0:
            continue
        b1, b2 = np.hsplit(bins, [i])  # 权重
        # 寻找均值和方差
        m1, m2 = np.sum(p1 * b1) / q1, np.sum(p2 * b2) / q2
        v1, v2 = np.sum(((b1 - m1) ** 2) * p1) / q1, np.sum(((b2 - m2) ** 2) * p2) / q2
        # 计算最小化函数
        # m = np.sum(bins * hist_norm) / np.sum(hist_norm)
        # m_norm = (m - m1) / (m2 - m1)
        # weight = m_norm
        # # if m_norm < 0.4:
        # #     weight = w1 * m_norm
        # # elif m_norm > 0.6:
        # #     weight = 1 - w2 * (1 - m_norm)
        # # else:
        # #     weight = 0.5
        fn = weight * v1 * q1 + (1 - weight) * v2 * q2
        if fn < fn_min:
            fn_min = fn
            mu1, mu2 = int(m1), int(m2)
            thresh = i
    # if m_norm > 0.7:
    #     thresh = min(thresh, max_th)
    if vis:
        plt.plot(bins, hist, '-', mu1, hist[mu1], 'o', mu2, hist[mu2], 'o', l, hist[l], 'x', u, hist[u], 'x')
        plt.vlines(thresh, 0, np.max(hist), 'r')
        plt.xlim(0, 256)
        plt.ylim(0, np.max(hist))
        plt.title(f"mean={m_norm:.2f}, weight={weight:.2f}, threshhold={thresh:.2f}")
        plt.show()
    return thresh
