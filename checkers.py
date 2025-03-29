import random
import time
import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

# Create crown image programmatically
def create_crown_image():
    """Create a crown image for king pieces."""
    surface = pygame.Surface((44, 25), pygame.SRCALPHA)
    pygame.draw.polygon(surface, GOLD, [(0, 25), (44, 25), (44, 15), (33, 15), (33, 0), (22, 15), (11, 0), (11, 15), (0, 15)])
    return surface

CROWN = create_crown_image()

class Piece:
    """Represents a checker piece on the board."""
    
    def __init__(self, color, row, col, king=False):
        """
        Initialize a new piece.
        
        Args:
            color (str): 'red' or 'black'
            row (int): Row position on the board
            col (int): Column position on the board
            king (bool): Whether the piece is a king
        """
        self.color = color
        self.row = row
        self.col = col
        self.king = king
        self.x = 0
        self.y = 0
        self.calc_pos()
        
    def calc_pos(self):
        """Calculate the pixel position of the piece."""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
        
    def make_king(self):
        """Promote the piece to a king."""
        self.king = True
        
    def draw(self, win):
        """Draw the piece on the window."""
        radius = SQUARE_SIZE // 2 - 10
        pygame.draw.circle(win, GRAY, (self.x, self.y), radius + 2)
        pygame.draw.circle(win, RED if self.color == 'red' else BLACK, (self.x, self.y), radius)
        if self.king:
            # Create a small white circle in the middle to represent a king
            pygame.draw.circle(win, WHITE, (self.x, self.y), radius // 2)
            
    def move(self, row, col):
        """Move the piece to a new position."""
        self.row = row
        self.col = col
        self.calc_pos()


class Board:
    """Represents the checkers game board."""
    
    def __init__(self):
        """Initialize a new board with pieces in starting positions."""
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.red_left = self.black_left = 12
        self.red_kings = self.black_kings = 0
        self.setup_board()
        
    def draw_squares(self, win):
        """Draw the checkerboard squares."""
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, BLACK, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def setup_board(self):
        """Set up the board with pieces in starting positions."""
        # Place black pieces (top of board)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only on black squares
                    self.grid[row][col] = Piece('black', row, col)
                    
        # Place red pieces (bottom of board)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only on black squares
                    self.grid[row][col] = Piece('red', row, col)
    
    def draw(self, win):
        """Draw the board and all pieces."""
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.grid[row][col]
                if piece:
                    piece.draw(win)
    
    def get_piece(self, row, col):
        """Get the piece at the specified position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from one position to another.
        
        Args:
            from_pos (tuple): (row, col) of the piece to move
            to_pos (tuple): (row, col) of the destination
            
        Returns:
            list: Positions of any captured pieces
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece and move it
        piece = self.grid[from_row][from_col]
        self.grid[from_row][from_col] = None
        
        # Update piece position
        piece.move(to_row, to_col)
        self.grid[to_row][to_col] = piece
        
        # Check if the piece should be kinged
        if (piece.color == 'red' and to_row == 0) or (piece.color == 'black' and to_row == 7):
            piece.make_king()
            if piece.color == 'red':
                self.red_kings += 1
            else:
                self.black_kings += 1
            
        # Check if a piece was captured
        captured = []
        if abs(from_row - to_row) == 2:  # A jump move
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            captured_piece = self.grid[mid_row][mid_col]
            if captured_piece:
                if captured_piece.color == 'red':
                    self.red_left -= 1
                    if captured_piece.king:
                        self.red_kings -= 1
                else:
                    self.black_left -= 1
                    if captured_piece.king:
                        self.black_kings -= 1
            
            captured.append((mid_row, mid_col))
            self.grid[mid_row][mid_col] = None
            
        return captured
    
    def get_valid_moves(self, row, col, jump_only=False):
        """
        Get all valid moves for a piece at the specified position.
        
        Args:
            row (int): Row of the piece
            col (int): Column of the piece
            jump_only (bool): Whether to only return jump moves
            
        Returns:
            dict: Dictionary mapping destination positions to captured positions
        """
        piece = self.get_piece(row, col)
        if piece is None:
            return {}
            
        moves = {}
        directions = []
        
        # Determine valid move directions based on piece color and king status
        if piece.color == 'red' or piece.king:
            directions.extend([(-1, -1), (-1, 1)])  # Up-left and up-right
        if piece.color == 'black' or piece.king:
            directions.extend([(1, -1), (1, 1)])    # Down-left and down-right
            
        # Check for jump moves
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                adjacent = self.get_piece(r, c)
                if adjacent and adjacent.color != piece.color:
                    jump_r, jump_c = r + dr, c + dc
                    if 0 <= jump_r < 8 and 0 <= jump_c < 8 and self.get_piece(jump_r, jump_c) is None:
                        moves[(jump_r, jump_c)] = [(r, c)]
        
        # If there are jump moves or we only want jump moves, return now
        if moves or jump_only:
            return moves
            
        # Check for regular moves
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.get_piece(r, c) is None:
                moves[(r, c)] = []
                
        return moves
    
    def get_all_valid_moves(self, color, jump_only=False):
        """
        Get all valid moves for all pieces of the specified color.
        
        Args:
            color (str): 'red' or 'black'
            jump_only (bool): Whether to only return jump moves
            
        Returns:
            dict: Dictionary mapping source positions to valid moves
        """
        all_moves = {}
        
        # Check if any piece can jump
        has_jumps = False
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = self.get_valid_moves(row, col, jump_only=True)
                    if moves:
                        has_jumps = True
                        all_moves[(row, col)] = moves
        
        # If there are jump moves or we only want jump moves, return now
        if has_jumps or jump_only:
            return all_moves
            
        # Otherwise, get all regular moves
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        all_moves[(row, col)] = moves
                        
        return all_moves
    
    def get_winner(self):
        """Check if there's a winner."""
        if self.red_left <= 0:
            return 'black'
        elif self.black_left <= 0:
            return 'red'
        return None


class Player:
    """Represents a human player."""
    
    def __init__(self, color):
        """
        Initialize a new player.
        
        Args:
            color (str): 'red' or 'black'
        """
        self.color = color
        self.selected_piece = None
        self.valid_moves = {}
        
    def get_move(self, board, game_valid_moves):
        """
        Get the player's move through mouse interaction.
        
        Args:
            board (Board): The game board
            game_valid_moves (dict): Dictionary of valid moves from the game
            
        Returns:
            tuple: ((from_row, from_col), (to_row, to_col)) or None if no move yet
        """
        self.valid_moves = game_valid_moves
        return None  # No move yet, will be handled by event processing
    
    def select(self, row, col, board):
        """
        Select a piece or move a selected piece.
        
        Args:
            row (int): Row position
            col (int): Column position
            board (Board): The game board
            
        Returns:
            bool: True if a move was made, False otherwise
        """
        # If a piece is already selected
        if self.selected_piece:
            # Try to move the selected piece
            result = self._move(row, col)
            if not result:
                # If the move is invalid, deselect and try to select a new piece
                self.selected_piece = None
                return self.select(row, col, board)
            return result
                
        # Try to select a piece
        piece = board.get_piece(row, col)
        if piece and piece.color == self.color:
            # Check if this piece has valid moves
            for from_pos, moves in self.valid_moves.items():
                if from_pos == (row, col) and moves:
                    self.selected_piece = piece
                    return True
                    
        return False
    
    def _move(self, row, col):
        """
        Move the selected piece to the specified position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            tuple: ((from_row, from_col), (to_row, to_col)) if valid move, None otherwise
        """
        from_pos = (self.selected_piece.row, self.selected_piece.col)
        
        # Check if the move is valid
        if from_pos in self.valid_moves:
            for to_pos in self.valid_moves[from_pos]:
                if to_pos == (row, col):
                    return (from_pos, to_pos)
                    
        return None


class ComputerPlayer:
    """Represents a computer player."""
    
    def __init__(self, color, difficulty='medium'):
        """
        Initialize a new computer player.
        
        Args:
            color (str): 'red' or 'black'
            difficulty (str): 'easy', 'medium', or 'hard'
        """
        self.color = color
        self.difficulty = difficulty
        
    def get_move(self, board, valid_moves):
        """
        Get the computer's move.
        
        Args:
            board (Board): The game board
            valid_moves (dict): Dictionary of valid moves
            
        Returns:
            tuple: ((from_row, from_col), (to_row, to_col))
        """
        if not valid_moves:
            return None
            
        # Simulate thinking
        pygame.time.delay(500)  # 500ms delay to simulate thinking
        
        # Easy: Random move
        if self.difficulty == 'easy':
            from_pos = random.choice(list(valid_moves.keys()))
            to_pos = random.choice(list(valid_moves[from_pos].keys()))
            return (from_pos, to_pos)
            
        # Medium: Prefer jumps and king moves
        elif self.difficulty == 'medium':
            # Prefer jumps
            jump_moves = {}
            for from_pos, moves in valid_moves.items():
                jump_moves_for_piece = {to_pos: captures for to_pos, captures in moves.items() if captures}
                if jump_moves_for_piece:
                    jump_moves[from_pos] = jump_moves_for_piece
            
            if jump_moves:
                from_pos = random.choice(list(jump_moves.keys()))
                to_pos = random.choice(list(jump_moves[from_pos].keys()))
                return (from_pos, to_pos)
            
            # Prefer moves that make kings
            king_moves = {}
            for from_pos, moves in valid_moves.items():
                from_row, from_col = from_pos
                piece = board.get_piece(from_row, from_col)
                if not piece.king:
                    king_row = 0 if self.color == 'red' else 7
                    king_moves_for_piece = {to_pos: captures for to_pos, captures in moves.items() 
                                           if to_pos[0] == king_row}
                    if king_moves_for_piece:
                        king_moves[from_pos] = king_moves_for_piece
            
            if king_moves:
                from_pos = random.choice(list(king_moves.keys()))
                to_pos = random.choice(list(king_moves[from_pos].keys()))
                return (from_pos, to_pos)
            
            # Otherwise, random move
            from_pos = random.choice(list(valid_moves.keys()))
            to_pos = random.choice(list(valid_moves[from_pos].keys()))
            return (from_pos, to_pos)
            
        # Hard: More sophisticated strategy (simplified for this example)
        else:
            # Prefer jumps
            jump_moves = {}
            for from_pos, moves in valid_moves.items():
                jump_moves_for_piece = {to_pos: captures for to_pos, captures in moves.items() if captures}
                if jump_moves_for_piece:
                    jump_moves[from_pos] = jump_moves_for_piece
            
            if jump_moves:
                # Find the move that captures the most pieces
                best_from_pos = None
                best_to_pos = None
                most_captures = 0
                
                for from_pos, moves in jump_moves.items():
                    for to_pos, captures in moves.items():
                        if len(captures) > most_captures:
                            most_captures = len(captures)
                            best_from_pos = from_pos
                            best_to_pos = to_pos
                
                return (best_from_pos, best_to_pos)
            
            # Prefer moves that make kings
            king_moves = {}
            for from_pos, moves in valid_moves.items():
                from_row, from_col = from_pos
                piece = board.get_piece(from_row, from_col)
                if not piece.king:
                    king_row = 0 if self.color == 'red' else 7
                    king_moves_for_piece = {to_pos: captures for to_pos, captures in moves.items() 
                                           if to_pos[0] == king_row}
                    if king_moves_for_piece:
                        king_moves[from_pos] = king_moves_for_piece
            
            if king_moves:
                from_pos = random.choice(list(king_moves.keys()))
                to_pos = random.choice(list(king_moves[from_pos].keys()))
                return (from_pos, to_pos)
            
            # Prefer moves that protect pieces
            # (simplified implementation)
            from_pos = random.choice(list(valid_moves.keys()))
            to_pos = random.choice(list(valid_moves[from_pos].keys()))
            return (from_pos, to_pos)


class Game:
    """Manages the checkers game."""
    
    def __init__(self, win, mode='two_player', difficulty='medium'):
        """
        Initialize a new game.
        
        Args:
            win (pygame.Surface): The game window
            mode (str): 'one_player' or 'two_player'
            difficulty (str): 'easy', 'medium', or 'hard'
        """
        self.win = win
        self.board = Board()
        self.mode = mode
        self.current_color = 'red'  # Red goes first
        self.selected_piece = None
        self.valid_moves = {}
        
        # Set up players
        if mode == 'one_player':
            self.players = {
                'red': Player('red'),
                'black': ComputerPlayer('black', difficulty)
            }
        else:
            self.players = {
                'red': Player('red'),
                'black': Player('black')
            }
            
        self.game_over = False
        self.winner = None
        self.waiting_for_player = False
        
    def switch_turn(self):
        """Switch to the other player's turn."""
        self.current_color = 'black' if self.current_color == 'red' else 'red'
        
    def check_game_over(self):
        """Check if the game is over."""
        red_moves = self.board.get_all_valid_moves('red')
        black_moves = self.board.get_all_valid_moves('black')
        
        if not red_moves:
            self.game_over = True
            self.winner = 'black'
        elif not black_moves:
            self.game_over = True
            self.winner = 'red'
            
    def update(self):
        """Update the game state and draw the board."""
        self.board.draw(self.win)
        self.draw_valid_moves()
        pygame.display.update()
        
    def draw_valid_moves(self):
        """Draw valid move indicators."""
        if self.selected_piece:
            row, col = self.selected_piece.row, self.selected_piece.col
            if (row, col) in self.valid_moves:
                for move in self.valid_moves[(row, col)]:
                    r, c = move
                    # Draw a blue circle to indicate valid move
                    pygame.draw.circle(self.win, BLUE, 
                                      (c * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                       r * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                      15)
    
    def select(self, row, col):
        """
        Select a piece or move a selected piece.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if a move was made, False otherwise
        """
        # If a piece is already selected
        if self.selected_piece:
            # Try to move the selected piece
            result = self._move(row, col)
            if not result:
                # If the move is invalid, deselect and try to select a new piece
                self.selected_piece = None
                # Don't recursively call select here, just return False
                return False
            return result
                
        # Try to select a piece
        piece = self.board.get_piece(row, col)
        if piece and piece.color == self.current_color:
            # Check if this piece has valid moves
            for from_pos, moves in self.valid_moves.items():
                if from_pos == (row, col) and moves:
                    self.selected_piece = piece
                    return True
                    
        return False
    
    def _move(self, row, col):
        """
        Move the selected piece to the specified position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if the move was valid, False otherwise
        """
        from_pos = (self.selected_piece.row, self.selected_piece.col)
        
        # Check if the move is valid
        if from_pos in self.valid_moves:
            for to_pos in self.valid_moves[from_pos]:
                if to_pos == (row, col):
                    # Make the move
                    captured = self.board.move_piece(from_pos, to_pos)
                    self.selected_piece = None
                    
                    # Check for additional jumps
                    if captured:
                        jump_moves = self.board.get_valid_moves(row, col, jump_only=True)
                        if jump_moves:
                            self.selected_piece = self.board.get_piece(row, col)
                            self.valid_moves = {(row, col): jump_moves}
                            return True
                    
                    # Switch turns
                    self.switch_turn()
                    return True
                    
        return False
    
    def handle_click(self, pos):
        """
        Handle mouse click events.
        
        Args:
            pos (tuple): (x, y) position of the click
            
        Returns:
            bool: True if a move was made, False otherwise
        """
        if self.game_over:
            return False
            
        x, y = pos
        row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
        
        # If it's a human player's turn
        if isinstance(self.players[self.current_color], Player):
            # Print debug info
            piece = self.board.get_piece(row, col)
            if piece:
                print(f"Clicked on {piece.color} piece at ({row}, {col})")
                if piece.color == self.current_color:
                    has_moves = False
                    for from_pos, moves in self.valid_moves.items():
                        if from_pos == (row, col):
                            has_moves = True
                            print(f"  Valid moves: {list(moves.keys())}")
                            break
                    if not has_moves:
                        print(f"  No valid moves for this piece")
                else:
                    print(f"  Not your turn (current turn: {self.current_color})")
            
            return self.select(row, col)
        
        return False
    
    def play(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            clock.tick(60)  # 60 FPS
            
            # Check for game over
            if self.board.get_winner():
                self.game_over = True
                self.winner = self.board.get_winner()
                
            # Get valid moves for current player
            if not self.waiting_for_player:
                self.valid_moves = self.board.get_all_valid_moves(self.current_color)
                
                # Print current turn and valid moves
                print(f"\n{self.current_color.capitalize()}'s turn")
                if self.valid_moves:
                    print(f"Valid moves: {[(pos, list(moves.keys())) for pos, moves in self.valid_moves.items()]}")
                else:
                    print("No valid moves available")
                
                # Check if the game is over
                if not self.valid_moves:
                    self.game_over = True
                    self.winner = 'black' if self.current_color == 'red' else 'red'
                    print(f"Game over! {self.winner.capitalize()} wins!")
                
                # If it's computer's turn
                if isinstance(self.players[self.current_color], ComputerPlayer) and not self.game_over:
                    self.waiting_for_player = True
                    # Get the computer's move
                    move = self.players[self.current_color].get_move(self.board, self.valid_moves)
                    
                    if move:
                        from_pos, to_pos = move
                        # Make the move
                        from_row, from_col = from_pos
                        to_row, to_col = to_pos
                        
                        print(f"Computer moves from ({from_row}, {from_col}) to ({to_row}, {to_col})")
                        
                        # Select and move the piece
                        self.select(from_row, from_col)
                        self.select(to_row, to_col)
                    
                    self.waiting_for_player = False
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if not self.waiting_for_player and isinstance(self.players[self.current_color], Player):
                        pos = pygame.mouse.get_pos()
                        self.handle_click(pos)
            
            # Draw everything
            self.update()
            
            # Display winner if game is over
            if self.game_over and self.winner:
                font = pygame.font.SysFont('comicsans', 80)
                text = font.render(f"{self.winner.capitalize()} Wins!", 1, BLUE)
                self.win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(2000)  # Show winner for 2 seconds
                running = False
                
        pygame.quit()


def main():
    """Main function to run the game."""
    # Create the game window
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers')
    
    # Show game mode selection screen
    win.fill(WHITE)
    font = pygame.font.SysFont('comicsans', 60)
    title = font.render('Checkers', 1, BLACK)
    win.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    font = pygame.font.SysFont('comicsans', 40)
    one_player = font.render('1. One Player vs Computer', 1, BLACK)
    two_player = font.render('2. Two Players', 1, BLACK)
    win.blit(one_player, (WIDTH//2 - one_player.get_width()//2, 300))
    win.blit(two_player, (WIDTH//2 - two_player.get_width()//2, 350))
    
    pygame.display.update()
    
    # Wait for user selection
    mode = None
    difficulty = 'medium'
    
    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 'one_player'
                    # Show difficulty selection
                    win.fill(WHITE)
                    title = font.render('Select Difficulty', 1, BLACK)
                    win.blit(title, (WIDTH//2 - title.get_width()//2, 100))
                    
                    easy = font.render('1. Easy', 1, BLACK)
                    medium = font.render('2. Medium', 1, BLACK)
                    hard = font.render('3. Hard', 1, BLACK)
                    
                    win.blit(easy, (WIDTH//2 - easy.get_width()//2, 300))
                    win.blit(medium, (WIDTH//2 - medium.get_width()//2, 350))
                    win.blit(hard, (WIDTH//2 - hard.get_width()//2, 400))
                    
                    pygame.display.update()
                    
                    # Wait for difficulty selection
                    difficulty_selected = False
                    while not difficulty_selected:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                                
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_1:
                                    difficulty = 'easy'
                                    difficulty_selected = True
                                elif event.key == pygame.K_2:
                                    difficulty = 'medium'
                                    difficulty_selected = True
                                elif event.key == pygame.K_3:
                                    difficulty = 'hard'
                                    difficulty_selected = True
                    
                elif event.key == pygame.K_2:
                    mode = 'two_player'
    
    # Start the game
    game = Game(win, mode=mode, difficulty=difficulty)
    game.play()


if __name__ == "__main__":
    main()
