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
COOLDOWN = 0.5
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
        new_positions = [(x + dx, y + dy) for x, y in tetromino.current_each_tile_pos]

        if self.check_tetromino(
            new_positions, tetromino.current_each_tile_pos, direction
        ):
            tetromino.current_each_tile_pos = new_positions

        self.clear_line()
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

        for line_to_clear in sorted(lines_to_clear, reverse=True):
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
        self._running = False
        time.sleep(COOLDOWN)
        self._running = True

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
        self._current_tetromino = Tetromino(self._bag.choose())
        self.spawn_tetromino(self._current_tetromino)

    def drop_tetromino(self):
        while self._running:
            self.move_tetromino(self._current_tetromino, "down")
            time.sleep(DROP_INTERVAL)

    def stop(self):
        self._running = False


def play_tetris():
    os.system("cls" if os.name == "nt" else "clear")
    board = Board()

    while True:
        board.display()
        if keyboard.is_pressed("a"):
            board.move_tetromino(board._current_tetromino, "left")
        if keyboard.is_pressed("d"):
            board.move_tetromino(board._current_tetromino, "right")
        if keyboard.is_pressed("s"):
            board.move_tetromino(board._current_tetromino, "down")
        time.sleep(0.05)


if __name__ == "__main__":
    play_tetris()
