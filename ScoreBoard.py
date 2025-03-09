import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.core.window import Window

LabelBase.register(name="Jersey10", fn_regular="./font/Jersey10-Regular.ttf")

class ScoreBoard(BoxLayout):
    def __init__(self, normal_mode_file, line40_mode_file, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.normal_mode_file = normal_mode_file
        self.line40_mode_file = line40_mode_file
        self.normal_mode_scores = self.load_scores(normal_mode_file)
        self.line40_mode_scores = self.load_scores(line40_mode_file)
        self.display_scores()

    def load_scores(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def display_scores(self):
        # สร้าง BoxLayout สำหรับทั้งสองตาราง
        normal_mode_box = BoxLayout(orientation='vertical', size_hint=(6,6))  # ใช้ 100% ของความกว้าง
        line40_mode_box = BoxLayout(orientation='vertical', size_hint=(6,6))  # ใช้ 100% ของความกว้าง

        # โหมด Normal Mode
        normal_mode_label = Label(text="Normal Mode Scores:", font_name="Jersey10", font_size=24, size_hint_y=None, height=40, color=(1, 1, 1, 1))
        normal_mode_box.add_widget(normal_mode_label)
        
        normal_mode_grid = GridLayout(cols=2, size_hint_y=None)
        normal_mode_grid.bind(minimum_height=normal_mode_grid.setter('height'))
        for idx, score in enumerate(self.normal_mode_scores):
            normal_mode_grid.add_widget(Label(text=f"Player {idx+1}:", font_name="Jersey10", font_size=20))
            normal_mode_grid.add_widget(Label(text=str(score), font_name="Jersey10", font_size=20))
        
        normal_mode_scroll = ScrollView(size_hint=(1, None), size=(self.width, 200))  # เพิ่มขนาดให้เต็มหน้าจอในแนวตั้ง
        normal_mode_scroll.add_widget(normal_mode_grid)
        normal_mode_box.add_widget(normal_mode_scroll)

        # โหมด 40 Line Mode
        line40_mode_label = Label(text="40 Line Mode Scores:", font_name="Jersey10", font_size=24, size_hint_y=None, height=40, color=(1, 1, 1, 1))
        line40_mode_box.add_widget(line40_mode_label)

        line40_mode_grid = GridLayout(cols=2, size_hint_y=None)
        line40_mode_grid.bind(minimum_height=line40_mode_grid.setter('height'))
        for idx, score in enumerate(self.line40_mode_scores):
            line40_mode_grid.add_widget(Label(text=f"Player {idx+1}:", font_name="Jersey10", font_size=20))
            line40_mode_grid.add_widget(Label(text=str(score), font_name="Jersey10", font_size=20))
        
        line40_mode_scroll = ScrollView(size_hint=(1, None), size=(self.width, 200))  # เพิ่มขนาดให้เต็มหน้าจอในแนวตั้ง
        line40_mode_scroll.add_widget(line40_mode_grid)
        line40_mode_box.add_widget(line40_mode_scroll)

        # เพิ่มทั้งสองตารางลงใน BoxLayout หลัก
        self.add_widget(normal_mode_box)
        self.add_widget(line40_mode_box)

class ScoreBoardApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        Window.fullscreen = "auto"
        normal_mode_file = 'normal_mode_scores.json'
        line40_mode_file = 'line40_mode_scores.json'
        return ScoreBoard(normal_mode_file, line40_mode_file)

if __name__ == "__main__":
    ScoreBoardApp().run()
