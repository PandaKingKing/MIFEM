import os
import re
import csv
from write_to_execl import JSONWriter


class CollectCSV:
    FIRST_ROW = ['', '',
                 'Ar', '', '', '',
                 'SmallProtozoa', '', '', '',
                 'Do', '', '', '', '',
                 'Mo', '', '', '', '',
                 'Ne', '', '', '', '',
                 'Eu', '', '', '', '',
                 'Gs', '', ''
                 ]
    SECOND_ROW = ['视频名', '总帧数',
                  '平均面积', '平均缺陷', '数量', '生存率',  # Ar
                  '平均面积', '平均速度', '平均角速度', '数量',  # SmallProtozoa
                  '平均面积', '平均速度', '平均角速度', '数量', '生存率',  # Do
                  '平均面积', '平均速度', '平均角速度', '数量', '生存率',  # Mo
                  '平均面积', '平均速度', '平均角速度', '数量', '生存率',  # Ne
                  '平均面积', '平均速度', '平均角速度', '数量', '生存率',  # Eu
                  '平均面积', '平均聚簇数量', "数量"  # Gs
                  ]
    PROTOZOA_LIST = ['Ar', 'SmallProtozoa', 'Do', 'Mo', 'Ne', 'Eu', 'Gs']

    def __init__(self, input_dir):

        self.input_dir = input_dir
        self.save_path = os.path.join(input_dir, 'result.csv')

    @staticmethod
    def survival_rate(alive_dict):
        """
        计算数量信息
        :param alive_dict: 数量字典
        :return: (存活率, 大虫子总数)
        """
        die_number = alive_dict['die']
        live_number = alive_dict['live']
        total_number = die_number + live_number
        survival_rate = live_number / total_number if total_number > 0 else 0
        return round(survival_rate, 2), total_number

    @staticmethod
    def parse_small_protozoa(small_protozoa_message_list):
        """
        解析小虫子信息
        :param small_protozoa_message_list: 小虫子信息列表
        :return:
        """
        total_number = len(small_protozoa_message_list)
        area_list, v1_list, w1_list = [], [], []
        for small_protozoa_message in small_protozoa_message_list:
            first_frame, area, v1, w1 = small_protozoa_message
            area_list.append(area)
            v1_list.append(v1)
            w1_list.append(w1)
        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_v1 = sum(v1_list) / len(v1_list) if len(v1_list) > 0 else 0
        average_w1 = sum(w1_list) / len(w1_list) if len(w1_list) > 0 else 0

        return round(average_area, 2), round(average_v1, 2), round(average_w1, 2), total_number

    def parse_ar(self, ar_number_dict, ar_message_list):
        """
        解析Ar数据
        :param ar_number_dict: Ar数量信息
        :param ar_message_list: Ar指标信息
        :return:
        """
        survival_rate, total_number = self.survival_rate(ar_number_dict)
        area_list, flaw_list = [], []
        for ar_message in ar_message_list:
            first_frame, area, flaw, alive, color_path = ar_message
            area_list.append(area)
            pattern = re.compile(r'[.\d]+', re.S)
            result = pattern.findall(flaw)
            if len(result) > 0:
                flaw_list.append(float(result[0]))
        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_flaw = sum(flaw_list) / len(flaw_list) if len(flaw_list) > 0 else 0
        average_flaw = f'{average_flaw:.2f}%'
        return round(average_area, 2), average_flaw, total_number, survival_rate

    @staticmethod
    def parse_gs(gs_message_list):
        """
        解析Gs信息
        :param gs_message_list: Gs指标信息
        :return:
        """
        total_number = len(gs_message_list)
        area_list, number_list = [], []
        for gs_message in gs_message_list:
            first_frame, area, number = gs_message
            area_list.append(area)
            number_list.append(number)

        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_number = sum(number_list) / len(number_list) if len(number_list) > 0 else 0
        return round(average_area, 2), round(average_number, 2), total_number

    def parse_do(self, do_number_dict, do_message_list):
        """
        解析Do数据
        :param do_number_dict: Do数量信息
        :param do_message_list: Do指标信息
        :return:
        """
        survival_rate, total_number = self.survival_rate(do_number_dict)
        area_list, v1_list, w1_list = [], [], []
        for do_message in do_message_list:
            first_frame, area, v1, w1, v2, alive = do_message
            area_list.append(area)
            v1_list.append(v1)
            w1_list.append(w1)

        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_v1 = sum(v1_list) / len(v1_list) if len(v1_list) > 0 else 0
        average_w1 = sum(w1_list) / len(w1_list) if len(w1_list) > 0 else 0

        return round(average_area, 2), round(average_v1, 2), round(average_w1, 2), total_number, survival_rate

    def parse_mo(self, mo_number_dict, mo_message_list):
        """
        解析Mo数据
        :param ar_number_dict: Mo数量信息
        :param ar_message_list: Mo指标信息
        :return:
        """
        survival_rate, total_number = self.survival_rate(mo_number_dict)
        area_list, v1_list, w1_list = [], [], []
        for mo_message in mo_message_list:
            first_frame, area, v1, w1, v2, alive = mo_message
            area_list.append(area)
            v1_list.append(v1)
            w1_list.append(w1)

        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_v1 = sum(v1_list) / len(v1_list) if len(v1_list) > 0 else 0
        average_w1 = sum(w1_list) / len(w1_list) if len(w1_list) > 0 else 0

        return round(average_area, 2), round(average_v1, 2), round(average_w1, 2), total_number, survival_rate

    def parse_ne(self, ne_number_dict, ne_message_list):
        """
        解析Ne数据
        :param ar_number_dict: Ne数量信息
        :param ar_message_list: Ne指标信息
        :return:
        """
        survival_rate, total_number = self.survival_rate(ne_number_dict)
        area_list, v1_list, w1_list = [], [], []
        for ne_message in ne_message_list:
            first_frame, area, v1, w1, alive = ne_message
            area_list.append(area)
            v1_list.append(v1)
            w1_list.append(w1)

        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_v1 = sum(v1_list) / len(v1_list) if len(v1_list) > 0 else 0
        average_w1 = sum(w1_list) / len(w1_list) if len(w1_list) > 0 else 0

        return round(average_area, 2), round(average_v1, 2), round(average_w1, 2), total_number, survival_rate

    def parse_eu(self, eu_number_dict, eu_message_list):
        """
        解析Eu数据
        :param eu_number_dict: Eu数量信息
        :param eu_message_list: Eu指标信息
        :return:
        """
        survival_rate, total_number = self.survival_rate(eu_number_dict)
        area_list, v1_list, w1_list = [], [], []
        for eu_message in eu_message_list:
            first_frame, area, v1, w1, alive = eu_message
            area_list.append(area)
            v1_list.append(v1)
            w1_list.append(w1)

        average_area = sum(area_list) / len(area_list) if len(area_list) > 0 else 0
        average_v1 = sum(v1_list) / len(v1_list) if len(v1_list) > 0 else 0
        average_w1 = sum(w1_list) / len(w1_list) if len(w1_list) > 0 else 0

        return round(average_area, 2), round(average_v1, 2), round(average_w1, 2), total_number, survival_rate

    @staticmethod
    def parse_json_data(json_data):
        """
        解析JSON数据
        :param json_data: 一个视频的JSON数据
        :return:
        """
        video_message = json_data['video_message']
        number_sheet_message = json_data['number_sheet_message']
        movement_sheet_message = json_data['movement_sheet_message']
        return video_message, number_sheet_message, movement_sheet_message

    def general_data(self, json_data):
        """
        生成一个视频的汇总数据
        :param json_data: 一个视频的所有数据
        :return:
        """
        video_message, number_message, movement_message = self.parse_json_data(json_data)
        # 解析函数列表（解析函数的顺序要与表头中微生物的顺序一致）
        function_list = [self.parse_ar, self.parse_small_protozoa,
                         self.parse_do, self.parse_mo, self.parse_ne, self.parse_eu,
                         self.parse_gs]
        video_name, video_fps, total_frames = video_message.values()
        data = [video_name, total_frames]
        for parse_function, bug_type in zip(function_list, self.PROTOZOA_LIST):
            number_dict = number_message[bug_type] if bug_type in number_message else None
            message_list = movement_message[bug_type] if bug_type in movement_message else None
            if bug_type == 'Gs' or bug_type == 'SmallProtozoa':
                result = parse_function(message_list)
            else:
                result = parse_function(number_dict, message_list)
            data += result
        return data

    def write(self):
        """
        汇总
        :return:
        """
        rows = [self.FIRST_ROW, self.SECOND_ROW]
        for dir_name in os.listdir(self.input_dir):
            try:
                json_name = dir_name.replace('.mp4', '_result.json')
                json_path = os.path.join(self.input_dir, dir_name, 'json', json_name)
                json_reader = JSONWriter(json_path)
                json_data = json_reader.read()
                row_data = self.general_data(json_data)
                rows.append(row_data)
            except FileNotFoundError:
                continue

        with open(self.save_path, 'w', newline="", encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)


if __name__ == '__main__':
    # 需要更改成视频结果的保存路径
    input_path = r'G:\PycharmProjects\MicrobialDetection\MICDetection\output\2023-7-15_'
    writer = CollectCSV(input_path)
    writer.write()
