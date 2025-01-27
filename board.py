# -*- coding: utf-8 -*-
from hex import Hex
from piece import Piece
from piece_moves import * # Import all piece movement functions
from copy import deepcopy
from utils import format_piece

class Board:
    """
    Represents the game board and manages game state.
    """
    BOARD_RADIUS = 4  # Distance from center (0,0,0) to edge

    def __init__(self):
        """
        Initializes the board and sets up the pieces.
        """
        self.board = {}  # Dictionary: {Hex: Piece}
        self.current_player = "white"
        self.setup_board()

    def setup_board(self):
        """
        Sets up the initial board configuration (Gliński's setup).
        """
        self.board = {
            Hex(-4, 2, 2): Piece("R", "white", Hex(-4, 2, 2)),
            Hex(-4, 1, 3): Piece("N", "white", Hex(-4, 1, 3)),
            Hex(-4, 0, 4): Piece("B", "white", Hex(-4, 0, 4)),
            Hex(-3, 0, 3): Piece("Q", "white", Hex(-3, 0, 3)),
            Hex(-2, 0, 2): Piece("K", "white", Hex(-2, 0, 2)),
            Hex(-4, -1, 5): Piece("B", "white", Hex(-4, -1, 5)),
            Hex(-4, -2, 6): Piece("N", "white", Hex(-4, -2, 6)),
            Hex(-4, -3, 7): Piece("R", "white", Hex(-4, -3, 7)),
            Hex(-3, -3, 6): Piece("B", "white", Hex(-3, -3, 6)),
            Hex(-2, -2, 4): Piece("P", "white", Hex(-2, -2, 4)),
            Hex(-1, -1, 2): Piece("P", "white", Hex(-1, -1, 2)),
            Hex(0, 0, 0): Piece("P", "white", Hex(0, 0, 0)),
            Hex(1, 1, -2): Piece("P", "white", Hex(1, 1, -2)),
            Hex(2, 2, -4): Piece("P", "white", Hex(2, 2, -4)),
             #Black pieces
            Hex(4, -2, -2): Piece("R", "black", Hex(4, -2, -2)),
            Hex(4, -1, -3): Piece("N", "black", Hex(4, -1, -3)),
            Hex(4, 0, -4): Piece("B", "black", Hex(4, 0, -4)),
            Hex(3, 0, -3): Piece("Q", "black", Hex(3, 0, -3)),
            Hex(2, 0, -2): Piece("K", "black", Hex(2, 0, -2)),
            Hex(4, 1, -5): Piece("B", "black", Hex(4, 1, -5)),
            Hex(4, 2, -6): Piece("N", "black", Hex(4, 2, -6)),
            Hex(4, 3, -7): Piece("R", "black", Hex(4, 3, -7)),
            Hex(3, 3, -6): Piece("B", "black", Hex(3, 3, -6)),
            Hex(2, 2, -4): Piece("P", "black", Hex(2, 2, -4)),
            Hex(1, 1, -2): Piece("P", "black", Hex(1, 1, -2)),
            Hex(0, 0, 0): Piece("P", "black", Hex(0, 0, 0)),
            Hex(-1, -1, 2): Piece("P", "black", Hex(-1, -1, 2)),
            Hex(-2, -2, 4): Piece("P", "black", Hex(-2, -2, 4)),
        }

    def is_valid_hex(self, hex):
        """Checks if a hex is within the board boundaries."""
        return (abs(hex.q) <= self.BOARD_RADIUS and 
                abs(hex.r) <= self.BOARD_RADIUS and 
                abs(hex.s) <= self.BOARD_RADIUS)

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

    def display(self, use_unicode=True, show_coords=False, use_colors=True):
        """Returns a formatted string representation of the board.

        Args:
            use_unicode (bool): Whether to use Unicode chess symbols
            show_coords (bool): Whether to show coordinates
            use_colors (bool): Whether to use ANSI colors in terminal output
        """
        output = "     " + "----" * (self.BOARD_RADIUS + 1) + "\n"
        for r in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):
            output += "  " * (self.BOARD_RADIUS - r) + "| "
            for q in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):
                s = -q - r
                if abs(q) <= self.BOARD_RADIUS and abs(r) <= self.BOARD_RADIUS and abs(s) <= self.BOARD_RADIUS:
                    hex = Hex(q, r, s)
                    piece = self.get_piece(hex)
                    if piece:
                        output += format_piece(str(piece), use_unicode, use_colors) + " "
                    else:
                        output += "· "
                else:
                    output += "  "
            output += "|\n"
        output += "     " + "----" * (self.BOARD_RADIUS + 1) + "\n"
        return output

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