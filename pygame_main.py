import pygame
from math import sqrt
from copy import deepcopy
from hex import Hex
from board import Board
from utils import format_piece, load_piece_images

# Constants
BOARD_SIZE = 5  # Board size
HEX_SIDE = 60  # Size of side of hexagon
HEX_DIAGONAL = HEX_SIDE * 2
HEX_APOTHEM = HEX_SIDE * (3 ** 0.5) / 2
HEX_HEIGHT = (3 ** 0.5) * HEX_SIDE  # Twice the apothem of the hexagon

BOARD_BORDER = 10  # Border around the board
BOARD_PADDING = 10  # Padding between board and window edge
WINDOW_WIDTH = ((BOARD_SIZE+1)*2+1) * HEX_SIDE * 1.5 + BOARD_PADDING * 2 + BOARD_BORDER * 2
WINDOW_HEIGHT = ((BOARD_SIZE+1)*2+1) * HEX_HEIGHT + BOARD_PADDING * 2 + BOARD_BORDER * 2
BOARD_OFFSET_X = WINDOW_WIDTH // 2  # Center the board horizontally
BOARD_OFFSET_Y = WINDOW_HEIGHT // 2  # Center the board vertically

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_WOOD = (222, 184, 135)  # Light wood color
MEDIUM_WOOD = (160, 82, 45)   # Medium wood color
DARK_WOOD = (101, 67, 33)     # Dark wood color
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlighting moves
COLORS = [LIGHT_WOOD, MEDIUM_WOOD, DARK_WOOD]

def hex_to_pixel(hex):
    """Convert hex coordinates to pixel coordinates."""
    x = HEX_SIDE * (hex.q * 3/2)
    y = HEX_HEIGHT * (hex.r - hex.s) / 2
    return (x + BOARD_OFFSET_X, y + BOARD_OFFSET_Y)

def pixel_to_hex(x, y):
    """Convert pixel coordinates to hex coordinates."""
    x -= BOARD_OFFSET_X
    y -= BOARD_OFFSET_Y
    q = (2/3 * x) / HEX_SIDE
    r = (-x / 3 + (3 ** 0.5) / 3 * y) / HEX_SIDE
    s = -q - r

    # Round q, r, s to the nearest integers
    rounded_q = round(q)
    rounded_r = round(r)
    rounded_s = round(s)

    # Calculate the differences between the rounded values and the original values
    q_diff = abs(rounded_q - q)
    r_diff = abs(rounded_r - r)
    s_diff = abs(rounded_s - s)

    # Adjust the rounded value with the largest difference to ensure rq + rr + rs == 0
    if q_diff > r_diff and q_diff > s_diff:
        rounded_q = -rounded_r - rounded_s
    elif r_diff > s_diff:
        rounded_r = -rounded_q - rounded_s
    else:
        rounded_s = -rounded_q - rounded_r

    return Hex(rounded_q, rounded_r, rounded_s)

def draw_hex(surface, color, hex):
    """Draw a hexagon at the given hex coordinates."""
    x, y = hex_to_pixel(hex)
    points = [
        (x + HEX_SIDE / 1, y),
        (x + HEX_SIDE / 2, y + HEX_APOTHEM),
        (x - HEX_SIDE / 2, y + HEX_APOTHEM),
        (x - HEX_SIDE / 1, y),
        (x - HEX_SIDE / 2, y - HEX_APOTHEM),
        (x + HEX_SIDE / 2, y - HEX_APOTHEM),
    ]
    pygame.draw.polygon(surface, color, points, 0)
    pygame.draw.polygon(surface, BLACK, points, 1)  # Thin black line around hexagon

    # Draw coordinates on the hex
    font = pygame.font.SysFont(None, 22)
    coord_text = font.render(f"q{hex.q} r{hex.r} s{hex.s}", True, WHITE)
    coord_rect = coord_text.get_rect(center=(x, y))
    surface.blit(coord_text, coord_rect)

def draw_board(surface, board, piece_images, selected_hex=None, possible_moves=None):
    """Draw the entire board."""
    for r in range(-board.BOARD_RADIUS, board.BOARD_RADIUS + 1):
        for q in range(-board.BOARD_RADIUS, board.BOARD_RADIUS + 1):
            s = -q - r
            hex = Hex(q, r, s)
            if board.is_valid_hex(hex):
                color_index = (q + 2 * r) % 3
                color = COLORS[color_index]
                draw_hex(surface, color, hex)
                piece = board.get_piece(hex)
                if piece:
                    piece_str = str(piece)
                    piece_image = piece_images[piece_str]
                    piece_rect = piece_image.get_rect(center=hex_to_pixel(hex))
                    surface.blit(piece_image, piece_rect)

    # Highlight selected hex
    if selected_hex:
        x, y = hex_to_pixel(selected_hex)
        points = [
            (x + HEX_SIDE / 1, y),
            (x + HEX_SIDE / 2, y + HEX_APOTHEM),
            (x - HEX_SIDE / 2, y + HEX_APOTHEM),
            (x - HEX_SIDE / 1, y),
            (x - HEX_SIDE / 2, y - HEX_APOTHEM),
            (x + HEX_SIDE / 2, y - HEX_APOTHEM),
        ]
        pygame.draw.polygon(surface, BLACK, points, 3)  # Highlight with thicker black line

    # Highlight possible moves
    if possible_moves:
        for move in possible_moves:
            x, y = hex_to_pixel(move)
            points = [
                (x + HEX_SIDE / 1, y),
                (x + HEX_SIDE / 2, y + HEX_APOTHEM),
                (x - HEX_SIDE / 2, y + HEX_APOTHEM),
                (x - HEX_SIDE / 1, y),
                (x - HEX_SIDE / 2, y - HEX_APOTHEM),
                (x + HEX_SIDE / 2, y - HEX_APOTHEM),
            ]
            pygame.draw.polygon(surface, HIGHLIGHT_COLOR, points, 3)  # Highlight with yellow border

def draw_score(surface, board):
    """Draw the position score on the screen."""
    font = pygame.font.SysFont(None, 36)
    score = board.evaluate_position()
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
    surface.blit(score_text, score_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gliński's Hexagonal Chess")
    clock = pygame.time.Clock()
    board = Board()

    # Load piece images
    piece_images = load_piece_images("images")

    selected_hex = None
    possible_moves = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_hex = pixel_to_hex(*mouse_pos)  # Unpack mouse_pos tuple
                if board.is_valid_hex(clicked_hex):
                    if selected_hex is None:
                        if board.is_occupied(clicked_hex) and board.get_piece(clicked_hex).color == board.current_player:
                            selected_hex = clicked_hex
                            possible_moves = board.get_possible_moves(selected_hex)
                    elif clicked_hex != selected_hex:
                        try:
                            if clicked_hex in possible_moves:
                                temp_board = deepcopy(board)
                                temp_board.move_piece(selected_hex, clicked_hex)
                                if not temp_board.is_check(board.current_player):
                                    board.move_piece(selected_hex, clicked_hex)
                                    if board.is_checkmate(board.current_player):
                                        winner = "black" if board.current_player == "white" else "white"
                                        print(board.display())  # Display the final board
                                        print(f"Checkmate! {winner} wins!")
                                        running = False
                                    if board.is_check(board.current_player):
                                        print("Check!")
                                    selected_hex = None
                                    possible_moves = None
                                else:
                                    print("You cannot put yourself in check")
                                    selected_hex = None
                                    possible_moves = None
                            else:
                                print("Invalid move")
                                selected_hex = None
                                possible_moves = None
                        except ValueError as e:
                            print(f"Invalid move: {e}")
                            selected_hex = None
                            possible_moves = None
                    else:
                        selected_hex = None
                        possible_moves = None
                else:
                    selected_hex = None
                    possible_moves = None

        screen.fill(WHITE)
        draw_board(screen, board, piece_images, selected_hex, possible_moves)
        draw_score(screen, board)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()