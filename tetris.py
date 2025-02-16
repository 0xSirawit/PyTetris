import numpy as np
import os
import time
import keyboard

WIDTH = 10
HEIGHT = 20

PIECES = {
    'L': [(0, 0), (-1, 0), (1, 0), (1, 1)],
    'S': [(0, 0), (-1, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (-1, 1), (0, 1), (1, 0)],
    'T': [(0, 0), (-1, 0), (0, 1), (1, 0)],
    'J': [(0, 0), (-1, 0), (-1, 1), (1, 0)],
    'I': [(0, 0), (-1, 0), (1, 0), (2, 0)]
}

class Tetromino:
    def __init__(self, piece_type):
        self._piece_type = piece_type
        self.grid = self.generate()
        self.current_each_tile_pos = []
        self.is_set = False

    def generate(self):
        condinate_piece = PIECES[self._piece_type]
        condinate_map = np.zeros((3, 3), dtype=int)
        for codinate in condinate_piece:
            condinate_map[codinate[1] + 1, codinate[0] + 1] = 1
        return np.flipud(condinate_map)

class Board:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self._board = np.flipud(np.zeros((height, width), dtype=int))
        self._width = width
        self._height = height
        self._tetrominos = []

    def place_tetromino(self, tetromino, x=3, y=0):
        piece_grid = tetromino.grid
        h, w = piece_grid.shape

        for i in range(h):
            for j in range(w):
                if piece_grid[i, j] == 1:
                    board_y = y + i
                    board_x = x + j
                    if 0 <= board_y < self._height and 0 <= board_x < self._width:
                        tetromino.current_each_tile_pos.append((board_y, board_x))
                        
        self._tetrominos.append(tetromino)
        self.render()

    def move_tetromino(self, tetromino, direction):
        new_pos = []
        for tile in tetromino.current_each_tile_pos:
            if direction == "right":
                if tile[1] + 1 < self._width: new_pos.append((tile[0], tile[1] + 1))        
                else: return
            elif direction == "left":
                if tile[1] - 1 >= 0: new_pos.append((tile[0], tile[1] - 1))
                else: return
            elif direction == "down":
                if tile[0] + 1 < self._height: new_pos.append((tile[0]+1, tile[1]))      
                else: return

        if all(0 <= pos[1] < self._width for pos in new_pos):
            tetromino.current_each_tile_pos = new_pos
        
        self.render()

    def render(self):
        self._board = np.zeros((self._height, self._width), dtype=int)
        for piece in self._tetrominos:
            for tile in piece.current_each_tile_pos:
                self._board[tile[0], tile[1]] = 1

    def display(self):
        print("\033[?25l", end="")
        print("\033[H", end="")

        for row in self._board:
            print("".join(["1" if cell else "0" for cell in row]))

        print(flush=True)

def play_tetris():
    os.system("cls" if os.name == "nt" else "clear")
    board = Board()
    tetromino = Tetromino('J')
    board.place_tetromino(tetromino)
    
    while True:
        board.display()
        if keyboard.is_pressed('a'):
            board.move_tetromino(tetromino, 'left')
        if keyboard.is_pressed('d'):
            board.move_tetromino(tetromino, 'right')
        if keyboard.is_pressed('s'):
            board.move_tetromino(tetromino, 'down')
        time.sleep(0.1)

if __name__ == "__main__":
    play_tetris()
