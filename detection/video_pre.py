import numpy as np
import cv2
import matplotlib.pyplot as plt
import csv
from pathlib import Path

from .image_pre import image_pre


def video_pre(video_path, gap=3, blur_th=9, std_th=20, vis=False, save_img=False, save_csv=False, save_root='result/'):
    """
    对视频进行标准化预处理与筛选，存储为图片数据集

    Parameters
    ----------
    video_path: Path or str
        视频路径
    gap: int, optional
        间隔读取的帧数
    blur_th: float, optional
        模糊度阈值，保留模糊度大于该阈值的视频帧
    std_th: float, optional
        图像标准差阈值，用于剔除全白或全黑的图像
    vis: bool, optional
        是否可视化
    save_img: bool, optional
        是否将筛选后的视频帧写入图像文件
    save_csv: bool, optional
        是否将计算结果存入CSV文件
    save_root: Path or str, optional
        存储路径

    Returns
    -------
    valid_id:
        返回有效帧序号的列表
    """
    video_path, save_root = Path(video_path), Path(save_root)
    vid_name = video_path.stem
    # save_dir = save_dir / time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    save_dir = save_root / vid_name
    if save_img or save_csv:
        save_dir.mkdir(parents=True, exist_ok=True)
        if save_csv:
            res_f = (save_dir / 'pre_res.csv').open('w', encoding="UTF8", newline="")
            csv_writer = csv.writer(res_f)
            csv_writer.writerow(['frame-id', 'is-save', 'blur', 'std'])

    cap = cv2.VideoCapture(str(video_path))
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # w, h, fps = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FPS)
    # out = cv2.VideoWriter(str(save_dir / ''))
    assert cap.isOpened(), "Failed to open the video file!"
    if vis:
        cv2.namedWindow("video", cv2.WINDOW_NORMAL)
        if cv2.waitKey(0) == ord('q'):
            exit(0)
    valid_id = []
    while True:
        frame_id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        ret = cap.grab()
        if not ret:
            break
        if frame_id % gap == 0:
            ret, frame = cap.retrieve()
            flag, blur, std = image_pre(frame, blur_th=blur_th, std_th=std_th, vis=False, save=save_img,
                                        save_path=save_dir / f"{vid_name}_{frame_id}.jpg")
            if save_csv:
                csv_writer.writerow([frame_id, flag, blur, std])
            if flag:
                if vis:
                    cv2.putText(frame, "HD", (300, 900), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 5)
                valid_id.append(frame_id)
            if vis:
                cv2.putText(frame, f"blur={blur:.2f}", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
                cv2.putText(frame, f"std={std:.2f}", (300, 600), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
                cv2.imshow("video", frame)
                kk = cv2.waitKey(1) & 0xff
                if kk == ord('p'):
                    cv2.waitKey(0)
                if kk == ord('q'):
                    frame_id += gap
                    break

    print(f"\nTotal Number of Frames: {frame_id // gap:.0f}")
    print(f"Number of Frames without blur: {len(valid_id)}")
    cv2.destroyAllWindows()
    cap.release()
    if save_csv:
        res_f.close()

    return valid_id


if __name__ == "__main__":
    root = Path('../video/')
    vids = [p for p in root.glob('*.mp4')]
    video_pre(vids[3], vis=True, save_img=True)

"""
0:'伸缩运动+虫子运动轨迹+模糊.mp4', 
1:'伸缩运动+虫子运动轨迹+部分模糊.mp4', 
2:'光线改变.mp4', 
3:'焦距调节.mp4', 
4:'移动方向改变.mp4', 
5:'运动中正常拍摄的视频.mp4', 
6:'运动轨迹.mp4'
"""
