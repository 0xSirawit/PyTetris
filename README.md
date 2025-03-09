# PyTetris
<small>240-123DATA STRU, ALGOR & PRO MODULE</small> <br>
This project is a modern implementation of the classic Tetris game using Python and the Kivy framework.

## Contributor
[@tawanza11](https://github.com/tawanza11) - Pechchanan Suwanrak 6710110298 <br>
[@sorazzzz-ui](https://github.com/sorazzzz-ui) - Sarankorn Nachailuck 6710110396 <br>
[@0xSirawit](https://github.com/0xSirawit) - Sirawit Loywirat 6710110443 <br>

## Features

- Classic Tetris gameplay (NES)
- SRS Rotation system
- Score tracking
- Different levels of difficulty
- Simple and intuitive controls
- Multi game mode

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/0xSirawit/PyTetris.git
    ```
2. Navigate to the project directory:
    ```bash
    cd PyTetris
    ```
3. Install the required dependencies:
    ```bash
    pip install kivy numpy
    ```

## Usage

To start the game, run the following command:
```bash
python main.py
```

## Controls
- **W** - Soft Drop
- **A** - Move Left
- **D** - Move Right
- **Arrow Right** - Rotate Clockwise
- **Arrow Left** - Rotate Counterclockwise

## Code Overview

### Project Structure

The project is organized into several Python files, each with specific responsibilities:

- **Main Application Files**:
  - `main.py`: Entry point for the application, manages the screen system and menu
  - `tetris.py`: Core game logic, board management, and tetromino movement
  
- **Screen Modules**:
  - `screen/modeClassic.py`: Implementation of the classic endless Tetris mode
  - `screen/mode40Line.py`: Implementation of the 40-line challenge mode
  - `screen/HowToPlay.py`: Instructions screen for players

### Key Components

#### 1. Tetromino System

The game uses a classic 7-piece tetromino system (I, J, L, O, S, T, Z). Each piece has its own shape, color, and rotation characteristics.

```python
TETROMINO_SHAPES = {
    "L": [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "S": [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "Z": [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "T": [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "J": [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "O": [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    "I": [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
}
```

#### 2. Bag Randomizer

The game uses a "bag" system to ensure a fair distribution of tetrominoes:

```python
class Bag:
    def __init__(self) -> None:
        self._available_pieces = list(PIECES.keys())
        self._total_pieces = len(self._available_pieces)
        self._current_index = 0
        self._shuffled_pieces = []
        self._shuffle_pieces()
        self._next_piece = None
```

Instead of pure randomness, this system shuffles all seven tetrominoes and deals them out in order, ensuring that players will receive each piece exactly once before getting any repeats.

#### 3. Game Board

The game board is represented as a NumPy array:

```python
self._board = np.zeros((height, width), dtype=int)
```

Non-zero values in the array represent placed tetrominoes, with different numbers corresponding to different tetromino types.

#### 4. SRS Rotation System

The game implements the Super Rotation System (SRS) for tetromino rotations, including wall kicks:

```python
OFFSET_JLSTZ = {
    "0>1": [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    # ... more offsets
}

OFFSET_I = {
    "0>1": [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    # ... more offsets
}
```

This system tries different positions when a rotation would otherwise be blocked by walls or other pieces.

#### 5. UI Implementation

The game uses Kivy for the user interface, creating a responsive and visually appealing playing experience:

```python
class TetrisBoard(Widget):
    lines_cleared = NumericProperty(0)
    level = NumericProperty(0)
    score = NumericProperty(0)
    next_tetromino = StringProperty("")
    game_over = BooleanProperty(False)
    
    # ... implementation
```
Kivy's property system allows for reactive UI updates when game state changes.

## Example
![image](https://github.com/user-attachments/assets/1417e6bd-7a99-4e54-841b-ad19a3f14186)
![image](https://github.com/user-attachments/assets/86f86f46-eae6-4408-a980-db6405adc983)
![image](https://github.com/user-attachments/assets/dd3052e6-2465-44bb-a9cc-c3a776dc6659)
![image](https://github.com/user-attachments/assets/d6e70666-fbc3-45bf-9dd9-f4781470ed2e)

