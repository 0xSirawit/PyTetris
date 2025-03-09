import csv
import os
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import ListProperty

class FadingTableRow(BoxLayout):
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, cells, is_header=False, **kwargs):
        super(FadingTableRow, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        
        # สร้าง Label สำหรับแต่ละเซลล์
        for cell in cells:
            lbl = Label(
                text=str(cell),
                size_hint_x=1,
                halign='center',
                valign='middle',
                color=[0, 0, 0, 1] if not is_header else [1, 1, 1, 1]
            )
            lbl.bind(size=lbl.setter('text_size'))
            self.add_widget(lbl)
        
        # ตั้งค่าสีพื้นหลังตามประเภทแถว
        if is_header:
            self.background_color = [0.2, 0.2, 0.6, 1]  # สีน้ำเงินเข้มสำหรับส่วนหัว
        else:
            self.background_color = [0.9, 0.9, 0.9, 1]  # สีเทาอ่อนสำหรับข้อมูล

    def on_background_color(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*value)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def fade_in(self, duration=1):
        anim = Animation(background_color=[0.9, 0.9, 0.9, 1], duration=duration)
        anim.start(self)

    def fade_out(self, duration=1):
        anim = Animation(background_color=[0.9, 0.9, 0.9, 0], duration=duration)
        anim.start(self)


class CSVTable(GridLayout):
    def __init__(self, csv_file, **kwargs):
        super(CSVTable, self).__init__(**kwargs)
        self.csv_file = csv_file
        self.cols = 1
        self.spacing = 1
        self.padding = 10
        self.size_hint_y = None
        
        self.data_rows = []
        self.current_displayed = 0
        self.rows_per_page = 10
        
        # อ่านข้อมูล CSV
        self.headers, self.rows = self.read_csv()
        self.bind(size=self.update_table)

    def read_csv(self):
        if not os.path.exists(self.csv_file):
            return ["No Data"], []
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader, ["No Data"])
            rows = list(reader)
        return headers, rows

    def update_table(self, *args):
        self.clear_widgets()
        
        # สร้างแถวส่วนหัว
        header_row = FadingTableRow(self.headers, is_header=True)
        self.add_widget(header_row)
        
        # คำนวณแถวที่จะแสดง
        start_idx = self.current_displayed
        end_idx = min(start_idx + self.rows_per_page, len(self.rows))
        
        # ถ้าไม่มีข้อมูลเพียงพอให้กลับไปเริ่มต้น
        if start_idx >= len(self.rows):
            self.current_displayed = 0
            start_idx = 0
            end_idx = min(self.rows_per_page, len(self.rows))
            
        # เคลียร์แถวเก่าที่เก็บไว้
        self.data_rows = []
        
        # สร้างแถวข้อมูล
        for row in self.rows[start_idx:end_idx]:
            data_row = FadingTableRow(row)
            self.data_rows.append(data_row)
            self.add_widget(data_row)
        
        # อัพเดต index
        self.current_displayed = end_idx

    def fade_out_current_rows(self, dt=None):
        for row in self.data_rows:
            row.fade_out()
        Clock.schedule_once(self.update_and_fade_in, 1)

    def update_and_fade_in(self, dt):
        self.update_table()
        for row in self.data_rows:
            row.fade_in()


class CSVTableApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        csv_file = "data.csv"
        
        main_layout = BoxLayout(orientation='vertical')
        self.table = CSVTable(csv_file)
        main_layout.add_widget(self.table)
        
        
        Clock.schedule_interval(self.table.fade_out_current_rows, 5)
        
        return main_layout


if __name__ == "__main__":
    CSVTableApp().run()