# -*- coding: utf-8 -*-
# pygame_main.py

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
RAISE3D = 0.9  # Factor to raise the 3D effect

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

class GameState:
    """Encapsulates the core game state."""
    def __init__(self):
        self.board = Board()
        self.selected_hex = None
        self.possible_moves = None

def hex_to_pixel(hex):
    """Convert hex coordinates to pixel coordinates."""
    x = HEX_SIDE * (hex.q * 3/2)
    y = HEX_HEIGHT * (hex.r - hex.s) / 2
    return (x + BOARD_OFFSET_X, y + BOARD_OFFSET_Y)

def pixel_to_hex(x, y):
    """Convert pixel coordinates to hex coordinates."""
    # Adjust x coordinate to account for moves list panel and score bar
    x -= MOVES_LIST_WIDTH
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

    # Adjust the rounded value with the largest difference to ensure q + r + s == 0
    if q_diff > r_diff and q_diff > s_diff:
        rounded_q = -rounded_r - rounded_s
    elif r_diff > s_diff:
        rounded_r = -rounded_q - rounded_s
    else:
        rounded_s = -rounded_q - rounded_r

    return Hex(rounded_q, rounded_r, rounded_s)

def draw_hexagon(surface, color, hex, border_color=BLACK, border_width=1, text=None, text_color=WHITE, fill=True, highlight=False):
    """Draw a hexagon at the given hex coordinates with optional text."""
    x, y = hex_to_pixel(hex)
    points = [
        (x + HEX_SIDE / 1, y),
        (x + HEX_SIDE / 2, y + HEX_APOTHEM),
        (x - HEX_SIDE / 2, y + HEX_APOTHEM),
        (x - HEX_SIDE / 1, y),
        (x - HEX_SIDE / 2, y - HEX_APOTHEM),
        (x + HEX_SIDE / 2, y - HEX_APOTHEM),
    ]
    
    if color is not None:
        # Define colors for highlights and shadows
        highlight_color = (255, 255, 255)  # Light color for highlights
        shadow_color = (0, 0, 0)  # Dark color for shadows

        # Calculate gradient for highlights and shadows
        # 3D effect is achieved by changing the color of each side based on the light source
        # The light source is assumed to be coming from NE direction
        # The brightest color is 3 parts of the original color plus 2 parts of the highlight color
        # The darkest color is 2 parts of the original color plus 3 parts of the shadow color
        side_colors = [
            tuple(int(4 * color[i] + 1 * highlight_color[i]) // 5 for i in range(3)),  # Bottom-right (highlight)
            tuple(int(3 * color[i] + 2 * shadow_color[i]) // 5 for i in range(3)),  # Bottom (shadow)
            tuple(int(2 * color[i] + 3 * shadow_color[i]) // 5 for i in range(3)),  # Bottom-left (deep shadow)
            tuple(int(3 * color[i] + 2 * shadow_color[i]) // 5 for i in range(3)),  # Top-left (shadow)
            tuple(int(3 * color[i] + 2 * highlight_color[i]) // 5 for i in range(3)),  # Top (highlight)
            tuple(int(1 * color[i] + 4 * highlight_color[i]) // 5 for i in range(3)),  # Top-right (direct highlight)
        ]

        if highlight:
            # Recalculate colors for each side based on light source reoriented by 180 degrees
            side_colors = side_colors[-3:] + side_colors[:-3]

        # Draw the hexagon fill with 3D effect
        for i in range(6):
            pygame.draw.polygon(surface, side_colors[i], [points[i], points[(i + 1) % 6], (x, y)])

    # Draw the hexagon border
    pygame.draw.polygon(surface, border_color, points, border_width)

    if fill:
        # Draw a slightly smaller hexagon with uniform fill on top
        smaller_points = [
            ((x + HEX_SIDE * RAISE3D / 1), y),
            ((x + HEX_SIDE * RAISE3D / 2), (y + HEX_APOTHEM * RAISE3D)),
            ((x - HEX_SIDE * RAISE3D / 2), (y + HEX_APOTHEM * RAISE3D)),
            ((x - HEX_SIDE * RAISE3D / 1), y),
            ((x - HEX_SIDE * RAISE3D / 2), (y - HEX_APOTHEM * RAISE3D)),
            ((x + HEX_SIDE * RAISE3D / 2), (y - HEX_APOTHEM * RAISE3D)),
        ]
        pygame.draw.polygon(surface, color, smaller_points, 0)

    if text:
        font = pygame.font.SysFont(None, 22)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

def draw_board(surface, game_state, piece_images):
    """Draw the entire board."""
    board = game_state.board
    selected_hex = game_state.selected_hex
    possible_moves = game_state.possible_moves

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
                piece = board.get_piece(hex)
                text = str(piece) if piece else f"{q_labels[q]}{r_labels[r]}"
                draw_hexagon(surface, color, hex, text=text)

                if piece:
                    piece_image = piece_images[str(piece)]
                    piece_rect = piece_image.get_rect(center=hex_to_pixel(hex))
                    surface.blit(piece_image, piece_rect)

    font = pygame.font.SysFont(None, 24)

    # Draw row labels
    for label, hex in board.row_label_positions.items():
        label_text = font.render(label, True, BLACK)
        x, y = hex_to_pixel(hex)
        surface.blit(label_text, (x + HEX_SIDE // 2, y))

    # Draw column labels
    for label, hex in board.column_label_positions.items():
        label_text = font.render(label, True, BLACK)
        x, y = hex_to_pixel(hex)
        surface.blit(label_text, (x, y + HEX_HEIGHT // 2 + 10))

    # Highlight selected hex
    if selected_hex:
        draw_hexagon(surface, color=None, hex=selected_hex, border_color=HIGHLIGHT_COLOR, border_width=1, fill=False)

    # Highlight possible moves
    if possible_moves:
        for move in possible_moves:
            draw_hexagon(surface, color=None, hex=move, border_color=HIGHLIGHT_COLOR, border_width=1, fill=False)

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
    for i, (start, end, move_str) in enumerate(moves):
        if i % 2 == 0:
            move_num_text = font.render(f"{(i // 2) + 1}.", True, BLACK)
            surface.blit(move_num_text, (10, 40 + (i // 2) * MOVES_LINE_HEIGHT))
            move_text = font.render(move_str, True, BLACK)
            surface.blit(move_text, (50, 40 + (i // 2) * MOVES_LINE_HEIGHT))
        else:
            move_text = font.render(move_str, True, BLACK)
            surface.blit(move_text, (MOVES_LIST_WIDTH // 2 + 50, 40 + (i // 2) * MOVES_LINE_HEIGHT))

def handle_mouse_button_down(game_state, mouse_pos):
    """Handle mouse button down events."""
    board = game_state.board
    selected_hex = game_state.selected_hex
    possible_moves = game_state.possible_moves

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
    game_state = GameState()

    # Load piece images
    piece_images = load_piece_images("images")

    running = True
    redraw = True  # Flag to indicate if the screen needs to be redrawn
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                new_selected_hex, new_possible_moves = handle_mouse_button_down(game_state, pygame.mouse.get_pos())
                if new_selected_hex != game_state.selected_hex or new_possible_moves != game_state.possible_moves:
                    game_state.selected_hex, game_state.possible_moves = new_selected_hex, new_possible_moves
                    redraw = True  # Set redraw flag when there is a mouse event

        if redraw:
            screen.fill(WHITE)
            draw_board(screen, game_state, piece_images)
            pygame.display.flip()
            redraw = False  # Reset redraw flag after drawing

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()