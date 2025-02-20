import numpy as np
import os
import time
import keyboard
import threading
import random

WIDTH = 10
HEIGHT = 20
DROP_INTERVAL = 1
CLEARLINE_NUM = 9

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

CW = [[0, 1], [-1, 0]]
CCW = [[0, -1], [1, 0]]

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
    def __init__(self):
        self._choices = list(PIECES.keys())
        self._index = 0
        self._random_pieces = []
        self.random_pieces()

    def random_pieces(self):
        self._index = 0
        self._random_pieces = []
        for _ in range(len(PIECES)):
            choose_piece = random.choice(self._choices)
            self._choices.remove(choose_piece)
            self._random_pieces.append(choose_piece)
        self._choices = list(PIECES.keys())

    def choose(self):
        choose_piece = self._random_pieces[self._index]
        self._index += 1
        if self._index == len(self._choices):
            self.random_pieces()
        return choose_piece


class Tetromino:
    def __init__(self, piece_type):
        self._piece_type = piece_type
        self.grid = self.generate()
        self.current_each_tile_pos = []
        self.is_set = False
        self.rotate_pos = 0
        self.rotate_point = None

    def generate(self):
        size = 4 if self._piece_type == "I" else 3
        coordinate_map = np.zeros((size, size), dtype=int)

        for coordinate in PIECES[self._piece_type]:
            x, y = coordinate
            if self._piece_type == "I":
                coordinate_map[y + 2, x] = 1
            else:
                coordinate_map[y + 1, x + 1] = 1

        return np.flipud(coordinate_map)

    def rotate_offset(self, board, direction, new_pos):
        if direction == "rotate-right":
            next_rotate_pos = (self.rotate_pos + 1) % 4
        elif direction == "rotate-left":
            next_rotate_pos = (self.rotate_pos - 1) % 4

        if self._piece_type == "I":
            offset_data = OFFSET_I[f"{self.rotate_pos}>{next_rotate_pos}"]
        else:
            offset_data = OFFSET_JLSTZ[f"{self.rotate_pos}>{next_rotate_pos}"]
        for offset_x, offset_y in offset_data:
            is_valid_rotate = True
            for new_tile in new_pos:
                next_x = new_tile[1] + offset_x
                next_y = new_tile[0] + offset_y
                if 0 <= next_x < WIDTH and 0 <= next_y < HEIGHT:
                    if (
                        board[next_y, next_x] != 0
                        and (next_y, next_x) not in self.current_each_tile_pos
                    ):
                        is_valid_rotate = False
                        break
                else:
                    is_valid_rotate = False
                    break
            if is_valid_rotate:
                self.rotate_pos = next_rotate_pos
                return (offset_x, offset_y)

        return False

    def rotate(self, board, direction):
        if self._piece_type == "O":
            return
        new_pos = []
        rotation_point = self.rotate_point

        for y, x in self.current_each_tile_pos:
            con_x = x - rotation_point[1]
            con_y = y - rotation_point[0]
            if direction == "rotate-right":
                con_pos = np.dot(CW, [con_x, con_y])
                final_pos = (
                    rotation_point[0] - int(con_pos[1]),
                    rotation_point[1] - int(con_pos[0]),
                )
                new_pos.append(final_pos)
            elif direction == "rotate-left":
                con_pos = np.dot(CCW, [con_x, con_y])
                final_pos = (
                    rotation_point[0] - int(con_pos[1]),
                    rotation_point[1] - int(con_pos[0]),
                )
                new_pos.append(final_pos)

        offset = self.rotate_offset(board, direction, new_pos)
        if offset:
            self.current_each_tile_pos = [
                (y + offset[1], x + offset[0]) for (y, x) in new_pos
            ]
            self.rotate_point = (
                self.rotate_point[0] + offset[1],
                self.rotate_point[1] + offset[0],
            )

    @property
    def piece_type(self):
        return self._piece_type


class Board:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self._board = np.zeros((height, width), dtype=int)
        self._width = width
        self._height = height
        self._tetrominos = []
        self._bag = Bag()
        self._current_tetromino = Tetromino(self._bag.choose())
        self._running = True
        self.spawn_tetromino(self._current_tetromino)

        threading.Timer(DROP_INTERVAL, self.start_drop_thread).start()

    def start_drop_thread(self):
        self.drop_thread = threading.Thread(
            target=self.drop_tetromino, daemon=True
        ).start()

    def spawn_tetromino(self, tetromino, x=3, y=0):
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
                        tetromino.current_each_tile_pos.append((board_y, board_x))

        self._tetrominos.append(self._current_tetromino)
        self.render()

    def check_tetromino(self, new_positions, current_positions, direction):
        for y, x in new_positions:
            if (y, x) not in current_positions:
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

    def move_tetromino(self, tetromino, direction):
        direction_map = {"right": (0, 1), "left": (0, -1), "down": (1, 0)}

        dx, dy = direction_map[direction]
        new_positions = []
        for x, y in tetromino.current_each_tile_pos:
            new_positions.append((x + dx, y + dy))
            if (x, y) == tetromino.rotate_point:
                new_rotate_point = (x + dx, y + dy)

        if self.check_tetromino(
            new_positions, tetromino.current_each_tile_pos, direction
        ):
            tetromino.current_each_tile_pos = new_positions
            tetromino.rotate_point = new_rotate_point

        self.render()

    def clear_line(self):
        stat = {i: 0 for i in range(20)}
        for tetromino in self._tetrominos:
            if tetromino.is_set == True:
                for y, x in tetromino.current_each_tile_pos:
                    stat[y] += 1

        lines_to_clear = [y for y in stat.keys() if stat[y] == 10]
        if not lines_to_clear:
            return False

        for line_to_clear in sorted(lines_to_clear):
            self._board[line_to_clear] = [CLEARLINE_NUM] * self._width
            self.display()
            for tetromino in self._tetrominos:
                if tetromino.is_set == True:
                    new_tile = []
                    for y, x in tetromino.current_each_tile_pos:
                        if y != line_to_clear:
                            if y < line_to_clear:
                                new_tile.append((y + 1, x))
                            else:
                                new_tile.append((y, x))
                    tetromino.current_each_tile_pos = new_tile

        time.sleep(DROP_INTERVAL)
        return

    def render(self):
        self._board = np.zeros((self._height, self._width), dtype=int)
        for piece in self._tetrominos:
            for tile in piece.current_each_tile_pos:
                self._board[tile[0], tile[1]] = PIECES_INDEX[piece.piece_type]

    def display(self):
        print("\033[?25l", end="")
        print("\033[H", end="")

        for row in self._board:
            print("".join([str(cell) if cell else "." for cell in row]))
        print(flush=True)

    def respawn_tetromino(self):
        self._current_tetromino.is_set = True
        self.clear_line()
        self._current_tetromino = Tetromino(self._bag.choose())
        self.spawn_tetromino(self._current_tetromino)

    def drop_tetromino(self):
        while self._running:
            if not self._current_tetromino.is_set:
                self.move_tetromino(self._current_tetromino, "down")
            time.sleep(DROP_INTERVAL)

    def stop(self):
        self._running = False

    def rotate_tetromino(self, direction):
        self._current_tetromino.rotate(self._board, direction)
        self.render()


def play_tetris():
    os.system("cls" if os.name == "nt" else "clear")
    board = Board()

    last_keys = set()  # Store previously pressed keys

    while True:
        board.display()
        current_keys = set()

        if keyboard.is_pressed("a"):
            board.move_tetromino(board._current_tetromino, "left")

        if keyboard.is_pressed("d"):
            board.move_tetromino(board._current_tetromino, "right")

        if keyboard.is_pressed("w"):
            board.move_tetromino(board._current_tetromino, "down")

        if keyboard.is_pressed("right"):
            current_keys.add("right")
            if "right" not in last_keys:
                board.rotate_tetromino("rotate-right")

        if keyboard.is_pressed("left"):
            current_keys.add("left")
            if "left" not in last_keys:
                board.rotate_tetromino("rotate-left")

        last_keys = current_keys
        time.sleep(0.05)


if __name__ == "__main__":
    play_tetris()
