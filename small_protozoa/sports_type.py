def is_same(output1, output2):
    x1, y1 ,x2, y2, task_id1 = output1.tolist()
    x3, y3 ,x4, y4, task_id2 = output2.tolist()

    inter_area = max(0, min(x2, x4) - max(x1, x3)) * max(0, min(y2, y4) - max(y1, y3))
    # 计算并集面积
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x4 - x3) * (y4 - y3)
    union_area = box1_area + box2_area - inter_area
    # 计算重叠面积比例
    iou = inter_area / union_area
    
    return iou