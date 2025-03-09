import numpy as np
import os
import time
import keyboard
import threading
import random

WIDTH = 10
HEIGHT = 20
DROP_INIT_INTERVAL = 1
CLEARLINE_NUM = 9
ROTATION_MATRIX = {"CW": [[0, 1], [-1, 0]], "CCW": [[0, -1], [1, 0]]}

PIECES = {
    "L": [(0, 0), (-1, 0), (1, 0), (1, 1)],
    "S": [(0, 0), (-1, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (-1, 1), (0, 1), (1, 0)],
    "T": [(0, 0), (-1, 0), (0, 1), (1, 0)],
    "J": [(0, 0), (-1, 0), (-1, 1), (1, 0)],
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "I": [(0, 0), (-1, 0), (1, 0), (2, 0)],
}

PIECES_INDEX = {piece: index for index, piece in enumerate(PIECES.keys(), start=1)}

OFFSET_JLSTZ = {
    "0>1": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    "1>0": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    "1>2": [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    "2>1": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    "2>3": [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    "3>2": [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    "3>0": [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    "0>3": [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
}

OFFSET_I = {
    "0>1": [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    "1>0": [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
    "1>2": [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
    "2>1": [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    "2>3": [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
    "3>2": [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    "3>0": [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    "0>3": [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
}


class Bag:
    def __init__(self) -> None:
        self._available_pieces = list(PIECES.keys())
        self._total_pieces = len(self._available_pieces)
        self._current_index = 0
        self._shuffled_pieces = []
        self._shuffle_pieces()
        self._next_piece = None

    def _shuffle_pieces(self) -> None:
        self._current_index = 0
        self._shuffled_pieces = []

        for _ in range(self._total_pieces):
            choose_piece = random.choice(self._available_pieces)
            self._available_pieces.remove(choose_piece)
            self._shuffled_pieces.append(choose_piece)

        self._available_pieces = list(PIECES.keys())

    def choose(self) -> str:
        choose_piece = self._shuffled_pieces[self._current_index]
        self._current_index += 1

        if self._current_index < self._total_pieces:
            self._next_piece = self._shuffled_pieces[self._current_index]
        else:
            self._shuffle_pieces()
            self._next_piece = self._shuffled_pieces[0]

        return choose_piece

    @property
    def next_piece(self) -> str:
        return self._next_piece


class Tetromino:
    def __init__(self, piece_type: str) -> None:
        self._piece_type = piece_type
        self._grid = self.generate_coordinate()
        self._rotate_index = 0
        self.rotate_point = None
        self.tiles_pos = []
        self.is_set = False

    def generate_coordinate(self) -> np:
        if self._piece_type == "I":
            grid_size = 4
            coordinate_offset = (2, 0)
        else:
            grid_size = 3
            coordinate_offset = (1, 1)

        coordinate_map = np.zeros((grid_size, grid_size), dtype=int)
        for x, y in PIECES[self._piece_type]:
            coordinate_map[y + coordinate_offset[0], x + coordinate_offset[1]] = 1

        return np.flipud(coordinate_map)

    def rotate_offset(
        self, board: np, direction: str, new_tiles_pos: list
    ) -> tuple[int, int] | bool:
        rotation_step = 1 if direction == "CW" else -1
        next_rotate_index = (self._rotate_index + rotation_step) % 4

        if self._piece_type == "I":
            offset_data = OFFSET_I[f"{self._rotate_index}>{next_rotate_index}"]
        else:
            offset_data = OFFSET_JLSTZ[f"{self._rotate_index}>{next_rotate_index}"]

        for offset_x, offset_y in offset_data:
            if all(
                0 <= (next_x := new_tile[1] + offset_x) < WIDTH
                and 0 <= (next_y := new_tile[0] + offset_y) < HEIGHT
                and (board[next_y, next_x] == 0 or (next_y, next_x) in self.tiles_pos)
                for new_tile in new_tiles_pos
            ):
                self._rotate_index = next_rotate_index
                return offset_x, offset_y

        return False

    def rotate(self, board: np, direction: str) -> None:
        if self._piece_type == "O":
            return

        new_tiles_pos = []

        for tile_y, tile_x in self.tiles_pos:
            tile_coordinate_x = tile_x - self.rotate_point[1]
            tile_coordinate_y = tile_y - self.rotate_point[0]
            tile_coordinate_rotated = np.dot(
                ROTATION_MATRIX[direction], [tile_coordinate_x, tile_coordinate_y]
            )

            tile_position_rotated = (
                self.rotate_point[0] - int(tile_coordinate_rotated[1]),
                self.rotate_point[1] - int(tile_coordinate_rotated[0]),
            )
            new_tiles_pos.append(tile_position_rotated)

        offset = self.rotate_offset(board, direction, new_tiles_pos)
        if offset:
            self.tiles_pos = [
                (new_tile_y + offset[1], new_tile_x + offset[0])
                for (new_tile_y, new_tile_x) in new_tiles_pos
            ]
            self.rotate_point = (
                self.rotate_point[0] + offset[1],
                self.rotate_point[1] + offset[0],
            )

    @property
    def piece_type(self) -> str:
        return self._piece_type

    @property
    def grid(self) -> np:
        return self._grid


class Tetris:
    def __init__(self, width=WIDTH, height=HEIGHT, level: int = 1) -> None:
        self._board = np.zeros((height, width), dtype=int)
        self._width = width
        self._height = height
        self._tetrominos = []
        self._bag = Bag()
        self._current_tetromino = Tetromino(self._bag.choose())
        self._running = True
        self.is_game_over = False
        self.spawn_tetromino(self._current_tetromino)
        self._total_clear_line = 0
        self._level = level
        self._level_progression = 0
        self._score = 0
        self._drop_interval = self.cal_drop_interval(level)
        threading.Timer(self._drop_interval, self.start_drop_thread).start()

    def cal_drop_interval(self, level: int) -> float:
        caled_drop_interval = 1
        if self._level <= 10:
            caled_drop_interval = (DROP_INIT_INTERVAL / 14) * (15 - self._level)
        else:
            if self._level >= 13:
                caled_drop_interval = (DROP_INIT_INTERVAL / 14) * 4
            if self._level >= 16:
                caled_drop_interval = (DROP_INIT_INTERVAL / 14) * 3
            if self._level >= 19:
                caled_drop_interval = (DROP_INIT_INTERVAL / 14) * 2
            if self._level >= 29:
                caled_drop_interval = (DROP_INIT_INTERVAL / 14) * 1
            else:
                caled_drop_interval = (DROP_INIT_INTERVAL / 14) * 5

        return caled_drop_interval

    def cal_score(self, level: int, num_line: int) -> int:
        if num_line == 1:
            score = level * 40
        if num_line == 2:
            score = level * 100
        if num_line == 3:
            score = level * 300
        if num_line == 4:
            score = level * 1200
        return score

    def start_drop_thread(self) -> None:
        self.drop_thread = threading.Thread(
            target=self.drop_tetromino, daemon=True
        ).start()

    def drop_tetromino(self):
        while self._running:
            if not self._current_tetromino.is_set:
                self.move_tetromino("down")
            time.sleep(self._drop_interval)

    def stop(self):
        self._running = False

    def spawn_tetromino(self, tetromino: object, x=3, y=0) -> None:
        piece_grid = tetromino.grid
        h, w = piece_grid.shape

        for i in range(h):
            for j in range(w):
                if piece_grid[i, j] == 1:
                    board_y = y + i if tetromino.piece_type != "I" else (y - 1) + i
                    board_x = x + j
                    if 0 <= board_y < self._height and 0 <= board_x < self._width:
                        if [i, j] == [1, 1]:
                            tetromino.rotate_point = (board_y, board_x)
                        tetromino.tiles_pos.append((board_y, board_x))
                        if self._board[board_y, board_x] != 0:
                            self._running = False
                            self._board = np.zeros((20, 10), dtype=int)
                            self.is_game_over = True

        self._tetrominos.append(self._current_tetromino)
        self.render()

    def respawn_tetromino(self) -> None:
        self._current_tetromino.is_set = True
        self.clear_line()
        self._current_tetromino = Tetromino(self._bag.choose())
        self.spawn_tetromino(self._current_tetromino)

    def check_tetromino(self, new_positions: list, direction: str) -> bool:
        for y, x in new_positions:
            if (y, x) in self._current_tetromino.tiles_pos:
                continue
            if y >= self._height:
                self.respawn_tetromino()
                return False
            if not (0 <= y < self._height and 0 <= x < self._width):
                return False
            if y < self._height and direction == "down" and self._board[y, x] != 0:
                self.respawn_tetromino()
                return False
            if self._board[y, x] != 0:
                return False
        return True

    def move_tetromino(self, direction: str) -> None:
        if self.is_game_over:
            return
        direction_map = {"right": (0, 1), "left": (0, -1), "down": (1, 0)}

        dx, dy = direction_map[direction]
        new_positions = []
        for x, y in self._current_tetromino.tiles_pos:
            new_positions.append((x + dx, y + dy))
            if (x, y) == self._current_tetromino.rotate_point:
                new_rotate_point = (x + dx, y + dy)

        if self.check_tetromino(new_positions, direction):
            self._current_tetromino.tiles_pos = new_positions
            if new_rotate_point:
                self._current_tetromino.rotate_point = new_rotate_point

        self.render()

    def clear_line(self) -> None:
        line_counts = {y: 0 for y in range(20)}
        for tetromino in self._tetrominos:
            if tetromino.is_set:
                for y, _ in tetromino.tiles_pos:
                    line_counts[y] += 1

        lines_to_clear = [y for y, count in line_counts.items() if count == 10]
        if not lines_to_clear:
            return False

        for line in sorted(lines_to_clear):
            self._board[line] = [CLEARLINE_NUM] * self._width
            # self.display()

            for tetromino in self._tetrominos:
                if tetromino.is_set:
                    new_tiles_pos = []
                    for tile_y, tile_x in tetromino.tiles_pos:
                        if tile_y != line:
                            if tile_y < line:
                                new_tiles_pos.append((tile_y + 1, tile_x))
                            else:
                                new_tiles_pos.append((tile_y, tile_x))
                    tetromino.tiles_pos = new_tiles_pos

        # time.sleep(self._drop_interval)
        lines_to_clear_amount = len(lines_to_clear)
        self._total_clear_line += lines_to_clear_amount
        self._level_progression += lines_to_clear_amount
        if self._level_progression >= 10:
            self._level += 1
            self._level_progression = self._level_progression % 10
        self._drop_interval = self.cal_drop_interval(self._level)
        self._score += self.cal_score(self._level, lines_to_clear_amount)
        return

    def rotate_tetromino(self, direction: str):
        if self.is_game_over:
            return
        self._current_tetromino.rotate(self._board, direction)
        self.render()

    def render(self) -> None:
        self._board = np.zeros((self._height, self._width), dtype=int)
        for piece in self._tetrominos:
            for tile in piece.tiles_pos:
                self._board[tile[0], tile[1]] = PIECES_INDEX[piece.piece_type]

    def display(self):
        print("\033[?25l", end="")
        print("\033[H", end="")

        for row in self._board:
            print("".join([str(cell) if cell else "." for cell in row]))
        print(flush=True)

    @property
    def board(self):
        return np.flipud(self._board)

    @property
    def total_clear_line(self):
        return self._total_clear_line

    @property
    def level(self):
        return self._level

    @property
    def score(self):
        return self._score

    @property
    def bag(self):
        return self._bag


def play_tetris():
    os.system("cls" if os.name == "nt" else "clear")
    game = Tetris()

    last_keys = set()  # Store previously pressed keys

    try:
        while True:
            game.display()
            current_keys = set()

            if keyboard.is_pressed("a"):
                game.move_tetromino("left")

            if keyboard.is_pressed("d"):
                game.move_tetromino("right")

            if keyboard.is_pressed("w"):
                game.move_tetromino("down")

            if keyboard.is_pressed("right"):
                current_keys.add("right")
                if "right" not in last_keys:
                    game.rotate_tetromino("CW")

            if keyboard.is_pressed("left"):
                current_keys.add("left")
                if "left" not in last_keys:
                    game.rotate_tetromino("CCW")

            last_keys = current_keys
            time.sleep(0.05)

    except KeyboardInterrupt:
        game.stop()
        keyboard.unhook_all()
        print("\033[?25h")  # Restore cursor visibility


if __name__ == "__main__":
    play_tetris()
