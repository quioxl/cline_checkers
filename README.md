# Python Checkers Game

A graphical implementation of the classic Checkers (Draughts) game written in Python using Pygame.

## Features

- Play against the computer or another player
- Three difficulty levels for computer opponent:
  - Easy: Makes random moves
  - Medium: Prefers jumps and king moves
  - Hard: More sophisticated strategy with prioritized captures
- Full implementation of checkers rules:
  - Mandatory jumps
  - Multiple jumps in a single turn
  - King pieces that can move in any diagonal direction
  - Win detection
- Graphical user interface with:
  - Visual board and pieces
  - Mouse-based interaction
  - Highlighted valid moves
  - Game over screen

## How to Play

1. Install the required dependencies:
   ```
   pip install pygame
   ```

2. Run the game:
   ```
   python checkers.py
   ```

3. Choose game mode by pressing the corresponding key:
   - Press `1` for One Player vs Computer
   - Press `2` for Two Players

4. If playing against the computer, select a difficulty level by pressing:
   - Press `1` for Easy
   - Press `2` for Medium
   - Press `3` for Hard

5. Game Controls:
   - Click on a piece to select it
   - Valid moves will be highlighted with blue circles
   - Click on a highlighted position to move the selected piece
   - The game automatically enforces the rules, including mandatory jumps

## Game Rules

- Red moves first
- Pieces can only move diagonally forward (toward the opponent's side)
- Kings can move diagonally in any direction
- If a jump is available, it must be taken
- Multiple jumps must be completed if possible
- A piece becomes a king when it reaches the opposite end of the board
- The game ends when a player has no valid moves or has lost all their pieces

## Code Structure

- `Piece`: Represents a checker piece (red/black, regular/king)
- `Board`: Manages the game board and valid move generation
- `Player`: Handles human player input through mouse interaction
- `ComputerPlayer`: Implements AI for the computer opponent
- `Game`: Coordinates game flow, rules enforcement, and graphical rendering
- `main()`: Entry point that sets up the game window and handles menu screens

## Requirements

- Python 3.6 or higher
- Pygame library
