import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class ScoreBoard(BoxLayout):
    def __init__(self, normal_mode_file, line40_mode_file, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
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
        normal_mode_label = Label(text="Normal Mode Scores:", size_hint_y=None, height=40)
        self.add_widget(normal_mode_label)
        normal_mode_scroll = ScrollView(size_hint=(1, None), size=(self.width, 200))
        normal_mode_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        normal_mode_layout.bind(minimum_height=normal_mode_layout.setter('height'))
        for score in self.normal_mode_scores:
            normal_mode_layout.add_widget(Label(text=str(score), size_hint_y=None, height=40))
        normal_mode_scroll.add_widget(normal_mode_layout)
        self.add_widget(normal_mode_scroll)

        line40_mode_label = Label(text="40 Line Mode Scores:", size_hint_y=None, height=40)
        self.add_widget(line40_mode_label)
        line40_mode_scroll = ScrollView(size_hint=(1, None), size=(self.width, 200))
        line40_mode_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        line40_mode_layout.bind(minimum_height=line40_mode_layout.setter('height'))
        for score in self.line40_mode_scores:
            line40_mode_layout.add_widget(Label(text=str(score), size_hint_y=None, height=40))
        line40_mode_scroll.add_widget(line40_mode_layout)
        self.add_widget(line40_mode_scroll)

class ScoreBoardApp(App):
    def build(self):
        normal_mode_file = 'normal_mode_scores.json'
        line40_mode_file = 'line40_mode_scores.json'
        return ScoreBoard(normal_mode_file, line40_mode_file)

if __name__ == "__main__":
    ScoreBoardApp().run()