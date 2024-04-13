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
        self.board = np.zeros(64, dtype=int)  # 1D array representing the chessboard
        self.selected_piece = None
        self.valid_moves = {}

    def initialize_board_from_fen(self, fen):
        rank_mapping = {'r': -4, 'n': -2, 'b': -3, 'q': -5, 'k': -6,
                        'p': -1, 'R': 4, 'N': 2, 'B': 3, 'Q': 5, 'K': 6, 'P': 1}
        fen_parts = fen.split()
        fen_board = fen_parts[0]
        fen_board = fen_board.replace('/', '')  # Remove slashes denoting row separation
        fen_board_index = 0
        i = 0
        while i < len(self.board) and fen_board_index < len(fen_board):
            if fen_board[fen_board_index].isdigit():  # Empty squares
                i += int(fen_board[fen_board_index])
                fen_board_index += 1
            else:
                self.board[i] = rank_mapping[fen_board[fen_board_index]]
                i += 1
                fen_board_index += 1

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

    def get_valid_moves(self, row, col):
        return {(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)}  # Example: All adjacent squares

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    chessboard = Chessboard()
    chessboard.initialize_board_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    row, col = chessboard.get_square(x, y)
                    chessboard.select_piece(row, col)

        chessboard.draw_board(win)
        chessboard.draw_pieces(win)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
