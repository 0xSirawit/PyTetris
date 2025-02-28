from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from main import *

SCREEN_RESOLUTION = (1920, 1080)
GRID_COLS, GRID_ROWS = 10, 20


# Game_menu
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        title = Label(text="Tetris Game", font_size=32, size_hint=(1, 0.1))

        btn_start = Button(
            text="Start Game",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        btn_high_scores = Button(
            text="High Scores",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(0.1, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        btn_exit = Button(
            text="Exit",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(1, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )

        btn_start.bind(on_press=self.start_game)
        btn_high_scores.bind(on_press=self.show_high_scores)
        btn_exit.bind(on_press=lambda: App.get_running_app().stop())

        layout.add_widget(title)
        layout.add_widget(btn_start)
        layout.add_widget(btn_high_scores)
        layout.add_widget(btn_exit)
        self.add_widget(layout)

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


# Game_screen
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        init_pos = (
            (((SCREEN_RESOLUTION[0] - (GRID_COLS * CELL_SIZE)) / 2) - 120),
            (((SCREEN_RESOLUTION[1] - (GRID_ROWS * CELL_SIZE)) / 2)),
        )

        self.tetris_board = TetrisBoard(init_pos)
        self.next_tetromino_widget = NextTetrominoWidget()

        self.info_panel = BoxLayout(
            orientation="vertical",
            spacing=120,
            size_hint=(None, None),
            size=(400, 300),
            pos=(
                self.tetris_board.width + init_pos[0] + 120,
                init_pos[1] + 100,
            ),
        )

        self.lines_container, self.lines_value = self.create_label_pair("LINES", "0")
        self.level_container, self.level_value = self.create_label_pair("LEVEL", "1")
        self.score_container, self.score_value = self.create_label_pair("SCORE", "0")

        next_tetromino_label_container = BoxLayout(
            orientation="vertical", size_hint=(None, None), spacing=64
        )
        next_tetromino_label = Label(
            text="NEXT",
            font_size=72,
            font_name="Jersey10",
        )
        next_tetromino_label_container.add_widget(next_tetromino_label)
        self.info_panel.add_widget(next_tetromino_label_container)
        self.info_panel.add_widget(self.next_tetromino_widget)
        self.info_panel.add_widget(self.lines_container)
        self.info_panel.add_widget(self.level_container)
        self.info_panel.add_widget(self.score_container)

        self.tetris_board.bind(lines_cleared=self.update_lines)
        self.tetris_board.bind(level=self.update_levels)
        self.tetris_board.bind(score=self.update_scores)
        self.tetris_board.bind(next_tetromino=self.update_next_tetromino)

        self.add_widget(self.tetris_board)
        self.add_widget(self.info_panel)

        Clock.schedule_once(
            lambda dt: self.next_tetromino_widget.update_tetromino(
                self.tetris_board.game.bag.next_piece
            )
        )

    def create_label_pair(self, text: str, value: str) -> tuple:
        container = BoxLayout(
            orientation="vertical", size_hint=(None, None), spacing=64
        )
        label = Label(text=text, font_size=72, font_name="Jersey10")
        value_label = Label(text=value, font_size=64, font_name="Jersey10")
        container.add_widget(label)
        container.add_widget(value_label)
        return container, value_label

    def update_lines(self, instance, value):
        self.lines_value.text = str(value)

    def update_levels(self, instance, value):
        self.level_value.text = str(value)

    def update_scores(self, instance, value):
        self.score_value.text = str(value)

    def update_next_tetromino(self, instance, value):
        self.next_tetromino_widget.update_tetromino(value)


# Main_app
class GameApp(App):
    def build(self):
        sm = ScreenManager()
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        Window.fullscreen = "auto"
        sm.add_widget(MenuScreen(name="menu_screen"))
        sm.add_widget(GameScreen(name="game_screen"))
        return sm


if __name__ == "__main__":
    app = GameApp()
    app.run()
