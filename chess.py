import pygame
import numpy as np


WIDTH, HEIGHT = 800, 1000
SQUARE_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class Chessboard:
    def __init__(self):
        self.board = np.zeros(64, dtype=int)
        self.active_color = None
        self.castling_rights = None
        self.en_passant_target = None
        self.halfmove_clock = None
        self.fullmove_number = None
        self.selected_piece = None
        self.valid_moves = {}
        self.piece_moved = False  # Flag to track whether a piece has been moved during the current turn
        self.move_made = False  # Flag to track whether a move has been made during the current turn
        self.promotion_square = None  # Track the square where promotion occurs
        self.promotion_piece = None  # Track the piece to promote to


    def initialize_board_from_fen(self, fen):
        fen_parts = fen.split()
        fen_board = fen_parts[0]
        fen_board = fen_board.replace('/', '')
        fen_board_index = 0
        i = 0
        while i < len(self.board) and fen_board_index < len(fen_board):
            if fen_board[fen_board_index].isdigit():
                i += int(fen_board[fen_board_index])
                fen_board_index += 1
            else:
                self.board[i] = self.get_piece_value(fen_board[fen_board_index])
                i += 1
                fen_board_index += 1

        self.active_color = fen_parts[1]
        self.castling_rights = fen_parts[2]
        self.en_passant_target = fen_parts[3]
        self.halfmove_clock = int(fen_parts[4]) if fen_parts[4].isdigit() else None
        self.fullmove_number = int(fen_parts[5]) if len(fen_parts) > 5 and fen_parts[
            5].isdigit() else None

    def get_piece_value(self, symbol):
        piece_mapping = {'r': -4, 'n': -2, 'b': -3, 'q': -5, 'k': -6,
                         'p': -1, 'R': 4, 'N': 2, 'B': 3, 'Q': 5, 'K': 6, 'P': 1}
        return piece_mapping.get(symbol, 0)

    def switch_active_color(self):
        self.active_color = 'b' if self.active_color == 'w' else 'w'
        self.piece_moved = False  # Reset piece_moved flag at the start of each turn
        self.move_made = False  # Reset move_made flag at the start of each turn

    def draw_board(self, win):
        win.fill(WHITE)
        light_green = (144, 238, 144)
        dark_green = (0, 128, 0)
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    if (row, col) in self.valid_moves:
                        # Fill valid move squares with green-grey color
                        pygame.draw.rect(win, dark_green,
                                         (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    if (row, col) in self.valid_moves:
                        # Fill valid move squares with white-green color
                        pygame.draw.rect(win, light_green,
                                         (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, win):
        piece_images = {
            1: pygame.transform.scale(pygame.image.load("static/white_pawn.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            2: pygame.transform.scale(pygame.image.load("static/white_knight.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            3: pygame.transform.scale(pygame.image.load("static/white_bishop.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            4: pygame.transform.scale(pygame.image.load("static/white_rook.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            5: pygame.transform.scale(pygame.image.load("static/white_queen.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            6: pygame.transform.scale(pygame.image.load("static/white_king.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -1: pygame.transform.scale(pygame.image.load("static/black_pawn.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -2: pygame.transform.scale(pygame.image.load("static/black_knight.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -3: pygame.transform.scale(pygame.image.load("static/black_bishop.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -4: pygame.transform.scale(pygame.image.load("static/black_rook.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -5: pygame.transform.scale(pygame.image.load("static/black_queen.png"), (SQUARE_SIZE, SQUARE_SIZE)),
            -6: pygame.transform.scale(pygame.image.load("static/black_king.png"), (SQUARE_SIZE, SQUARE_SIZE))
        }

        for row in range(8):
            for col in range(8):
                piece = self.board[row * 8 + col]
                if piece != 0:
                    win.blit(piece_images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))
                if self.promotion_square:
                    row, col = self.promotion_square
                    pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    def get_square(self, x, y):
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return row, col

    def select_piece(self, row, col):
        if not self.piece_moved and not self.move_made:  # Check if a piece can be selected and moved
            if self.selected_piece:
                if (row, col) != self.selected_piece:  # Ensure the clicked square is different from the selected piece's square
                    self.move_piece(row, col)
            else:
                piece = self.board[row * 8 + col]
                if piece != 0:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.get_valid_moves(row, col)

    def move_piece(self, row, col):
        if self.selected_piece and not self.piece_moved and not self.move_made:
            piece = self.board[self.selected_piece[0] * 8 + self.selected_piece[1]]
            if (row, col) != self.selected_piece:  # Ensure the destination is different from the current location
                if (row, col) in self.valid_moves and \
                        (piece > 0 and self.active_color == 'w' or piece < 0 and self.active_color == 'b'):
                    # Move the piece only if it's the correct player's turn
                    self.board[row * 8 + col] = piece
                    self.board[self.selected_piece[0] * 8 + self.selected_piece[1]] = 0
                    self.selected_piece = None
                    self.valid_moves = {}
                    self.piece_moved = True
                    self.move_made = True  # Set move_made to True after a move

                    # Check for castling
                    if abs(piece) == 6 and self.selected_piece is not None and abs(self.selected_piece[1] - col) == 2:
                        # Castling move, move the rook
                        if col == 6:  # King side castling
                            self.board[row * 8 + 5] = self.board[row * 8 + 7]
                            self.board[row * 8 + 7] = 0
                        elif col == 2:  # Queen side castling
                            self.board[row * 8 + 3] = self.board[row * 8]
                            self.board[row * 8] = 0

                    # Update en passant target square after move
                    self.en_passant_target = None

    def squares_between_empty(self, start_row, start_col, end_col):
        # Check if the squares between start_col and end_col are empty
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if self.board[start_row * 8 + col] != 0:
                return False
        return True

    def squares_not_under_attack(self, row, col):
        # Check if the squares the king moves through and ends up in are not under attack
        # For simplicity, assume all squares are safe for now
        return True

    def get_valid_moves(self, row, col):
        piece = self.board[row * 8 + col]
        valid_moves = set()

        if piece == 1:  # White Pawn
            # Move one square forward
            if row > 0 and self.board[(row - 1) * 8 + col] == 0:
                valid_moves.add((row - 1, col))
                # Move two squares forward from starting position
                if row == 6 and self.board[(row - 2) * 8 + col] == 0:
                    valid_moves.add((row - 2, col))
            # Capture diagonally
            if row > 0 and col > 0 and self.board[(row - 1) * 8 + col - 1] < 0:
                valid_moves.add((row - 1, col - 1))
            if row > 0 and col < 7 and self.board[(row - 1) * 8 + col + 1] < 0:
                valid_moves.add((row - 1, col + 1))
            if row == 3 and self.en_passant_target and col - 1 >= 0 and \
                    (row, col - 1) == self.en_passant_target:
                valid_moves.add((row - 1, col - 1))
            if row == 3 and self.en_passant_target and col + 1 <= 7 and \
                    (row, col + 1) == self.en_passant_target:
                valid_moves.add((row - 1, col + 1))


        elif piece == -1:  # Black Pawn
            # Move one square forward
            if row < 7 and self.board[(row + 1) * 8 + col] == 0:
                valid_moves.add((row + 1, col))
                # Move two squares forward from starting position
                if row == 1 and self.board[(row + 2) * 8 + col] == 0:
                    valid_moves.add((row + 2, col))
            # Capture diagonally
            if row < 7 and col > 0 and self.board[(row + 1) * 8 + col - 1] > 0:
                valid_moves.add((row + 1, col - 1))
            if row < 7 and col < 7 and self.board[(row + 1) * 8 + col + 1] > 0:
                valid_moves.add((row + 1, col + 1))

        elif piece == 2 or piece == -2:  # Knight
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for move in knight_moves:
                new_row, new_col = row + move[0], col + move[1]
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = self.board[new_row * 8 + new_col]
                    if target_piece == 0 or (piece < 0) != (target_piece < 0):
                        valid_moves.add((new_row, new_col))

        elif abs(piece) == 3:  # Bishop
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + direction[0] * i, col + direction[1] * i
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        target_piece = self.board[new_row * 8 + new_col]
                        if target_piece == 0:
                            valid_moves.add((new_row, new_col))
                        elif (piece < 0) != (target_piece < 0):
                            valid_moves.add((new_row, new_col))
                            break
                        else:
                            break
                    else:
                        break

        elif abs(piece) == 4:  # Rook
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + direction[0] * i, col + direction[1] * i
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        target_piece = self.board[new_row * 8 + new_col]
                        if target_piece == 0:
                            valid_moves.add((new_row, new_col))
                        elif (piece < 0) != (target_piece < 0):
                            valid_moves.add((new_row, new_col))
                            break
                        else:
                            break
                    else:
                        break

        elif abs(piece) == 5:  # Queen
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
            for direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + direction[0] * i, col + direction[1] * i
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        target_piece = self.board[new_row * 8 + new_col]
                        if target_piece == 0:
                            valid_moves.add((new_row, new_col))
                        elif (piece < 0) != (target_piece < 0):
                            valid_moves.add((new_row, new_col))
                            break
                        else:
                            break
                    else:
                        break



        elif abs(piece) == 6:  # King
            # King moves
            king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for move in king_moves:
                new_row, new_col = row + move[0], col + move[1]
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = self.board[new_row * 8 + new_col]
                    if target_piece == 0 or (piece < 0) != (target_piece < 0):
                        if self.squares_not_under_attack(row, col) and self.squares_not_under_attack(new_row, new_col):
                            valid_moves.add((new_row, new_col))
        return valid_moves

    def get_fen(self):
        fen_board = ""
        empty_count = 0

        for i in range(64):
            if self.board[i] == 0:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_board += str(empty_count)
                    empty_count = 0
                fen_board += self.get_piece_symbol(self.board[i])

            if (i + 1) % 8 == 0:
                if empty_count > 0:
                    fen_board += str(empty_count)
                    empty_count = 0  # Reset empty count after each row
                if i != 63:
                    fen_board += "/"

        return fen_board

        fen = fen_board + " " + self.active_color + " " + self.castling_rights + " " + self.en_passant_target + " "
        fen += str(self.halfmove_clock) + " " + str(self.fullmove_number)
        return fen

    def get_piece_symbol(self, value):
        piece_mapping = {-4: 'r', -2: 'n', -3: 'b', -5: 'q', -6: 'k',
                         -1: 'p', 1: "P", 4: 'R', 2: 'N', 3: 'B', 5: 'Q', 6: 'K'}
        return piece_mapping.get(value, ' ')


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    chessboard = Chessboard()

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    chessboard.initialize_board_from_fen(starting_fen)
    run = True
    font = pygame.font.SysFont(None, 36)  # Use SysFont instead of None
    print(chessboard.get_fen())  # Print initial FEN string

    # Inside the main loop where event handling occurs
    double_click_time = 0  # Variable to store the time of the last click
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    if pygame.mouse.get_pressed()[0]:
                        x, y = pygame.mouse.get_pos()
                        row, col = chessboard.get_square(x, y)
                        if chessboard.selected_piece is None:
                            # If no piece is selected, select the piece at the clicked square
                            if chessboard.board[row * 8 + col] != 0:
                                # Check if it's the current player's turn
                                piece = chessboard.board[row * 8 + col]
                                if (piece > 0 and chessboard.active_color == 'w') or (
                                        piece < 0 and chessboard.active_color == 'b'):
                                    chessboard.selected_piece = (row, col)
                                    chessboard.valid_moves = chessboard.get_valid_moves(row, col)
                        else:
                            # If a piece is already selected, try to move it to the clicked square
                            if (row,
                                col) != chessboard.selected_piece:  # Ensure the destination is different from the current location
                                chessboard.move_piece(row, col)
                                if chessboard.piece_moved:  # Check if a piece has been successfully moved
                                    chessboard.selected_piece = None
                                    chessboard.valid_moves = {}
                                    print(chessboard.get_fen())  # Print FEN string after each move

                                    # Switch active color after handling events and drawing the board
                                    chessboard.switch_active_color()  # Move this line inside the event handling block

        # Draw the board and pieces
        chessboard.draw_board(win)
        chessboard.draw_pieces(win)

        # Render text areas
        turn_text = font.render("Turn: White" if chessboard.active_color == 'w' else "Turn: Black", True, BLACK)
        win.blit(turn_text, (20, HEIGHT - 30))  # Position the text below the game board

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
