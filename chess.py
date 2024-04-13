import pygame
import numpy as np

WIDTH, HEIGHT = 800, 800
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

    def draw_board(self, win):
        win.fill(WHITE)
        for row in range(8):
            for col in range(row % 2, 8, 2):
                pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

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

    def get_square(self, x, y):
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return row, col

    def select_piece(self, row, col):
        if self.selected_piece:
            self.move_piece(row, col)
        else:
            piece = self.board[row * 8 + col]
            if piece != 0:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)

    def move_piece(self, row, col):
        if (row, col) in self.valid_moves:
            self.board[row * 8 + col] = self.board[self.selected_piece[0] * 8 + self.selected_piece[1]]
            self.board[self.selected_piece[0] * 8 + self.selected_piece[1]] = 0
            self.selected_piece = None
            self.valid_moves = {}

            # Check for en passant capture
            if self.en_passant_target and (row, col) == self.en_passant_target:
                if self.board[self.selected_piece[0] * 8 + col] == 0:  # Capture the pawn
                    self.board[(row - 1) * 8 + col] = 0
                elif self.board[self.selected_piece[0] * 8 + col] == 0:  # Capture the pawn
                    self.board[(row + 1) * 8 + col] = 0

            # Update en passant target square after move
            self.en_passant_target = None

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
            king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for move in king_moves:
                new_row, new_col = row + move[0], col + move[1]
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = self.board[new_row * 8 + new_col]
                    if target_piece == 0 or (piece < 0) != (target_piece < 0):
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
    print(chessboard.get_fen())  # Print initial FEN string

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    row, col = chessboard.get_square(x, y)
                    chessboard.select_piece(row, col)

                    print(chessboard.get_fen())  # Print FEN string after each move

        chessboard.draw_board(win)
        chessboard.draw_pieces(win)
        pygame.display.update()
        clock.tick(60)

        chessboard.switch_active_color()

    pygame.quit()


if __name__ == "__main__":
    main()
