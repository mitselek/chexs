from typing import Dict, Optional
import os
import pygame

# Unicode chess piece symbols
UNICODE_PIECES: Dict[str, str] = {
    "wP": "♙", "wR": "♖", "wN": "♘", "wB": "♗", "wQ": "♕", "wK": "♔",
    "bP": "♟", "bR": "♜", "bN": "♞", "bB": "♝", "bQ": "♛", "bK": "♚",
}

# ANSI color and style codes
COLORS = {
    "white": "\033[97m",      # Bright white
    "black": "\033[30m",      # Black
    "reset": "\033[0m",       # Reset all
    "bg_light": "\033[47m",   # Light background
    "bg_dark": "\033[100m",   # Dark background
}

# Board display constants
BORDER_STYLES = {
    "simple": {
        "horizontal": "─",
        "vertical": "│",
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
    },
    "double": {
        "horizontal": "═",
        "vertical": "║",
        "top_left": "╔",
        "top_right": "╗",
        "bottom_left": "╚",
        "bottom_right": "╝",
    }
}

# Hex board display constants
HEX_BORDERS = {
    "simple": {
        "nw_edge": "╱",  # North-west edge
        "ne_edge": "╲",  # North-east edge
        "vertical": "│",
        "horizontal": "─",
        "cross": "┼",
    },
    "double": {
        "nw_edge": "╱",
        "ne_edge": "╲",
        "vertical": "║",
        "horizontal": "═",
        "cross": "╬",
    }
}

# Display constants
EMPTY_CELL = "·"  # Unicode empty cell
ASCII_EMPTY_CELL = "  "  # ASCII empty cell (double space)
ASCII_CELL_WIDTH = 2  # Width for ASCII display
UNICODE_CELL_WIDTH = 1  # Width for Unicode display
ROW_INDENT = 4 # Indentation for row numbers

def get_cell_width(use_unicode: bool) -> int:
    """Returns appropriate cell width based on display mode."""
    return UNICODE_CELL_WIDTH if use_unicode else ASCII_CELL_WIDTH

def supports_unicode() -> bool:
    """Check if the terminal supports Unicode characters."""
    return 'UTF-8' in os.environ.get('LANG', '').upper()

def supports_ansi() -> bool:
    """Check if the terminal supports ANSI escape codes."""
    return os.environ.get('TERM') is not None

def format_piece(piece_str: str, use_unicode: bool = True, use_colors: bool = True) -> str:
    """Format a piece string with Unicode symbols and/or colors.

    Args:
        piece_str: The piece string (e.g., "wP", "bK")
        use_unicode: Whether to use Unicode chess symbols
        use_colors: Whether to use ANSI colors in terminal output

    Returns:
        The formatted piece string

    Raises:
        ValueError: If piece_str is not in the format [w|b][P|R|N|B|Q|K]
    """
    if not piece_str or len(piece_str) != 2 or piece_str[0] not in 'wb':
        raise ValueError(f"Invalid piece string: {piece_str}")

    # Check terminal capabilities
    use_unicode &= supports_unicode()
    use_colors &= supports_ansi()
    
    # Get the piece symbol
    if use_unicode and piece_str in UNICODE_PIECES:
        formatted = UNICODE_PIECES[piece_str]
    else:
        formatted = piece_str

    # Apply colors if supported
    if use_colors:
        color = "white" if piece_str.startswith("w") else "black"
        formatted = COLORS[color] + formatted + COLORS["reset"]

    return formatted

def create_border(width: int, style: str = "simple") -> str:
    """Create a border string for the board display.

    Args:
        width: The width of the border
        style: The border style ("simple", "double", or "heavy")

    Returns:
        The border string

    Raises:
        ValueError: If style is not one of the supported styles
    """
    styles = {
        "simple": "-",
        "double": "═",
        "heavy": "━",
    }
    
    if style not in styles:
        valid_styles = '", "'.join(styles.keys())
        raise ValueError(f'Invalid border style: "{style}". Must be one of: "{valid_styles}"')
    
    return styles[style] * width

def load_piece_images(image_folder):
    """Load images for chess pieces from the specified folder."""
    piece_images = {}
    piece_types = ["P", "R", "N", "B", "Q", "K"]
    colors = ["w", "b"]
    for color in colors:
        for piece in piece_types:
            piece_str = f"{color}{piece}"
            image_path = os.path.join(image_folder, f"{piece_str}.png")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"No file '{image_path}' found in working directory '{os.getcwd()}'.")
            piece_images[piece_str] = pygame.image.load(image_path)
    return piece_images