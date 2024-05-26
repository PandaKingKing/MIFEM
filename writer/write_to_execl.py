import xlwings as xw
import json


class JSONWriter:

    def __init__(self, json_path):
        """

        :param json_path: json路径
        """
        self.json_path = json_path

    def generate_json(self, bug_record):
        """
        生成需要储存的JSON
        :param bug_record: 微生物记录器
        :return: None
        """

        json_data = {
            "video_message": self.video_message_to_json(bug_record),
            "number_sheet_message": self.number_sheet_to_json(bug_record),
            "movement_sheet_message": self.movement_sheet_to_json(bug_record)
        }

        return json_data

    def write(self, bug_record):
        """
        将输入写入成JSON
        :param bug_record: 微生物记录器
        :return: None
        """

        json_data = self.generate_json(bug_record)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json_data = json.dumps(json_data)
            f.write(json_data)

    def read(self):
        """
        将JSON数据读出
        :return: 读出的JSON数据字典
        """
        with open(self.json_path, "r", encoding="utf-8") as f:
            json_data = f.read()
            json_data = json.loads(json_data)
        return json_data

    @staticmethod
    def number_sheet_to_json(bug_record):
        """
        微生物死活数量转换成JSON信息
        :param bug_record: 微生物记录器
        :return:
        """
        number_json = {}
        for bug_name, alive in bug_record.bug_dead_or_live.items():
            number_json[str(bug_name)] = dict(alive)
        number_json['Gs'] = sum(bug_record.gs_area_list) if bug_record.gs_area_list else 0
        return number_json

    @staticmethod
    def movement_sheet_to_json(bug_record):
        """
        微生物各项指标转换成JSON信息
        :param bug_record: 微生物记录器
        :return:
        """
        movement_json = {}
        bug_record.bug_record['SmallProtozoa'] = bug_record.bug_record['SmallProtozoa'][:20000]
        for bug_name, bug_list in bug_record.bug_record.items():
            movement_json[str(bug_name)] = list(bug_list)
        for index, ar_path in enumerate(bug_record.ar_colors_list):
            movement_json['Ar'][index].append(ar_path)
        return movement_json

    @staticmethod
    def video_message_to_json(bug_record):
        """
        视频信息转换成JSON信息
        :param bug_record: 微生物记录器
        :return:
        """

        video_message_json = {
            "video_name": bug_record.video_path,
            "video_fps": bug_record.fps,
            "total_frames": bug_record.frames
        }
        return video_message_json


class ExcelWriter:

    def __init__(self, execl_path: str):
        """
        A1 格的坐标为（1， 1）
        :param execl_path:
        """
        self.names = ['Ar', 'Do', 'Mo', 'Ne', 'Eu', 'Gs', 'SmallProtozoa']
        self.execl_path = execl_path

        self.app = xw.App(visible=False, add_book=False)
        self.app.display_alerts = False
        self.app.screen_updating = False
        self.work_book = self.app.books.add()
        self.sheet2 = self.work_book.sheets['sheet1']
        self.sheet2.name = '运动'
        self.sheet1 = self.work_book.sheets.add('死活')
        self.init_execl()

    def init_sheet1(self):
        """
        初始化"数量"sheet
        :return: None
        """
        cell_a1_a2 = self.sheet1.range('A1:A2')
        cell_a1_a2.merge()
        cell_a1_a2.value = "数量"
        cell_a1_a2.api.HorizontalAlignment = -4108

        names = self.names[:-1]
        cells = [self.sheet1.range('B1:C1'), self.sheet1.range('D1:E1'), self.sheet1.range('F1:G1'),
                 self.sheet1.range('H1:I1'), self.sheet1.range('J1:K1'), self.sheet1.range('L1:M1')]

        for name, cell in zip(names, cells):
            cell.merge()
            cell.value = name
            cell.api.HorizontalAlignment = -4108

        self.sheet1.range('B2:K2').value = ['活', '死'] * 5
        self.sheet1.range('L2:M2').merge()
        self.sheet1.range('L3').value = '面积'

    def init_sheet2(self):
        """
        初始化"运动"sheet
        :return: None
        """
        # 第一行
        cell_a1_b1 = self.sheet2.range('A1:B1')
        cell_a1_b1.merge()
        cell_a1_b1.value = '视频名称'
        self.video_name = self.sheet2.range("C1:D1")
        self.video_name.merge()
        cell_e1_f1 = self.sheet2.range('E1:F1')
        cell_e1_f1.merge()
        cell_e1_f1.value = '视频帧率'
        self.video_fps = self.sheet2.range("G1:H1")
        self.video_fps.merge()
        cell_i1_j1 = self.sheet2.range('I1:J1')
        cell_i1_j1.merge()
        cell_i1_j1.value = '视频总帧数'
        self.video_total_frames = self.sheet2.range('K1:L1')
        self.video_total_frames.merge()

        # 第二行
        cell_a2_a3 = self.sheet2.range('A2:A3')
        cell_a2_a3.merge()
        cell_a2_a3.value = "number"
        cell_a2_a3.api.HorizontalAlignment = -4108

        names = self.names[:]
        cells = [self.sheet2.range('B2:F2'), self.sheet2.range('G2:L2'), self.sheet2.range('M2:R2'),
                 self.sheet2.range('S2:W2'), self.sheet2.range('X2:AB2'), self.sheet2.range('AC2:AE2'),
                 self.sheet2.range('AF2:AI2')]

        for name, cell in zip(names, cells):
            cell.merge()
            cell.value = name
            cell.api.HorizontalAlignment = -4108

        cell = self.sheet2.range('B3')
        cell.value = ['frame', 'area_average', 'flaw', 'die/live', 'color',
                      'frame', 'area_average', 'v1', 'w1', 'v2', 'die/live',
                      'frame', 'area_average', 'v1', 'w1', 'v2', 'die/live',
                      'frame', 'area_average', 'v1', 'w1', 'die/live',
                      'frame', 'area_average', 'v1', 'w1', 'die/live',
                      'frame', 'area_average', 'number',
                      'frame', 'area_average', 'v1', 'w1']
        cell.expand('right').api.HorizontalAlignment = -4108

    def init_execl(self):
        """
        初始化excel表
        :return: None
        """
        self.init_sheet1()
        self.init_sheet2()

    def set_video_message(self, video_name, video_fps, video_total_frames):
        """
        设置视频信息
        :param video_name: 视频名称
        :param video_fps: 视频帧率
        :param video_total_frames: 视频总帧数
        :return:
        """
        self.video_name.value = video_name
        self.video_fps.value = video_fps
        self.video_total_frames.value = video_total_frames

    def set_total_alive(self, bug_name, bug_num, state):
        """
        设置大虫子死活数量
        :param bug_name: 微生物类别
        :param bug_num: 微生物数量
        :param state: 微生物状态live or die
        :return:
        """

        col = (self.names.index(bug_name) + 1) * 2
        if state == 'die':
            col += 1
        self.sheet1.range(3, col).value = str(bug_num)

    def set_total_gs_area(self, area):
        """
        设置Gs面积
        :param area: Gs面积
        :return:
        """
        self.sheet1.range(3, 13).value = str(area)

    def set_number(self, total_number):
        """
        设置行号
        :param total_number: 行的数量
        :return:
        """

        try:
            self.sheet2.range('A4').options(transpose=True).value = list(range(1, total_number + 1))
            self.sheet2.range('A4').expand('down').api.HorizontalAlignment = -4108
        except Exception as e:
            print(e, 'e')
            print(total_number, type(total_number))
            print(list(range(1, total_number + 1)), type(list(range(1, total_number + 1))))

    def set_bug_message(self, bug_name, bug_list):
        """
        设置微生物信息
        :param bug_name: 微生物类别
        :param bug_list: 对应的微生物数据
        :return:
        """

        index = self.names.index(bug_name)
        cells = [self.sheet2.range('B4'), self.sheet2.range('G4'), self.sheet2.range('M4'),
                 self.sheet2.range('S4'), self.sheet2.range('X4'), self.sheet2.range('AC4'),
                 self.sheet2.range('AF4')]
        cell = cells[index]
        cell.value = bug_list

    def set_ar_colors(self, ar_color_list):
        """
        设置Ar颜色
        :param ar_color_list: Ar颜色图片路径列表
        :return:
        """
        color_index = 4
        for color_path in ar_color_list:
            try:
                cell = self.sheet2[f'F{color_index}']
                self.sheet2.pictures.add(color_path, left=cell.left, top=cell.top, width=cell.width, height=cell.height)
                color_index += 1
            except:
                pass

    def write(self, bug_record):
        """
        将数据写入excel
        :param bug_record: 微生物记录器
        :return:
        """

        # sheet1
        # 写入活与死的数量信息
        for bug_name, alive in bug_record.bug_dead_or_live.items():
            for state, number in alive.items():
                self.set_total_alive(bug_name, number, state)

        # 写入gs面积
        total_gs_area = 0
        if bug_record.gs_area_list:
            total_gs_area = sum(bug_record.gs_area_list)
        self.set_total_gs_area(total_gs_area)

        # sheet2
        # 写入视频信息
        self.set_video_message(bug_record.video_path, bug_record.fps, bug_record.frames)

        # 限制小虫子的数量
        bug_record.bug_record['SmallProtozoa'] = bug_record.bug_record['SmallProtozoa'][:20000]

        # 写入number
        total_number = len(max(bug_record.bug_record.values(), key=len))
        self.set_number(total_number)

        # 更改Ar颜色
        self.set_ar_colors(bug_record.ar_colors_list)

        # 写入虫子信息
        for bug_name, bug_list in bug_record.bug_record.items():
            self.set_bug_message(str(bug_name), list(bug_list))

        self.exit()

    def json_write(self, json_writer):
        """
        将JSON数据写入excel
        :param json_writer: JSON写入器对象
        :return:
        """

        json_data = json_writer.read()
        bug_dead_or_live = json_data['number_sheet_message']
        # sheet1
        # 写入活与死的数量信息
        for bug_name, alive in bug_dead_or_live.items():
            if bug_name != 'Gs':
                for state, number in alive.items():
                    self.set_total_alive(bug_name, number, state)

        # 写入gs面积
        gs_area = bug_dead_or_live['Gs']
        self.set_total_gs_area(gs_area)

        # sheet2
        # 写入视频信息
        video_message = json_data['video_message']
        self.set_video_message(video_message.video_name, video_message.video_fps, video_message.total_frames)

        bug_record = json_data['movement_sheet_message']
        # 写入number
        total_number = len(max(bug_record.values(), key=len))
        self.set_number(total_number)

        # 更改Ar颜色
        ar_colors_list = []
        for ar_message in enumerate(bug_record['Ar']):
            ar_path = ar_message.pop()
            ar_colors_list.append(ar_path)
        self.set_ar_colors(bug_record.ar_colors_list)

        # 写入虫子信息
        for bug_name, bug_list in bug_record.items():
            self.set_bug_message(str(bug_name), list(bug_list))

        self.exit()

    def exit(self):
        """
        退出并保存excel
        :return: None
        """
        self.work_book.save(self.execl_path)
        self.work_book.close()
        self.app.quit()


if __name__ == '__main__':
    writer1 = ExcelWriter('test1')
    writer1.sheet2.range('A4').options(transpose=True).value = list(range(1, 10))
    writer1.exit()
    writer2 = ExcelWriter('test2')
    writer2.set_number(10)
    writer2.exit()
