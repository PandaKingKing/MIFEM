from .deep_sort import DeepSort
from pathlib import Path

root = Path(__file__).parent

__all__ = ['DeepSort', 'build_tracker']
model_path = r'.\yolo_detect\DeepSORT\deep_sort\deep\checkpoint\ckpt.t7'


def build_tracker(cfg, use_cuda):
    return DeepSort(model_path,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=use_cuda)
