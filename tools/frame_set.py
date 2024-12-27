def frame_set(methods, manual_option, start_index, end_index, detect_index, total_index, name):
    """
    指定视频帧数检测
    输入视频帧数，提供两种方式
    - "manual": 手动设置起始帧，根据manual_option有三种选择
        - 'start_detect': 返回起始帧和检测帧数
        - 'end_detect': 返回结束帧和检测帧数
        - 'start_end': 返回起始帧和结束帧
    - "auto": 自动化处理
    :param methods:检测视频方式
    :param manual_option:手动检测方式
    :param start_index:起始帧号
    :param end_index:结束帧号
    :param detect_index:固定帧数
    :param total_index:视频总帧数
    :param name:视频名称
    """
    if methods == "manual":
        if start_index > end_index or detect_index > end_index:
            print("帧数大小设置有误")
        try:
            if manual_option == "start_detect":  # 选择1: 起始帧号和固定帧数
                detect_count = start_index + detect_index
                return [start_index, detect_count]
            elif manual_option == "end_detect":  # 选择2: 结束帧号和固定帧数
                detect_count = end_index - detect_index
                return [detect_count, end_index]
            elif manual_option == "start_end":  # 选择3: 起始帧号和结束帧号
                return [start_index, end_index]
            else:
                return name
        except Exception as e:
            print(f"视频{name}无法满足帧数要求，请重新考量")
            return name

    elif methods == "auto":
        if 30000 >= total_index >= 20000:
            a = (total_index - 20000) // 2
            return [a, a + 19999]
        else:
            return name

    else:
        return []
