import os
import cv2
from tqdm import tqdm


def images_to_video_recursive(root_folder, txt_file, fps=17):
    """
    递归遍历文件夹中的图片序列，并整合为视频
    :param root_folder: 根文件夹路径
    :param txt_file: 记录已遍历文件夹的txt文件路径
    :param fps: 视频的帧率，默认为17
    :return: None
    """
    # 检查txt文件是否存在，如果不存在则创建一个新的txt文件
    if not os.path.exists(txt_file):
        with open(txt_file, 'w') as f:
            pass

    # 读取已遍历的文件夹列表
    with open(txt_file, 'r') as f:
        traversed_folders = f.read().splitlines()

    # 遍历根文件夹下的所有子文件夹
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)

        # 如果文件夹已经遍历过，则跳过
        if folder_path in traversed_folders:
            continue

        # 如果是文件夹，则继续递归遍历
        if os.path.isdir(folder_path):
            images_folder = os.path.join(folder_path, 'images')

            # 如果images文件夹存在且没被遍历过，则将其中的图片转换为视频
            if os.path.exists(images_folder) and images_folder not in traversed_folders and len(os.listdir(images_folder)) > 0:
                video_name = os.path.basename(os.path.dirname(images_folder)) +'_result' + '.mp4'
                output_folder = os.path.join(os.path.dirname(images_folder), 'video')
                os.makedirs(output_folder, exist_ok=True)
                video_path = os.path.join(output_folder, video_name)
                images_to_video(images_folder, video_path, fps)

                # 记录已遍历的文件夹
                with open(txt_file, 'a') as f:
                    f.write(images_folder + '\n')

            # 继续递归遍历下一个文件夹
            images_to_video_recursive(folder_path, txt_file, fps)


def images_to_video(image_folder, video_path, fps=17):
    """
    将图片序列整合为视频
    :param image_folder: 包含图片的文件夹路径
    :param video_path: 输出视频的路径
    :param fps: 视频的帧率，默认为17
    :return: None
    """
    image_files = os.listdir(image_folder)
    image_files = sorted(image_files, key=lambda x: int(x.split("_")[1].split(".")[0]))  # 按数字进行排序
    frame = cv2.imread(os.path.join(image_folder, image_files[0]))
    height, width, _ = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for image_file in tqdm(image_files, desc='Converting images to video'):
        image_path = os.path.join(image_folder, image_file)
        frame = cv2.imread(image_path)
        video_writer.write(frame)

    video_writer.release()


if __name__ == '__main__':
    # # 示例用法
    # image_folder = "/root/home/MIFEM/output/2023-9-21/230402092944_origin.avi/images"
    # video_path = "/root/home/MIFEM/output/2023-9-21/230402092944_origin.avi/video/1.mp4"
    # images_to_video(image_folder, video_path)
    root_path = "/root/home/MIFEM/output"
    txt_path = "/root/home/MIFEM/output/record.txt"
    images_to_video_recursive(root_path, txt_path)
