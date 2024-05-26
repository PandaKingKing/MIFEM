import torch
from sklearn.cluster import dbscan


def cluster(predict_boxs):
    """
    聚类函数
    :param predict_boxs: 预测框
    :return:
    """
    point_list = [((p.tolist()[0] + p.tolist()[2]) / 2, (p.tolist()[1] + p.tolist()[3]) / 2) for p in predict_boxs]
    eps = 2
    _, labels = dbscan(point_list, eps=eps, min_samples=1)
    # print(labels)
    clss = set(labels)
    index_list = []
    for cls in clss:
        index_list.append((torch.tensor(labels.copy()) == cls).cuda())
    return index_list


def merge_prediction_box(prediction_box, cls):
    """
    GS聚类
    :param prediction_box: 预测框
    :param cls: 聚类的类别
    :return: 聚类后的微生物信息
    """
    cls_index = prediction_box[:, -1] == cls
    if torch.any(cls_index):
        result = prediction_box[cls_index == 0]
        index_list = cluster(prediction_box[cls_index])
        bug_nums = [1] * len(result)
        for index in index_list:
            if len(index):
                bug_nums.append(len(index))
                temp_index = cls_index.clone()
                temp_index[cls_index] = index
                result = torch.cat([result, torch.cat([
                    torch.min(prediction_box[temp_index, :2], dim=0).values,
                    torch.max(prediction_box[temp_index, 2:4], dim=0).values,
                    torch.mean(prediction_box[temp_index, 4:], dim=0)
                ], dim=0).unsqueeze(dim=0)], dim=0)
        prediction_box = result
        return prediction_box, bug_nums
    bug_nums = [1] * len(prediction_box)
    return prediction_box, bug_nums
