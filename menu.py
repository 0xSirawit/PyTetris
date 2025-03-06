from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.core.window import Window
from main import TetrisApp

SCREEN_RESOLUTION = (2880, 1800)
GRID_COLS, GRID_ROWS = 10, 20
WINDOW_BG_COLOR = (0.1, 0.1, 0.1, 1)
BASE_FONT_SIZE = SCREEN_RESOLUTION[1] * 0.04
LabelBase.register(name="Jersey10", fn_regular="./font/Jersey10-Regular.ttf")


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        title = Label(
            text="Tetris Game",
            font_size=BASE_FONT_SIZE * 1.5,
            font_name="Jersey10",
            size_hint=(1, 0.1),
        )

        btn_start = self.create_button("Start Game", (0.2, 0.6, 1, 1), self.start_game)
        btn_high_scores = self.create_button(
            "High Scores", (0.1, 0.7, 0.3, 1), self.show_high_scores
        )
        btn_exit = self.create_button(
            "Exit", (1, 0.3, 0.3, 1), lambda _: App.get_running_app().stop()
        )

        layout.add_widget(title)
        layout.add_widget(btn_start)
        layout.add_widget(btn_high_scores)
        layout.add_widget(btn_exit)
        self.add_widget(layout)

    def create_button(self, text, background_color, callback):
        button = Button(
            text=text,
            font_size=BASE_FONT_SIZE,
            font_name="Jersey10",
            size_hint=(0.3, 0.1),
            background_color=background_color,
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        button.bind(on_press=callback)
        return button

    def start_game(self, instance):
        self.manager.current = "game_screen"

    def show_high_scores(self, instance):
        content = BoxLayout(orientation="vertical")
        content.add_widget(
            Label(
                text="High Scores:\n1. Player1 - 10000\n2. Player2 - 8000\n3. Player3 - 6000",
                font_size=24,
            )
        )
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        content.add_widget(close_btn)

        popup = Popup(title="High Scores", content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tetris_app = None  # Delay initialization

    def on_enter(self, *args):
        if self.tetris_app is None:
            self.tetris_app = TetrisApp()
            self.add_widget(self.tetris_app.build())

    def on_leave(self, *args):
        if self.tetris_app:
            self.remove_widget(self.tetris_app.root)
            self.tetris_app.stop()
            self.tetris_app = None


class TetrisMenuApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        Window.fullscreen = "auto"

        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu_screen"))
        sm.add_widget(GameScreen(name="game_screen"))
        return sm


if __name__ == "__main__":
    TetrisMenuApp().run()
