import pygame
from hex import Hex
from board import Board
from utils import format_piece

# Constants
BOARD_SIZE = 5  # Board size
HEX_SIDE = 40  # Size of side of hexagon
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
COLORS = [LIGHT_WOOD, MEDIUM_WOOD, DARK_WOOD]

def hex_to_pixel(hex):
    """Convert hex coordinates to pixel coordinates."""
    x = HEX_SIDE * (hex.q * 3/2)
    y = HEX_HEIGHT * (hex.r - hex.s) / 2
    return (x + BOARD_OFFSET_X, y + BOARD_OFFSET_Y)

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
    font = pygame.font.SysFont(None, 18)
    coord_text = font.render(f"q{hex.q}|r{hex.r}|s{hex.s}", True, WHITE)
    coord_rect = coord_text.get_rect(center=(x, y))
    surface.blit(coord_text, coord_rect)

def draw_board(surface, board):
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
                    piece_text = format_piece(piece_str, use_unicode=True, use_colors=False)
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(piece_text, True, BLACK)
                    text_rect = text.get_rect(center=hex_to_pixel(hex))
                    surface.blit(text, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gliński's Hexagonal Chess")
    clock = pygame.time.Clock()
    board = Board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        draw_board(screen, board)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
