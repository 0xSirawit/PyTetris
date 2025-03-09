from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.core.window import Window
from screen.modeClassic import TetrisApp
from screen.mode40Line import Tetris40LineApp
from screen.HowToPlay import HowToPlayScreen

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
        layout = BoxLayout(orientation="vertical", padding=[10, 32], spacing=32)

        title = Label(
            text="Tetris Game",
            font_size=BASE_FONT_SIZE * 2,
            font_name="Jersey10",
            size_hint=(1, 0.1),
        )

        btn_start = self.create_button("CLASSIC", (0.1, 0.7, 0.3, 1), self.start_game)
        btn_40line = self.create_button("40 LINES", (0.1, 1, 0.3, 1), self.start_40line)
        btn_high_scores = self.create_button(
            "HOW TO PLAY", (0.2, 0.6, 1, 1), self.how_to_play
        )
        btn_exit = self.create_button(
            "EXIT", (1, 0.3, 0.3, 1), lambda _: App.get_running_app().stop()
        )

        layout.add_widget(title)
        layout.add_widget(btn_start)
        layout.add_widget(btn_40line)
        layout.add_widget(btn_high_scores)
        layout.add_widget(btn_exit)
        self.add_widget(layout)

    def create_button(self, text, background_color, callback):
        button = Button(
            text=text,
            font_size=BASE_FONT_SIZE * 1.1,
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

    def start_40line(self, instance):
        self.manager.current = "game_40line_screen"

    def how_to_play(self, instance):
        self.manager.current = "how_to_play_screen"


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


class Game40LineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tetris_app = None  # Delay initialization

    def on_enter(self, *args):
        if self.tetris_app is None:
            self.tetris_app = Tetris40LineApp()
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
        sm.add_widget(Game40LineScreen(name="game_40line_screen"))
        sm.add_widget(HowToPlayScreen(name="how_to_play_screen"))
        return sm


if __name__ == "__main__":
    TetrisMenuApp().run()
