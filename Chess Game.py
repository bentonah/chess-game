import pygame
from pygame.locals import *
import pickle

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BOARD_SIZE = 8
SQUARE_SIZE = SCREEN_WIDTH // BOARD_SIZE

pygame.init()

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.selected_piece = None

    def run(self):
        while True:
            self.handle_events()
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.save_game()  # Save the game before quitting
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN:
                self.on_mouse_press(*pygame.mouse.get_pos(), event.button, event.mod)

            if event.type == KEYDOWN:
                if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                    self.save_game()  # Save the game when Ctrl + S is pressed

                if event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
                    self.load_game()  # Load the game when Ctrl + L is pressed

    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = (200, 200, 200) if (row + col) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.draw(self.screen, col * SQUARE_SIZE, row * SQUARE_SIZE)

    def on_mouse_press(self, x, y, button, modifiers):
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE

        if self.selected_piece is None:
            self.selected_piece = (row, col)
        else:
            if self.is_valid_move(self.selected_piece, (row, col)):
                self.move_piece(self.selected_piece, (row, col))
            self.selected_piece = None

    def is_valid_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]

        if piece:
            return piece.is_valid_move(start, end, self.board)

        return False

    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]

        if piece:
            if piece.is_valid_move(start, end, self.board):
                self.board[end_row][end_col] = piece
                self.board[start_row][start_col] = None

    def is_check(self, color):
        king_position = None

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_position = (row, col)
                    break

        if king_position:
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    piece = self.board[row][col]
                    if piece and piece.color != color and piece.is_valid_move((row, col), king_position, self.board):
                        return True

        return False

    def is_checkmate(self, color):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for i in range(BOARD_SIZE):
                        for j in range(BOARD_SIZE):
                            if piece.is_valid_move((row, col), (i, j), self.board):
                                temp_board = [row[:] for row in self.board]
                                temp_board[i][j] = temp_board[row][col]
                                temp_board[row][col] = None

                                if not self.is_check(color):
                                    return False

        return True

    def save_game(self):
        with open("chess_save.pickle", "wb") as file:
            pickle.dump(self.board, file)
            print("Game saved!")

    def load_game(self):
        try:
            with open("chess_save.pickle", "rb") as file:
                self.board = pickle.load(file)
                print("Game loaded!")
        except FileNotFoundError:
            print("No saved game found.")

class ChessPiece:
    def __init__(self, filename, scale, color, symbol):
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (int(scale * SQUARE_SIZE), int(scale * SQUARE_SIZE)))
        self.rect = self.image.get_rect()
        self.color = color
        self.symbol = symbol

    def is_valid_move(self, start, end, board):
        raise NotImplementedError("Subclasses must implement this method")

    def draw(self, screen, x, y):
        screen.blit(self.image, (x, y))


class Pawn(ChessPiece):
    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end
        direction = 1 if self.color == "white" else -1

        # Regular move
        if start_col == end_col and start_row + direction == end_row and board[end_row][end_col] is None:
            return True

        # Initial double move
        if (
            start_col == end_col
            and start_row + 2 * direction == end_row
            and start_row == 1 if self.color == "white" else 6
            and board[end_row][end_col] is None
        ):
            return True

        # Capture move
        if abs(start_col - end_col) == 1 and start_row + direction == end_row:
            if board[end_row][end_col] and board[end_row][end_col].color != self.color:
                return True

        return False


class Rook(ChessPiece):
    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        # Horizontal move
        if start_row == end_row and self.is_clear_horizontal_path(start, end, board):
            return True

        # Vertical move
        if start_col == end_col and self.is_clear_vertical_path(start, end, board):
            return True

        return False

    def is_clear_horizontal_path(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        step = 1 if end_col > start_col else -1

        for col in range(start_col + step, end_col, step):
            if board[start_row][col]:
                return False

        return True

    def is_clear_vertical_path(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        step = 1 if end_row > start_row else -1

        for row in range(start_row + step, end_row, step):
            if board[row][start_col]:
                return False

        return True


class Knight(ChessPiece):
    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        # Knight Move
        if (
            (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1)
            or (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2)
        ) and (board[end_row][end_col] is None or board[end_row][end_col].color != self.color):
            return True

        return False


class Bishop(ChessPiece):
    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        # Diagonal Move
        if abs(start_row - end_row) == abs(start_col - end_col):
            if self.is_clear_diagonal_path(start, end, board):
                return True

        return False

    def is_clear_diagonal_path(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if board[row][col]:
                return False
            row += row_step
            col += col_step

        return True


class Queen(ChessPiece):
    def __init__(self, filename, scale, color, symbol):
        super().__init__(filename, scale, color, symbol)

    def is_valid_move(self, start, end, board):
        if Rook(self.filename, self.scale, self.color, self.symbol).is_valid_move(start, end, board) or \
           Bishop(self.filename, self.scale, self.color, self.symbol).is_valid_move(start, end, board):
            return True
        return False


class King(ChessPiece):
    def is_valid_move(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        # Single move in any direction
        if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
            return True

        return False


def initialize_board(game):
    # Pawns
    for col in range(BOARD_SIZE):
        game.board[1][col] = Pawn("pawn_white.png", 0.5, "white", "P")
        game.board[6][col] = Pawn("pawn_black.png", 0.5, "black", "p")

    # Rooks
    game.board[0][0] = Rook("rook_white.png", 0.5, "white", "R")
    game.board[0][7] = Rook("rook_white.png", 0.5, "white", "R")
    game.board[7][0] = Rook("rook_black.png", 0.5, "black", "r")
    game.board[7][7] = Rook("rook_black.png", 0.5, "black", "r")

    # Knights
    game.board[0][1] = Knight("knight_white.png", 0.5, "white", "N")
    game.board[0][6] = Knight("knight_white.png", 0.5, "white", "N")
    game.board[7][1] = Knight("knight_black.png", 0.5, "black", "n")
    game.board[7][6] = Knight("knight_black.png", 0.5, "black", "n")

    # Bishops
    game.board[0][2] = Bishop("bishop_white.png", 0.5, "white", "B")
    game.board[0][5] = Bishop("bishop_white.png", 0.5, "white", "B")
    game.board[7][2] = Bishop("bishop_black.png", 0.5, "black", "b")
    game.board[7][5] = Bishop("bishop_black.png", 0.5, "black", "b")

    # Queens
    game.board[0][3] = Queen("queen_white.png", 0.5, "white", "Q")
    game.board[7][3] = Queen("queen_black.png", 0.5, "black", "q")

    # Kings
    game.board[0][4] = King("king_white.png", 0.5, "white", "K")
    game.board[7][4] = King("king_black.png", 0.5, "black", "k")


def main():
    game = ChessGame()
    initialize_board(game)
    game.run()


if __name__ == "__main__":
    main()