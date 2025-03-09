from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, InstructionGroup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from tetris import Tetris

LabelBase.register(name="Jersey10", fn_regular="./font/Jersey10-Regular.ttf")

SCREEN_RESOLUTION = (1920, 1080)
GRID_COLS, GRID_ROWS = 10, 20
CELL_SIZE = 50
REFRESH_RATE = 1 / 30
MOVE_INTERVAL = 0.05

TETROMINO_COLORS = {
    1: [0.7, 0.3, 0.2],
    2: [0.5, 0.7, 0.2],
    3: [0.7, 0.2, 0.2],
    4: [0.6, 0.2, 0.6],
    5: [0.4, 0.8, 0.6],
    6: [0.7, 0.6, 0.2],
    7: [0.2, 0.7, 0.5],
    9: [0, 0, 0],
}

TETROMINO_SHAPES = {
    "L": [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "S": [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "Z": [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "T": [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "J": [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "O": [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "I": [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
}

Window.clearcolor = WINDOW_BG_COLOR


class TetrisBoard(Widget):
    lines_cleared = NumericProperty(0)
    level = NumericProperty(0)
    score = NumericProperty(0)
    next_tetromino = StringProperty("")
    game_over = BooleanProperty(False)

    def __init__(self, init_pos, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        self.size_hint = (None, None)
        self.size = (GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE)
        self.pos = init_pos

        self._draw_grid_borders()
        self.grid_lines = InstructionGroup()
        self.canvas.add(self.grid_lines)
        self._draw_grid_lines(init_pos)

        self.game = Tetris(GRID_COLS, GRID_ROWS)
        self.total_clear_line = self.game.total_clear_line
        self.level = self.game.level
        self.score = self.game.score
        self.next_tetromino = self.game.bag.next_piece
        self.game_over = self.game.is_game_over
        self.blocks = [[None] * GRID_COLS for _ in range(GRID_ROWS)]

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        self.handled_keys = set()

        Clock.schedule_interval(self.update_board, REFRESH_RATE)
        Clock.schedule_interval(self.move_step, MOVE_INTERVAL)

    def _draw_grid_lines(self, init_pos: tuple = (0, 0)) -> None:
        x, y = init_pos
        self.grid_lines.clear()
        self.grid_lines.add(Color(1, 1, 1, 0.4))
        for row in range(GRID_ROWS + 1):
            self.grid_lines.add(
                Line(
                    points=[
                        x,
                        y + row * CELL_SIZE,
                        x + GRID_COLS * CELL_SIZE,
                        y + row * CELL_SIZE,
                    ],
                    width=1,
                )
            )
        for col in range(GRID_COLS + 1):
            self.grid_lines.add(
                Line(
                    points=[
                        x + col * CELL_SIZE,
                        y,
                        x + col * CELL_SIZE,
                        y + GRID_ROWS * CELL_SIZE,
                    ],
                    width=1,
                )
            )

    def _draw_grid_borders(self) -> None:
        # Left border
        self.canvas.add(
            Line(
                points=[self.x, self.y, self.x, self.y + GRID_ROWS * CELL_SIZE], width=2
            )
        )

        # Right border
        self.canvas.add(
            Line(
                points=[
                    self.x + GRID_COLS * CELL_SIZE,
                    self.y,
                    self.x + GRID_COLS * CELL_SIZE,
                    self.y + GRID_ROWS * CELL_SIZE,
                ],
                width=2,
            )
        )

        # Bottom border
        self.canvas.add(
            Line(
                points=[self.x, self.y, self.x + GRID_COLS * CELL_SIZE, self.y], width=2
            )
        )

    def update_board(self, *args) -> None:
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                board_value = self.game.board[row, col]
                if board_value != 0 and self.blocks[row][col] is None:
                    rect = Rectangle(
                        pos=(
                            self.pos[0] + col * CELL_SIZE,
                            self.pos[1] + row * CELL_SIZE,
                        ),
                        size=(CELL_SIZE, CELL_SIZE),
                    )
                    self.canvas.add(Color(*TETROMINO_COLORS[board_value], 1))
                    self.blocks[row][col] = rect
                    self.canvas.add(rect)
                elif board_value == 0 and self.blocks[row][col] is not None:
                    self.canvas.remove(self.blocks[row][col])
                    self.blocks[row][col] = None
        self.checks()

    def checks(self):
        cleared_lines = self.game.total_clear_line
        level = self.game.level
        score = self.game.score
        next_tetromino = self.game.bag.next_piece
        game_over = self.game.is_game_over

        if self.game_over != game_over:
            self.game_over = game_over
        if cleared_lines != self.lines_cleared:
            self.lines_cleared = cleared_lines
        if level != self.level:
            self.level = level
        if score != self.score:
            self.score = score
        if next_tetromino != self.next_tetromino:
            self.next_tetromino = next_tetromino

    def _on_keyboard_closed(self) -> None:
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers) -> None:
        self.pressed_keys.add(keycode[1])

    def _on_key_up(self, keyboard, keycode) -> None:
        self.pressed_keys.discard(keycode[1])
        self.handled_keys.discard(keycode[1])

    def move_step(self, dt: float) -> None:
        if "w" in self.pressed_keys:
            self.game.move_tetromino("down")
        if "a" in self.pressed_keys:
            self.game.move_tetromino("left")
        if "d" in self.pressed_keys:
            self.game.move_tetromino("right")

        if "right" in self.pressed_keys and "right" not in self.handled_keys:
            self.game.rotate_tetromino("CW")
            self.handled_keys.add("right")
        if "left" in self.pressed_keys and "left" not in self.handled_keys:
            self.game.rotate_tetromino("CCW")
            self.handled_keys.add("left")

        if "q" in self.pressed_keys:
            exit()

    def reset_game(self):
        self.game = Tetris(GRID_COLS, GRID_ROWS)
        self.total_clear_line = self.game.total_clear_line
        self.level = self.game.level
        self.score = self.game.score
        self.next_tetromino = self.game.bag.next_piece
        self.game_over = self.game.is_game_over
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.blocks[row][col] is not None:
                    self.canvas.remove(self.blocks[row][col])
                    self.blocks[row][col] = None


class GameOverScreen(ModalView):
    def __init__(self, score, lines, level, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.5, 0.6)
        self.auto_dismiss = False
        self.background_color = (0.1, 0.1, 0.1, 0.9)

        # Main layout
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Game Over title
        game_over_label = Label(
            text="GAME OVER", font_size=100, font_name="Jersey10", size_hint=(1, 0.2)
        )

        # Stats layout
        stats_layout = BoxLayout(orientation="vertical", spacing=20, size_hint=(1, 0.5))

        score_label = Label(text=f"SCORE: {score}", font_size=72, font_name="Jersey10")

        lines_label = Label(
            text=f"LINES CLEARED: {lines}", font_size=72, font_name="Jersey10"
        )

        level_label = Label(text=f"LEVEL: {level}", font_size=72, font_name="Jersey10")

        stats_layout.add_widget(score_label)
        stats_layout.add_widget(lines_label)
        stats_layout.add_widget(level_label)

        # Buttons layout
        buttons_layout = BoxLayout(
            orientation="horizontal", spacing=30, size_hint=(1, 0.3), padding=(50, 10)
        )

        restart_button = Button(
            text="RESTART",
            font_size=64,
            font_name="Jersey10",
            background_color=(0.1, 0.7, 0.3, 1),
            size_hint=(0.5, 1),
        )
        restart_button.bind(on_release=self.restart_game)

        exit_button = Button(
            text="EXIT",
            font_size=64,
            font_name="Jersey10",
            background_color=(1, 0.3, 0.3, 1),
            size_hint=(0.5, 1),
        )
        exit_button.bind(on_release=self.exit_game)

        buttons_layout.add_widget(restart_button)
        buttons_layout.add_widget(exit_button)

        # Add all elements to the main layout
        layout.add_widget(game_over_label)
        layout.add_widget(stats_layout)
        layout.add_widget(buttons_layout)

        self.add_widget(layout)

    def restart_game(self, instance):
        App.get_running_app().tetris_board.reset_game()
        self.dismiss()

    def exit_game(self, instance):
        exit()


class NextTetrominoWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (4 * CELL_SIZE // 1.2, 4 * CELL_SIZE // 1.2)
        self.canvas.clear()
        self.blocks = []

    def update_tetromino(self, tetromino: str) -> None:
        piece_shape = TETROMINO_SHAPES[tetromino]
        self.canvas.clear()
        self.blocks.clear()

        match tetromino:
            case "L":
                color = TETROMINO_COLORS[1]
            case "S":
                color = TETROMINO_COLORS[2]
            case "Z":
                color = TETROMINO_COLORS[3]
            case "T":
                color = TETROMINO_COLORS[4]
            case "J":
                color = TETROMINO_COLORS[5]
            case "O":
                color = TETROMINO_COLORS[6]
            case "I":
                color = TETROMINO_COLORS[7]

        with self.canvas:
            Color(*color, 1)
            for row in range(4):
                for col in range(4):
                    if piece_shape[row][col]:
                        rect = Rectangle(
                            pos=(
                                (self.x - CELL_SIZE // 2) + col * (CELL_SIZE // 1.2),
                                (self.y + CELL_SIZE // 2)
                                + (3 - row) * (CELL_SIZE // 1.2),
                            ),
                            size=(CELL_SIZE // 1.2, CELL_SIZE // 1.2),
                        )
                        self.blocks.append(rect)
                        self.canvas.add(rect)


class TetrisApp(App):
    def create_label_pair(self, text: str, value: str) -> tuple[BoxLayout, Label]:
        container = BoxLayout(
            orientation="vertical", size_hint=(None, None), spacing=64
        )
        label = Label(
            text=text,
            font_size=72,
            font_name="Jersey10",
        )
        value_label = Label(
            text=value,
            font_size=64,
            font_name="Jersey10",
        )
        container.add_widget(label)
        container.add_widget(value_label)
        return container, value_label

    def build(self) -> TetrisBoard:
        Window.fullscreen = "auto"
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
        self.tetris_board.bind(game_over=self.show_game_over)

        root = FloatLayout()
        root.add_widget(self.tetris_board)
        root.add_widget(self.info_panel)

        Clock.schedule_once(
            lambda dt: self.next_tetromino_widget.update_tetromino(
                self.tetris_board.game.bag.next_piece
            )
        )
        return root

    def update_lines(self, instance, value):
        self.lines_value.text = str(value)

    def update_levels(self, instance, value):
        self.level_value.text = str(value)

    def update_scores(self, instance, value):
        self.score_value.text = str(value)

    def update_next_tetromino(self, instance, value):
        self.next_tetromino_widget.update_tetromino(value)

    def show_game_over(self, instance, value):
        if value:
            game_over_screen = GameOverScreen(
                score=instance.score, lines=instance.lines_cleared, level=instance.level
            )
            game_over_screen.open()


if __name__ == "__main__":
    TetrisApp().run()
