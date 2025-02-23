from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, InstructionGroup
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

        self._draw_grid_borders()
        self.grid_lines = InstructionGroup()
        self.canvas.add(self.grid_lines)
        self._draw_grid_lines()

        self.game = Tetris(GRID_COLS, GRID_ROWS)
        self.blocks = [[None] * GRID_COLS for _ in range(GRID_ROWS)]

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        self.handled_keys = set()

        Clock.schedule_interval(self.update_board, REFRESH_RATE)
        Clock.schedule_interval(self.move_step, MOVE_INTERVAL)

    def _draw_grid_lines(self) -> None:
        self.grid_lines.clear()
        self.grid_lines.add(Color(1, 1, 1, 0.4))
        for row in range(GRID_ROWS + 1):
            self.grid_lines.add(
                Line(
                    points=[0, row * CELL_SIZE, GRID_COLS * CELL_SIZE, row * CELL_SIZE],
                    width=1,
                )
            )
        for col in range(GRID_COLS + 1):
            self.grid_lines.add(
                Line(
                    points=[col * CELL_SIZE, 0, col * CELL_SIZE, GRID_ROWS * CELL_SIZE],
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
                        pos=(col * CELL_SIZE, row * CELL_SIZE),
                        size=(CELL_SIZE, CELL_SIZE),
                    )
                    self.blocks[row][col] = rect
                    self.canvas.add(
                        Color(
                            TETROMINO_COLORS[board_value][0],
                            TETROMINO_COLORS[board_value][1],
                            TETROMINO_COLORS[board_value][2],
                            1,
                        )
                    )
                    self.canvas.add(rect)
                elif board_value == 0 and self.blocks[row][col] is not None:
                    self.canvas.remove(self.blocks[row][col])
                    self.blocks[row][col] = None

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
