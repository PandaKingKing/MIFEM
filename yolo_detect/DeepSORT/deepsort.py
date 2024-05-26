import sys
import torch
from pathlib import Path

root = Path(__file__).parent
sys.path.append(str(root))
from deep_sort import build_tracker
from deepsort_utils import scale_boxes, xyxy2xywh, get_config


class OtherMessage:
    """
    自定义额外参数
    """

    def __init__(self, cls, bug_nums):
        self.cls = cls
        self.bug_nums = bug_nums


class DeepSORT:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    cfg_path = str(root / 'configs/deep_sort.yaml')
    use_cuda = device.type != 'cpu'
    cfg = get_config()
    cfg.merge_from_file(cfg_path)

    def __init__(self):

        self.deepsort = build_tracker(self.cfg, use_cuda=self.use_cuda)

    def image_track(self, det, bug_nums, img, new_shape, ori_shape, frame_index):

        if det is not None and len(det):  # det: (#obj, 6)  x1 y1 x2 y2 conf cls

            # Rescale boxes from img_size to original im0 size
            det[:, :4] = scale_boxes(new_shape, det[:, :4], ori_shape).round()

            # save_det = "/root/home/MIFEM/result/det.txt"
            # with open(save_det, 'a') as f:
            #     f.write(f'frame_index: {frame_index}\n')
            #     for det_info in det:
            #         det_info1 = ','.join(str(coord) for coord in det_info)
            #         f.write(det_info1 + '\n')
 
            det = det[det[:, 1] > 30]  # 去除上边界碰到屏幕边缘的检测框

            bbox_xywh = xyxy2xywh(det[:, :4]).cpu()

            # for a, b in zip(bbox_xywh, det):
            #     print(a, b)
            confs = det[:, 4:5].cpu()
            others = [OtherMessage(cls, bug_num) for cls, bug_num in zip(det[:, 5].cpu(), bug_nums)]
            # ****************************** deepsort ****************************

            outputs, others = self.deepsort.update(bbox_xywh, confs, img, others, frame_index)
            # (#ID, 5) x1,y1,x2,y2,track_ID
        else:
            outputs = torch.zeros((0, 5))
            others = []
        return outputs, others


if __name__ == '__main__':
    d = DeepSORT()
