import numpy as np
import torch

from .deep.feature_extractor import Extractor
from .sort.nn_matching import NearestNeighborDistanceMetric
from .sort.preprocessing import non_max_suppression
from .sort.detection import Detection
from .sort.tracker import Tracker

__all__ = ['DeepSort']


class DeepSort(object):
    def __init__(self, model_path, max_dist=0.2, min_confidence=0.3, nms_max_overlap=1.0, max_iou_distance=0.7,
                 max_age=30, n_init=3, nn_budget=100, use_cuda=True):
        self.min_confidence = min_confidence
        self.nms_max_overlap = nms_max_overlap
        self.model_path = model_path
        self.use_cuda = use_cuda
        self.extractor = Extractor(model_path, use_cuda=use_cuda)

        max_cosine_distance = max_dist
        nn_budget = nn_budget
        metric = NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)

        # tracker maintain a list contains(self.tracks) for each Track object
        self.tracker = Tracker(metric, max_iou_distance=max_iou_distance, max_age=max_age, n_init=n_init)

        self.reload = False

    def update(self, bbox_xywh, confidences, ori_img, others, frame_index):

        self.height, self.width = ori_img.shape[:2]

        # get appearance feature with neural network (Deep) *********************************************************
        features = self._get_features(bbox_xywh, ori_img) # 后续匹配

        bbox_tlwh = self._xywh_to_tlwh(bbox_xywh)  # # [cx,cy,w,h] -> [x1,y1,w,h]   top left

        #  generate detections class object for each person *********************************************************
        # filter object with less confidence
        # each Detection obj maintain the location(bbox_tlwh), confidence(conf), and appearance feature
        detections = [Detection(bbox_tlwh[i], conf, features[i], others[i]) for i, conf in enumerate(confidences) if
                      conf > self.min_confidence]
        # run on non-maximum supression (useless) *******************************************************************
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = non_max_suppression(boxes, self.nms_max_overlap, scores)  # Here, nms_max_overlap is 1
        detections = [detections[i] for i in indices]
        # update tracker ********************************************************************************************
        self.tracker.predict()  # predict based on t-1 info
        # for first frame, this function do nothing

        for track in self.tracker.tracks:

            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            
            
            # print(frame_index, track.mean)

        # detections is the measurement results as time T
        self.tracker.update(detections)
        # for detection in detections:
        #     print(frame_index, detection.tlwh)
        
        # print(frame_index, boxes)
        # output bbox identities ************************************************************************************
        outputs = []
        others = []

        for track in self.tracker.tracks:

            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            
            box = track.to_tlwh()  # (xc,yc,a,h) to (x1,y1,w,h)

            # print(frame_index, box)
            # ****************************************************************
            # save_det = "/root/home/MIFEM/result/det.txt"
            # with open(save_det, 'a') as f:
            #     f.write(f'frame_index: {frame_index}\n')
            #     for det_info in box:
            #         det_info1 = ','.join(str(coord) for coord in det_info)
            #         f.write(det_info1 + '\n')

            x1, y1, x2, y2 = self._tlwh_to_xyxy(box)
            track_id = track.track_id
            outputs.append(np.array([x1, y1, x2, y2, track_id], dtype=np.int32))
            others.append(track.other)
        if len(outputs) > 0:
            outputs = np.stack(outputs, axis=0)  # (#obj, 5) (x1,y1,x2,y2,ID)
        else:
            outputs = np.zeros((0, 5))

        return outputs, others

    """
    TODO:
        Convert bbox from xc_yc_w_h to xtl_ytl_w_h
    Thanks JieChen91@github.com for reporting this bug!
    """

    @staticmethod
    def _xywh_to_tlwh(bbox_xywh):
        if isinstance(bbox_xywh, np.ndarray):
            bbox_tlwh = bbox_xywh.copy()
        elif isinstance(bbox_xywh, torch.Tensor):
            bbox_tlwh = bbox_xywh.clone()
        bbox_tlwh[:, 0] = bbox_xywh[:, 0] - bbox_xywh[:, 2] / 2.
        bbox_tlwh[:, 1] = bbox_xywh[:, 1] - bbox_xywh[:, 3] / 2.
        return bbox_tlwh

    def _xywh_to_xyxy(self, bbox_xywh):
        x, y, w, h = bbox_xywh
        x1 = max(int(x - w / 2), 0)
        x2 = min(int(x + w / 2), self.width - 1)
        y1 = max(int(y - h / 2), 0)
        y2 = min(int(y + h / 2), self.height - 1)
        return x1, y1, x2, y2

    def _tlwh_to_xyxy(self, bbox_tlwh):
        """
        TODO:
            Convert bbox from xtl_ytl_w_h to xc_yc_w_h
        Thanks JieChen91@github.com for reporting this bug!
        """
        x, y, w, h = bbox_tlwh
        x1 = max(int(x), 0)
        x2 = min(int(x + w), self.width - 1)
        y1 = max(int(y), 0)
        y2 = min(int(y + h), self.height - 1)
        return x1, y1, x2, y2

    def _xyxy_to_tlwh(self, bbox_xyxy):
        x1, y1, x2, y2 = bbox_xyxy

        t = x1
        l = y1
        w = int(x2 - x1)
        h = int(y2 - y1)
        return t, l, w, h

    def _get_features(self, bbox_xywh, ori_img):
        import cv2
        im_crops = []
        l = []
        for box in bbox_xywh:
            x1, y1, x2, y2 = self._xywh_to_xyxy(box)
            im = ori_img[y1:y2, x1:x2]
            im_crops.append(im)
            l.append((y1, y2, x1, x2))
        if im_crops:
            # for index, image in enumerate(im_crops):
            #     try:
            #         cv2.resize(image.astype(np.float32)/255., (64, 128))
            #     except:
            #         print(l[index])
            features = self.extractor(im_crops)
        else:
            features = np.array([])
        return features
