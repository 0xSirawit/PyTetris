import json
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

SCOREBOARD_FILE = "scoreboard.json"

class ScoreBoard:
    def __init__(self):
        self.scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(SCOREBOARD_FILE):
            with open(SCOREBOARD_FILE, "r") as file:
                return json.load(file)
        return []

    def save_scores(self):
        with open(SCOREBOARD_FILE, "w") as file:
            json.dump(self.scores, file)

    def add_score(self, player_name, score, lines_cleared, level):
        self.scores.append({
            "player_name": player_name,
            "score": score,
            "lines_cleared": lines_cleared,
            "level": level
        })
        self.scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        self.save_scores()

    def get_top_scores(self, top_n=10):
        return self.scores[:top_n]

class ScoreBoardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scoreboard = ScoreBoard()
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        title = Label(text="High Scores", font_size=32, size_hint=(1, 0.1))
        layout.add_widget(title)

        top_scores = self.scoreboard.get_top_scores()
        for rank, score in enumerate(top_scores, start=1):
            score_label = Label(
                text=f"{rank}. {score['player_name']} - {score['score']} points",
                font_size=24,
                size_hint=(1, 0.1)
            )
            layout.add_widget(score_label)

        btn_close = Button(text="Close", font_size=24, size_hint=(1, 0.1))
        btn_close.bind(on_press=self.close)
        layout.add_widget(btn_close)

        self.add_widget(layout)

    def close(self, instance):
        self.manager.current = "menu_screen"