import pygame
from math import sqrt
from copy import deepcopy
from hex import Hex
from board import Board
from utils import format_piece, load_piece_images
import string

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

# Add to Constants section
MOVES_LIST_WIDTH = 400  # Width of the moves list panel (doubled)
NEW_WINDOW_WIDTH = WINDOW_WIDTH + MOVES_LIST_WIDTH  # Remove space for score bar
MOVES_LINE_HEIGHT = 24  # Height of each line in the moves list

# Tile labels
q_labels = {q: letter for q, letter in zip(range(-5, 6), string.ascii_uppercase[:11])}
r_labels = {r: str(r + 6) for r in range(-5, 6)}

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
    # Adjust x coordinate to account for moves list panel and score bar
    x -= (MOVES_LIST_WIDTH)
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
    coord_text = font.render(f"{q_labels[hex.q]}{r_labels[hex.r]}", True, WHITE)
    coord_rect = coord_text.get_rect(center=(x, y))
    surface.blit(coord_text, coord_rect)

# Column label positions
column_label_positions = {
    "A": Hex(-5, 5, 0),
    "B": Hex(-4, 5, -1),
    "C": Hex(-3, 5, -2),
    "D": Hex(-2, 5, -3),
    "E": Hex(-1, 5, -4),
    "F": Hex(0, 5, -5),
    "G": Hex(1, 4, -5),
    "H": Hex(2, 3, -5),
    "I": Hex(3, 2, -5),
    "J": Hex(4, 1, -5),
    "K": Hex(5, 0, -5),
}

# Row label positions
row_label_positions = {
    "11": Hex(-6, 5, 1),
    "10": Hex(-6, 4, 2),
    "9": Hex(-6, 3, 3),
    "8": Hex(-6, 2, 4),
    "7": Hex(-6, 1, 5),
    "6": Hex(-6, 0, 6),
    "5": Hex(-5, -1, 6),
    "4": Hex(-4, -2, 6),
    "3": Hex(-3, -3, 6),
    "2": Hex(-2, -4, 6),
    "1": Hex(-1, -5, 6),
}

def draw_board(surface, board, piece_images, selected_hex=None, possible_moves=None):
    """Draw the entire board."""
    # Draw moves list first
    draw_move_history(surface, board)
    
    # Offset all board drawing by MOVES_LIST_WIDTH
    old_BOARD_OFFSET_X = BOARD_OFFSET_X
    globals()['BOARD_OFFSET_X'] = BOARD_OFFSET_X + MOVES_LIST_WIDTH

    # Draw the board
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

    font = pygame.font.SysFont(None, 24)

    # Draw row labels
    for label, hex in row_label_positions.items():
        label_text = font.render(label, True, BLACK)
        x, y = hex_to_pixel(hex)
        surface.blit(label_text, (x + HEX_SIDE // 2, y))
    # for r in range(-board.BOARD_RADIUS, board.BOARD_RADIUS + 1):
    #     label = font.render(r_labels[r], True, BLACK)
    #     x, y = hex_to_pixel(Hex(-board.BOARD_RADIUS, r, board.BOARD_RADIUS - r))
    #     surface.blit(label, (x - HEX_SIDE - 20, y - HEX_HEIGHT // 2))

    # Draw column labels
    for label, hex in column_label_positions.items():
        label_text = font.render(label, True, BLACK)
        x, y = hex_to_pixel(hex)
        surface.blit(label_text, (x, y + HEX_HEIGHT // 2 + 10))

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

    # Restore original offset
    globals()['BOARD_OFFSET_X'] = old_BOARD_OFFSET_X

def draw_move_history(surface, board):
    """Draw the move history in three columns on the left side of the screen."""
    font = pygame.font.SysFont(None, 24)
    moves = board.moves_history
    
    # Draw moves list background
    pygame.draw.rect(surface, WHITE, (0, 0, MOVES_LIST_WIDTH, WINDOW_HEIGHT))
    pygame.draw.line(surface, BLACK, (MOVES_LIST_WIDTH, 0), (MOVES_LIST_WIDTH, WINDOW_HEIGHT), 2)
    
    # Get scores for both players and round to 2 decimal places
    white_score = round(board.evaluate_position_for("white"), 2)
    black_score = round(board.evaluate_position_for("black"), 2)
    
    # Draw column headers with scores
    white_header = font.render(f"White ({white_score:.2f})", True, BLACK)
    black_header = font.render(f"Black ({black_score:.2f})", True, BLACK)
    surface.blit(white_header, (10, 10))
    surface.blit(black_header, (MOVES_LIST_WIDTH // 2 + 10, 10))
    
    # Draw moves in three columns
    for i in range(0, len(moves), 2):
        move_num = (i // 2) + 1
        white_move = moves[i]
        black_move = moves[i + 1] if i + 1 < len(moves) else None
        
        move_num_text = font.render(f"{move_num}.", True, BLACK)
        white_move_text = font.render(f"{white_move[0]}<{white_move[1].q} {white_move[1].r} {white_move[1].s}>", True, BLACK)
        black_move_text = font.render(f"{black_move[0]}<{black_move[1].q} {black_move[1].r} {black_move[1].s}>" if black_move else "", True, BLACK)
        
        surface.blit(move_num_text, (10, 40 + (i // 2) * MOVES_LINE_HEIGHT))
        surface.blit(white_move_text, (50, 40 + (i // 2) * MOVES_LINE_HEIGHT))
        surface.blit(black_move_text, (MOVES_LIST_WIDTH // 2 + 50, 40 + (i // 2) * MOVES_LINE_HEIGHT))

def handle_mouse_button_down(board, mouse_pos, selected_hex, possible_moves):
    """Handle mouse button down events."""
    clicked_hex = pixel_to_hex(*mouse_pos)  # Unpack mouse_pos tuple
    if not board.is_valid_hex(clicked_hex):
        return None, None

    if selected_hex is None:
        if board.is_occupied(clicked_hex) and board.get_piece(clicked_hex).color == board.current_player:
            return clicked_hex, board.get_possible_moves(clicked_hex)
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
                        return None, None
                    if board.is_check(board.current_player):
                        print("Check!")
                    return None, None
                else:
                    print("You cannot put yourself in check")
                    return None, None
            else:
                print("Invalid move")
                return None, None
        except ValueError as e:
            print(f"Invalid move: {e}")
            return None, None
    return None, None

def main():
    pygame.init()
    screen = pygame.display.set_mode((NEW_WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gliński's Hexagonal Chess")
    clock = pygame.time.Clock()
    board = Board()

    # Load piece images
    piece_images = load_piece_images("images")

    selected_hex = None
    possible_moves = None
    running = True
    redraw = True  # Flag to indicate if the screen needs to be redrawn
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                new_selected_hex, new_possible_moves = handle_mouse_button_down(board, pygame.mouse.get_pos(), selected_hex, possible_moves)
                if new_selected_hex != selected_hex or new_possible_moves != possible_moves:
                    selected_hex, possible_moves = new_selected_hex, new_possible_moves
                    redraw = True  # Set redraw flag when there is a mouse event

        if redraw:
            screen.fill(WHITE)
            draw_board(screen, board, piece_images, selected_hex, possible_moves)
            pygame.display.flip()
            redraw = False  # Reset redraw flag after drawing

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()