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
        self.board = np.zeros((8, 8), dtype=int)
        self.initialize_board()
        self.selected_piece = None
        self.valid_moves = {}

    def initialize_board(self):
        starting_row = [4, 2, 3, 5, 6, 3, 2, 4]
        for col, piece in enumerate(starting_row):
            self.board[0][col] = piece  # White pieces
            self.board[1][col] = 1  # White pawns

            self.board[7][col] = -piece  # Black pieces
            self.board[6][col] = -1  # Black pawns

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
                piece = self.board[row][col]
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
            piece = self.board[row][col]
            if piece != 0:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)

    def move_piece(self, row, col):
        if (row, col) in self.valid_moves:
            self.board[row][col] = self.board[self.selected_piece[0]][self.selected_piece[1]]
            self.board[self.selected_piece[0]][self.selected_piece[1]] = 0
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
