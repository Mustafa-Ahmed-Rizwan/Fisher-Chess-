# Chess960 (Fischer Random Chess)

## Overview

Chess960, also known as Fischer Random Chess, is a chess variant with 960 possible starting positions, randomizing the back-rank pieces to reduce reliance on memorized openings. This project implements a fully functional Chess960 game with a Pygame-based graphical user interface (GUI), an AI opponent powered by the Negamax algorithm with Alpha-Beta pruning, and a data analysis module to evaluate AI performance. Key features include animated moves, sound effects, customizable board themes, and game data tracking. The project showcases skills in Python programming, AI development, GUI design, and data analysis, making it an engaging platform for chess enthusiasts and AI researchers.


![image](https://github.com/user-attachments/assets/bce6a013-4679-4f09-9a96-2d5bfde90059)


---

## Demo Video

Watch a demo of the Chess960 game, showcasing gameplay, AI moves, and the user interface.


https://github.com/user-attachments/assets/a33c2fc8-6e74-42a9-97d4-b77eb16bddf6



---

## Features

- **Chess960 Gameplay**: Supports all 960 starting positions with randomized back-rank pieces, adhering to official rules (bishops on opposite-colored squares, king between rooks).
- **AI Opponent**: Powered by Negamax with Alpha-Beta pruning, optimized for Chess960 with bishop pair bonuses (+0.5) and rook development penalties (-0.3).
- **GUI**: Pygame-based interface with:
  - Animated piece movements and sound effects (move, capture, check, game-end).
  - Five board themes (blue, black-and-white, green, wood, purple).
  - Sidebar for move history (with scrolling), undo/redo buttons, and quit option.
- **Game Settings**: Tkinter menu to choose player color (White, Black, Random) and board theme.
- **Data Analysis**: Saves game data to `game_data.csv` and generates AI performance reports (`chess960_ai_report.txt`) with win rate, decision time, and outcome distribution.
- **Flexible Rules**: Implements Chess960-specific castling, en passant, pawn promotion, and 50-move rule draws.

---

## Requirements

- **Python**: 3.8 or higher
- **Dependencies** (listed in `requirements.txt`):

  ```
  numpy>=2.2.5
  pandas>=2.2.3
  pygame>=2.6.1
  ```
- **Assets**:
  - Chess piece images (`utils/images/*.png`, e.g., `wK.png`, `bQ.png`).
  - Sound effects (`utils/sounds/*.wav`, e.g., `move.wav`, `check.wav`).
  - Note: These assets are not included in the repository. Use placeholder images/sounds or source your own.

---

## Installation

1. **Clone the Repository**:

   ```bash
   https://github.com/Mustafa-Ahmed-Rizwan/Fisher-Chess-.git
   ```

2. **Create a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Assets**:

   - Place chess piece images in `utils/images/` (e.g., `wK.png` for white king).
   - Place sound effects in `utils/sounds/` (e.g., `move.wav`, `capture.wav`).
   - Alternatively, use placeholder assets (e.g., blank PNGs or silent WAVs) for testing.

---

## Usage

1. **Run the Game**:

   ```bash
   python chess_main.py
   ```

   - The Tkinter menu appears:
     - Select player color: White, Black, or Random.
     - Choose a board theme: blue, green, wood, purple, or black-and-white.
     - Click "Start Chess960 Game!".
   - Gameplay:
     - Click a piece to select it (highlighted with valid moves in green, captures in red).
     - Click a destination square to move.
     - For pawn promotion, enter `q` (Queen), `k` (Knight), `r` (Rook), or `b` (Bishop) in the console.
     - Use the sidebar to:
       - Undo moves (left arrow or button).
       - Redo moves (right arrow or button).
       - Quit to the menu.
     - Move history is displayed in algebraic notation, with scrolling for long games.

2. **Analyze AI Performance**:

   ```bash
   python analyze_game_data.py
   ```

   - Reads `game_data.csv` (generated after games).
   - Outputs AI win rate, average decision time, and outcome distribution to `chess960_ai_report.txt` and console.

3. **Game Data**:

   - Saved to `game_data.csv` upon game completion (checkmate or stalemate).
   - Columns: `game_id`, `outcome`, `winner`, `move_count`, `avg_decision_time`, `starting_position`, `timestamp`.

---

## Project Structure

```
chess960/
├── Fisher Chess.exe            # Standalone executable (Windows)
├── chess_main.py               # Main GUI driver (Pygame)
├── chess_engine.py             # Game state and move validation
├── chess_board.py              # Board setup and Chess960 position generation
├── chess_pieces.py             # Chess piece definitions
├── chess_ai.py                 # AI with Negamax and Alpha-Beta pruning
├── chess_menu.py               # Tkinter-based game settings menu
├── chess_themes.py             # Board color themes
├── analyze_game_data.py        # AI performance analysis script
├── utils/
│   ├── images/                # Chess piece images (e.g., wK.png)
│   └── sounds/                # Sound effects (e.g., move.wav)
├── chess960_ai_report.txt     # Output: AI performance report
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit changes:

   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:

   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request with a clear description of your changes.

Please ensure code follows PEP 8 style guidelines and includes docstrings for new functions.

---

## Acknowledgments

- **Bobby Fischer**: For inventing Chess960, inspiring this project.
- **Pygame Community**: For providing a robust library for GUI and sound.
- **Pandas and NumPy**: For enabling efficient data analysis and board management.
- **Tkinter**: For the game settings menu.
- **AI Resources**: Concepts from *Artificial Intelligence: A Modern Approach* by Norvig and Russell informed the Negamax implementation.
