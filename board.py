# -*- coding: utf-8 -*-
from hex import Hex
from piece import Piece
from piece_moves import * # Import all piece movement functions
from copy import deepcopy
from utils import format_piece, HEX_BORDERS, EMPTY_CELL, ASCII_EMPTY_CELL, get_cell_width, ROW_INDENT

class Board:
    """
    Represents the game board and manages game state.
    """
    BOARD_RADIUS = 5  # Distance from center (0,0,0) to edge

    def __init__(self):
        """
        Initializes the board and sets up the pieces.
        """
        self.board = {}  # Dictionary: {Hex: Piece}
        self.current_player = "white"
        self.setup_board()

    def is_valid_hex(self, hex):
        """Checks if a hex is within the board boundaries and forms a valid hexagonal shape.
        
        For radius 5, valid coordinates must satisfy:
        1. -5 ≤ q,r,s ≤ 5 (within radius)
        2. q + r + s = 0 (cubic coordinates)
        3. max(|q|, |r|, |s|) ≤ 5 (hexagonal shape)
        """
        # Check cubic coordinate constraint
        if hex.q + hex.r + hex.s != 0:
            return False
            
        # Check radius constraint
        if (abs(hex.q) > self.BOARD_RADIUS or 
            abs(hex.r) > self.BOARD_RADIUS or 
            abs(hex.s) > self.BOARD_RADIUS):
            return False
            
        # Check hexagonal shape using max norm
        if max(abs(hex.q), abs(hex.r), abs(hex.s)) > self.BOARD_RADIUS:
            return False
            
        return True

    def setup_board(self):
        """Sets up the initial board configuration for radius 5 board."""
        self.board = {
            # White center bishop row from South corner
            Hex(0, -5, 5): Piece("B", "white", Hex(0, -5, 5)),    # Bishop
            Hex(0, -4, 4): Piece("B", "white", Hex(0, -4, 4)),    # Bishop
            Hex(0, -3, 3): Piece("B", "white", Hex(0, -3, 3)),    # Bishop

            # White left back row
            Hex(-1, -4, 5): Piece("Q", "white", Hex(-1, -4, 5)),  # Queen
            Hex(-2, -3, 5): Piece("N", "white", Hex(-2, -3, 5)),  # Knight
            Hex(-3, -2, 5): Piece("R", "white", Hex(-3, -2, 5)),  # Rook
            
            # White right back row
            Hex(1, -5, 4): Piece("K", "white", Hex(1, -5, 4)),    # King
            Hex(2, -5, 3): Piece("N", "white", Hex(2, -5, 3)),    # Knight
            Hex(3, -5, 2): Piece("R", "white", Hex(3, -5, 2)),    # Rook

            # White pawns from left to right
            Hex(-4, -1, 5): Piece("P", "white", Hex(-4, -1, 5)),  # Pawn
            Hex(-3, -1, 4): Piece("P", "white", Hex(-3, -1, 4)),  # Pawn
            Hex(-2, -1, 3): Piece("P", "white", Hex(-2, -1, 3)),  # Pawn
            Hex(-1, -1, 2): Piece("P", "white", Hex(-1, -1, 2)),  # Pawn
            Hex(0, -1, 1): Piece("P", "white", Hex(0, -1, 1)),    # Pawn
            Hex(1, -2, 1): Piece("P", "white", Hex(1, -2, 1)),    # Pawn
            Hex(2, -3, 1): Piece("P", "white", Hex(2, -3, 1)),    # Pawn
            Hex(3, -4, 1): Piece("P", "white", Hex(3, -4, 1)),    # Pawn
            Hex(4, -5, 1): Piece("P", "white", Hex(4, -5, 1)),    # Pawn

            # Black pieces mirrored across the center
            Hex(0, 5, -5): Piece("B", "black", Hex(0, 5, -5)),    # Bishop
            Hex(0, 4, -4): Piece("B", "black", Hex(0, 4, -4)),    # Bishop
            Hex(0, 3, -3): Piece("B", "black", Hex(0, 3, -3)),    # Bishop

            Hex(-1, 5, -4): Piece("Q", "black", Hex(-1, 5, -4)),  # Queen
            Hex(-2, 5, -3): Piece("N", "black", Hex(-2, 5, -3)),  # Knight
            Hex(-3, 5, -2): Piece("R", "black", Hex(-3, 5, -2)),  # Rook

            Hex(1, 4, -5): Piece("K", "black", Hex(1, 4, -5)),    # King
            Hex(2, 3, -5): Piece("N", "black", Hex(2, 3, -5)),    # Knight
            Hex(3, 2, -5): Piece("R", "black", Hex(3, 2, -5)),    # Rook

            Hex(-4, 5, -1): Piece("P", "black", Hex(-4, 5, -1)),  # Pawn
            Hex(-3, 4, -1): Piece("P", "black", Hex(-3, 4, -1)),  # Pawn
            Hex(-2, 3, -1): Piece("P", "black", Hex(-2, 3, -1)),  # Pawn
            Hex(-1, 2, -1): Piece("P", "black", Hex(-1, 2, -1)),  # Pawn
            Hex(0, 1, -1): Piece("P", "black", Hex(0, 1, -1)),    # Pawn
            Hex(1, 1, -2): Piece("P", "black", Hex(1, 1, -2)),    # Pawn
            Hex(2, 1, -3): Piece("P", "black", Hex(2, 1, -3)),    # Pawn
            Hex(3, 1, -4): Piece("P", "black", Hex(3, 1, -4)),    # Pawn
            Hex(4, 1, -5): Piece("P", "black", Hex(4, 1, -5)),    # Pawn
        }

    def is_occupied(self, hex):
        """Checks if a hex is occupied by a piece."""
        return hex in self.board

    def get_piece(self, hex):
        """Returns the piece at a given hex, or None if empty."""
        return self.board.get(hex)

    def move_piece(self, start_hex, end_hex):
        """Moves a piece from one hex to another."""
        piece = self.board.pop(start_hex)
        piece.move(end_hex)
        self.board[end_hex] = piece
        self.current_player = "black" if self.current_player == "white" else "white"

        # Promotion logic
        if piece.type == "P":
            if (piece.color == "white" and end_hex.r == 4) or (piece.color == "black" and end_hex.r == -4):
                self.promote_pawn(end_hex, "Q")  # Promote at the end hex

    def get_possible_moves(self, hex):
        """Returns a set of legal moves for the piece at the given hex."""
        piece = self.get_piece(hex)
        if piece is None or piece.color != self.current_player:
            return set()

        move_functions = {
            "N": get_knight_moves,
            "R": get_rook_moves,
            "B": get_bishop_moves,
            "Q": get_queen_moves,
            "K": get_king_moves,
            "P": get_pawn_moves,
        }
        if piece.type in move_functions:
            return move_functions[piece.type](self, piece)
        return set()

    def is_check(self, color):
        """Checks if the given color's king is in check."""
        # Find king position
        king_pos = None
        for hex, piece in self.board.items():
            if piece.type == "K" and piece.color == color:
                king_pos = hex
                break
        if king_pos is None:
            return False

        opponent_color = "black" if color == "white" else "white"
        
        # Check pawns (they can only attack in specific directions)
        pawn_attacks = [hex_directions[1], hex_directions[5]] if opponent_color == "white" else [hex_directions[2], hex_directions[4]]
        for direction in pawn_attacks:
            attack_pos = king_pos + direction
            if self.is_valid_hex(attack_pos):
                piece = self.get_piece(attack_pos)
                if piece and piece.type == "P" and piece.color == opponent_color:
                    return True

        # Check knights
        for hex, piece in self.board.items():
            if piece.color == opponent_color and piece.type == "N":
                if abs(king_pos - hex) == 2:  # Knights move in L-shape (2 steps)
                    return True

        # Check sliding pieces (rook, bishop, queen)
        for direction in hex_directions:
            current = king_pos
            while True:
                current = current + direction
                if not self.is_valid_hex(current):
                    break
                piece = self.get_piece(current)
                if piece:
                    if piece.color == opponent_color:
                        # Check if piece can attack along this line
                        if piece.type == "Q":  # Queen attacks in all directions
                            return True
                        if piece.type == "R" and direction in hex_directions:  # Rook attacks orthogonally
                            return True
                        if piece.type == "B" and direction in [hex_directions[i] for i in [1,3,5]]:  # Bishop attacks diagonally
                            return True
                    break  # Blocked by any piece
                
        return False

    def is_checkmate(self, color):
        """Checks if the given color is checkmated."""
        if not self.is_check(color):
            return False

        for hex, piece in self.board.items():
            if piece.color == color:
                for move in self.get_possible_moves(hex):
                    # Create a deep copy of the board to test moves
                    temp_board = deepcopy(self)
                    temp_board.move_piece(piece.position, move)
                    if not temp_board.is_check(color):
                        return False

        return True

    def __repr__(self):
        """Returns an unambiguous string representation of the board (for debugging)."""
        pieces = [f"{pos}:{piece.type}{piece.color[0]}" for pos, piece in self.board.items()]
        return f"Board({len(pieces)} pieces, current_player='{self.current_player}')"

    def display(self, use_unicode=True, show_coords=False, use_colors=True, border_style="simple") -> str:
        """Returns a hexagonal string representation of the board.
        
        The board is displayed with white pieces at the bottom (South)
        and black pieces at the top (North).
        """
        borders = HEX_BORDERS[border_style]
        output = []
        empty = EMPTY_CELL if use_unicode else ASCII_EMPTY_CELL
        cell_width = get_cell_width(use_unicode)

        # Create board content - iterate from top (black) to bottom (white)
        for r in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):  # Changed iteration order
            # Calculate row indentation (reversed to match new order)
            indent = " " * (ROW_INDENT + (self.BOARD_RADIUS + r) * 2)  # Changed sign in calculation
            row = []

            for q in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):
                s = -q - r
                if abs(q) <= self.BOARD_RADIUS and abs(r) <= self.BOARD_RADIUS and abs(s) <= self.BOARD_RADIUS:
                    hex = Hex(q, r, s)
                    piece = self.get_piece(hex)
                    if piece:
                        cell = format_piece(str(piece), use_unicode, use_colors)
                        row.append(f"{cell:^{cell_width}}")
                    else:
                        row.append(f"{empty:^{cell_width}}")
                else:
                    row.append(" " * cell_width)

            # Add hex borders
            hex_row = []
            for i, cell in enumerate(row):
                if i > 0:
                    hex_row.append(borders["vertical"])
                hex_row.append(cell)

            # Add coordinates if requested
            coord_suffix = f" r={r:2d}" if show_coords else ""
            
            # Join the row parts and check if it contains any non-space characters
            row_str = "".join(hex_row)
            if row_str.strip():  # Only add non-empty rows
                output.append(f"{indent}{borders['nw_edge']}{row_str}{borders['ne_edge']}{coord_suffix}")

        return "\n".join(output)

    def __str__(self):
        """Returns a formatted string representation of the board."""
        return self.display()

def print_board(board, use_unicode=True, show_coords=False):
    """Returns a formatted string representation of the board."""
    output = ""
    for q in range(-board.BOARD_RADIUS, board.BOARD_RADIUS + 1):
        for r in range(max(-board.BOARD_RADIUS, -q-board.BOARD_RADIUS), 
                     min(board.BOARD_RADIUS + 1, -q+board.BOARD_RADIUS + 1)):
            hex = Hex(q, r, -q-r)
            piece = board.get_piece(hex)
            if piece:
                output += str(piece) + " "
            else:
                output += ". "
        output += "\n"
    return output