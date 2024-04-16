from copy import deepcopy

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


    def is_king_under_attack(self, color):
        # Find the position of the king of the specified color
        king_position = get_king_position(self, color)

        if king_position is None:
            return False  # King not found, shouldn't happen in a valid game

        # Check if any opponent's pieces can attack the king
        opponent_color = 'b' if color == 'w' else 'w'
        for i, piece in enumerate(self.board):
            if (piece < 0 and opponent_color == 'b') or (piece > 0 and opponent_color == 'w'):
                # Piece belongs to the opponent
                valid_moves = self.get_valid_moves(i // 8, i % 8)
                if king_position in valid_moves:
                    return True

        return False
    def perform_castling(self, direction):
        king_row, king_col = get_king_position(self, self.active_color)

        if direction == "k":  # King side castling
            if king_col + 2 > 7:  # Check if the king is not already at the edge of the board
                return  # Invalid castling
            # Check if there are no pieces between the king and the rook
            if any(self.board[king_row * 8 + col] != 0 for col in range(king_col + 1, king_col + 3)):
                return  # Invalid castling
            # Check if the king passes through or finishes on a square attacked by an enemy piece
            if self.is_king_under_attack(self.active_color) or \
                    any(self.is_king_under_attack(self.active_color) for col in range(king_col, king_col + 3)):
                return  # Invalid castling
            # Move the king two squares to the right
            self.board[king_row * 8 + king_col + 2] = self.board[king_row * 8 + king_col]
            self.board[king_row * 8 + king_col] = 0
            # Move the rook to the square next to the king
            self.board[king_row * 8 + king_col + 1] = self.board[king_row * 8 + 7]
            self.board[king_row * 8 + 7] = 0

        elif direction == "q":  # Queen side castling
            if king_col - 2 < 0:  # Check if the king is not already at the edge of the board
                return  # Invalid castling
            # Check if there are no pieces between the king and the rook
            if any(self.board[king_row * 8 + col] != 0 for col in range(king_col - 2, king_col)):
                return  # Invalid castling
            # Check if the king passes through or finishes on a square attacked by an enemy piece
            if self.is_king_under_attack(self.active_color) or \
                    any(self.is_king_under_attack(self.active_color) for col in range(king_col - 2, king_col + 1)):
                return  # Invalid castling
            # Move the king two squares to the left
            self.board[king_row * 8 + king_col - 2] = self.board[king_row * 8 + king_col]
            self.board[king_row * 8 + king_col] = 0
            # Move the rook to the square next to the king
            self.board[king_row * 8 + king_col - 1] = self.board[king_row * 8]
            self.board[king_row * 8] = 0

        # Update any other game state variables as needed


    def pawn_promotion(self, row, col, win):
        self.valid_moves = {}  # Reset valid_moves dictionary
        promotion_options = {
            "queen": (5, -5),
            "knight": (2, -2),
            "bishop": (3, -3),
            "rook": (4, -4)
        }  # Piece name to integer mapping for both white and black
        promotion_index = 0  # Start at the first promotion option

        # Display piece options (queen, knight, bishop, rook)

        run = True
        while run:
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        promotion_index = (promotion_index - 1) % len(promotion_options)
                    elif event.key == pygame.K_RIGHT:
                        promotion_index = (promotion_index + 1) % len(promotion_options)
                    elif event.key == pygame.K_RETURN:
                        promotion_piece = list(promotion_options.values())[promotion_index][0]
                        if self.active_color == 'b':  # If black's turn, choose the negative value for promotion
                            promotion_piece = list(promotion_options.values())[promotion_index][1]
                        self.board[row * 8 + col] = promotion_piece
                        run = False

            # Redraw the board after promotion
            self.draw_board(win)
            self.draw_pieces(win)

            # Redraw the square with the appropriate background color
            if (row + col) % 2 == 0:
                pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Display the selected promotion piece with the proper background color
            selected_piece = list(promotion_options.keys())[promotion_index]
            if self.active_color == 'b':  # If black's turn, load black piece images
                selected_piece_img = pygame.transform.scale(
                    pygame.image.load(f"static/black_{selected_piece}.png"),
                    (SQUARE_SIZE, SQUARE_SIZE))
            else:  # Otherwise, load white piece images
                selected_piece_img = pygame.transform.scale(
                    pygame.image.load(f"static/white_{selected_piece}.png"),
                    (SQUARE_SIZE, SQUARE_SIZE))
            win.blit(selected_piece_img, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            pygame.display.update()

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

        # Draw pieces on the board
        self.draw_pieces(win)

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

    def move_piece(self, row, col, win):
        if self.selected_piece and not self.piece_moved and not self.move_made:
            piece = self.board[self.selected_piece[0] * 8 + self.selected_piece[1]]
            if (row, col) != self.selected_piece:  # Ensure the destination is different from the current location
                if (row, col) in self.valid_moves and \
                        (piece > 0 and self.active_color == 'w' or piece < 0 and self.active_color == 'b'):
                    # Move the piece only if it's the correct player's turn
                    #start_square = chr(self.selected_piece[1] + 97) + str(8 - self.selected_piece[0])
                    #end_square = chr(col + 97) + str(8 - row)
                    #print(f"{start_square} -> {end_square}")  # Print move in chess notation
                    self.board[row * 8 + col] = piece
                    self.board[self.selected_piece[0] * 8 + self.selected_piece[1]] = 0

                    # Check for pawn promotion
                    if piece == 1 and row == 0:  # White pawn reached the top row
                        self.pawn_promotion(row, col, win)  # Pass the 'win' argument here
                    elif piece == -1 and row == 7:  # Black pawn reached the bottom row
                        self.pawn_promotion(row, col, win)  # Pass the 'win' argument here

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
                        if True and True:
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



    def get_piece_symbol(self, value):
        piece_mapping = {-4: 'r', -2: 'n', -3: 'b', -5: 'q', -6: 'k',
                         -1: 'p', 1: "P", 4: 'R', 2: 'N', 3: 'B', 5: 'Q', 6: 'K'}
        return piece_mapping.get(value, ' ')


def get_king_position(chessboard, color):
    for row in range(8):
        for col in range(8):
            piece = chessboard.board[row * 8 + col]
            if color == 'w' and piece == 6:  # White king
                return row, col
            elif color == 'b' and piece == -6:  # Black king
                return row, col
    # If the king is not found, return None
    return None, None


def filter_safe_moves(chessboard, moves):
    safe_moves = set()
    if chessboard.selected_piece is not None:  # Check if a piece is selected
        for move in moves:
            # Create a temporary copy of the current board
            temp_board = chessboard.board.copy()

            # Simulate the move on the temporary board
            original_piece = temp_board[move[0] * 8 + move[1]]
            temp_board[move[0] * 8 + move[1]] = temp_board[
                chessboard.selected_piece[0] * 8 + chessboard.selected_piece[1]]
            temp_board[chessboard.selected_piece[0] * 8 + chessboard.selected_piece[1]] = 0

            # Check if the king is under attack after the move
            if not chessboard.is_king_under_attack(chessboard.active_color):
                safe_moves.add(move)

            # Discard the changes by restoring the original board state
            temp_board[chessboard.selected_piece[0] * 8 + chessboard.selected_piece[1]] = temp_board[
                move[0] * 8 + move[1]]
            temp_board[move[0] * 8 + move[1]] = original_piece

    return safe_moves


def check_for_checkmate(chessboard):
    for active_color in ['w', 'b']:
        if chessboard.is_king_under_attack(active_color):
            valid_moves_to_escape = []
            for row in range(8):
                for col in range(8):
                    piece = chessboard.board[row * 8 + col]

                    if (piece > 0 and active_color == 'w') or (piece < 0 and active_color == 'b'):
                        valid_moves = chessboard.get_valid_moves(row, col)
                        for move in valid_moves:
                            start_square = chr(col + 97) + str(8 - row)
                            end_square = chr(move[1] + 97) + str(8 - move[0])
                            temp_board = chessboard.board.copy()

                            temp_board[move[0] * 8 + move[1]] = temp_board[row * 8 + col]
                            temp_board[row * 8 + col] = 0
                            temp_chessboard = Chessboard()
                            temp_chessboard.board = temp_board
                            temp_chessboard.active_color = active_color
                            if not temp_chessboard.is_king_under_attack(active_color):
                                valid_moves_to_escape.append((start_square, end_square))
            if valid_moves_to_escape:
                #print(f"{active_color.upper()} Check!")
                pass
            else:
                #print(f"{active_color.upper()} Checkmate!")
                pass
                return active_color  # Return the winning player
        else:
            pass

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    chessboard = Chessboard()
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    chessboard.initialize_board_from_fen(starting_fen)
    run = True
    font = pygame.font.SysFont(None, 36)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    x, y = pygame.mouse.get_pos()
                    row, col = chessboard.get_square(x, y)
                    if chessboard.selected_piece is None:
                        if chessboard.board[row * 8 + col] != 0:
                            piece = chessboard.board[row * 8 + col]
                            if (piece > 0 and chessboard.active_color == 'w') or (
                                    piece < 0 and chessboard.active_color == 'b'):
                                chessboard.selected_piece = (row, col)
                                chessboard.valid_moves = chessboard.get_valid_moves(row, col)
                    else:
                        if (row, col) in chessboard.valid_moves:
                            # Create a temporary copy of the chessboard to simulate the move
                            temp_chessboard = deepcopy(chessboard)
                            temp_chessboard.move_piece(row, col, win)
                            # Check if the player's king is still under attack after the move
                            if not temp_chessboard.is_king_under_attack(chessboard.active_color):
                                # Move is valid, update the actual chessboard
                                chessboard.move_piece(row, col, win)
                                if chessboard.piece_moved:
                                    chessboard.selected_piece = None
                                    chessboard.valid_moves = {}
                                    # Check for checkmate after each move
                                    winner = check_for_checkmate(chessboard)
                                    if winner:
                                        print(f"Checkmate! {winner.upper()} Loses!")

                                    else:
                                        chessboard.switch_active_color()  # Switch active color after handling events and drawing the board
                            else:
                                pass
                                # Optionally, you can provide feedback to the player that the move is invalid
                        else:
                            chessboard.selected_piece = None
                            chessboard.valid_moves = {}

        # If the player is in check, filter the valid moves to only allow moves that get out of check
        if chessboard.is_king_under_attack(chessboard.active_color):
            moves_to_remove = set()  # Create a set to store moves to be removed
            for row, col in chessboard.valid_moves:
                # Create a temporary copy of the chessboard to simulate the move
                temp_chessboard = deepcopy(chessboard)
                temp_chessboard.move_piece(row, col, win)
                if temp_chessboard.is_king_under_attack(chessboard.active_color):
                    # If the move still leaves the king under attack, add it to the set of moves to remove
                    moves_to_remove.add((row, col))
            # Remove invalid moves from the set of valid moves
            for move in moves_to_remove:
                chessboard.valid_moves.remove(move)

        chessboard.draw_board(win)
        chessboard.draw_pieces(win)

        if check_for_checkmate(chessboard):
            check_status = f"{check_for_checkmate(chessboard).capitalize()} Checkmate!"
        elif chessboard.is_king_under_attack(chessboard.active_color):
            check_status = f"{chessboard.active_color.capitalize()} Check"
        else:
            check_status = ""
        check_text = font.render(check_status, True, BLACK)
        win.blit(check_text, (20, HEIGHT - 60))

        turn_text = font.render("Turn: White" if chessboard.active_color == 'w' else "Turn: Black", True, BLACK)
        win.blit(turn_text, (20, HEIGHT - 30))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
