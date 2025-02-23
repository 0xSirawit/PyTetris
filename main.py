from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.clock import Clock
from kivy.core.window import Window
from tetris import Tetris

GRID_COLS, GRID_ROWS = 10, 20
CELL_SIZE = 60
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


class TetrisBoard(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        self.size_hint = (None, None)
        self.size = (GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE)
        self.bind(size=self.redraw)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        self.handled_keys = set()
        self.game = Tetris(GRID_COLS, GRID_ROWS)
        Clock.schedule_interval(self.redraw, REFRESH_RATE)
        Clock.schedule_interval(self.move_step, MOVE_INTERVAL)
        with self.canvas:
            self._draw_grid_lines()

    def redraw(self, *args) -> None:
        self.canvas.remove_group("tetrominos")
        with self.canvas:
            self._draw_grid_borders()
            self._draw_blocks()

    def _draw_grid_lines(self) -> None:
        Color(1, 1, 1, 0.4)
        for row in range(GRID_ROWS + 1):
            Line(
                points=[0, row * CELL_SIZE, GRID_COLS * CELL_SIZE, row * CELL_SIZE],
                width=1,
            )
        for col in range(GRID_COLS + 1):
            Line(
                points=[col * CELL_SIZE, 0, col * CELL_SIZE, GRID_ROWS * CELL_SIZE],
                width=1,
            )

    def _draw_grid_borders(self) -> None:
        Color(1, 1, 1, 1)

        # Left border
        Line(points=[self.x, self.y, self.x, self.y + GRID_ROWS * CELL_SIZE], width=2)

        # Right border
        Line(
            points=[
                self.x + GRID_COLS * CELL_SIZE,
                self.y,
                self.x + GRID_COLS * CELL_SIZE,
                self.y + GRID_ROWS * CELL_SIZE,
            ],
            width=2,
        )

        # Bottom border
        Line(points=[self.x, self.y, self.x + GRID_COLS * CELL_SIZE, self.y], width=2)

    def _draw_blocks(self) -> None:
        for row in range(len(self.game.board)):
            for col in range(len(self.game.board[0])):
                board_value = self.game.board[row, col]
                if board_value != 0:
                    Color(
                        TETROMINO_COLORS[board_value][0],
                        TETROMINO_COLORS[board_value][1],
                        TETROMINO_COLORS[board_value][2],
                        1,
                    )
                    Rectangle(
                        pos=(col * CELL_SIZE, row * CELL_SIZE),
                        size=(CELL_SIZE, CELL_SIZE),
                        group="tetrominos",
                    )

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


class TetrisApp(App):
    def build(self) -> TetrisBoard:
        return TetrisBoard()


if __name__ == "__main__":
    TetrisApp().run()
