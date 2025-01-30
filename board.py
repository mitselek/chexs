# -*- coding: utf-8 -*-
# board.py

import string  # Add this import
from hex import Hex, hex_directions
from piece import Piece
from piece_moves import * # Import all piece movement functions
from copy import deepcopy
from utils import format_piece, HEX_BORDERS, EMPTY_CELL, ASCII_EMPTY_CELL, get_cell_width, ROW_INDENT

PIECE_VALUES = {
    "P": 1,  # Pawn
    "N": 3,  # Knight
    "B": 3,  # Bishop
    "R": 5,  # Rook
    "Q": 9,  # Queen
    "K": 1000, # King (very high value)
}

UNIT_VECTORS = {
    "N": (0, -1, 1),  # North
    "NE": (1, -1, 0),  # North-East
    "SE": (1, 0, -1),  # South-East
    "S": (0, 1, -1),  # South
    "SW": (-1, 1, 0),  # South-West
    "NW": (-1, 0, 1),  # North-West
}

CENTER_BONUS = 0.1  # Bonus points per step closer to the center
MOBILITY_BONUS = 0.05  # Bonus points per legal move
KING_EXPOSURE_PENALTY = 0.5  # Penalty points per missing friendly piece around the king

class Board:
    """
    Represents the game board and manages game state.
    """
    BOARD_RADIUS = 5  # Distance from center (0,0,0) to edge

    # Attack direction constants
    PAWN_ATTACKS = {
        "white": [hex_directions[0], hex_directions[5]],  # NE, NW
        "black": [hex_directions[3], hex_directions[4]],  # SW, SE
    }
    
    ROOK_DIRECTIONS = set(hex_directions)  # All 6 primary directions
    hex_bishop_directions = [
        (hex_directions[0][0] + hex_directions[1][0], hex_directions[0][1] + hex_directions[1][1], hex_directions[0][2] + hex_directions[1][2]),  # NE + N  = NNE
        (hex_directions[1][0] + hex_directions[2][0], hex_directions[1][1] + hex_directions[2][1], hex_directions[1][2] + hex_directions[2][2]),  # N  + NW = NNW
        (hex_directions[2][0] + hex_directions[3][0], hex_directions[2][1] + hex_directions[3][1], hex_directions[2][2] + hex_directions[3][2]),  # NW + SW = W
        (hex_directions[3][0] + hex_directions[4][0], hex_directions[3][1] + hex_directions[4][1], hex_directions[3][2] + hex_directions[4][2]),  # SW + S  = SSW
        (hex_directions[4][0] + hex_directions[5][0], hex_directions[4][1] + hex_directions[5][1], hex_directions[4][2] + hex_directions[5][2]),  # S  + SE = SSE
        (hex_directions[5][0] + hex_directions[0][0], hex_directions[5][1] + hex_directions[0][1], hex_directions[5][2] + hex_directions[0][2])   # SE + NE = E
    ]    
    BISHOP_DIRECTIONS = set(hex_bishop_directions)  # Diagonal directions between primary directions
    QUEEN_DIRECTIONS = ROOK_DIRECTIONS | BISHOP_DIRECTIONS  # Queens can move in all directions
    
    # Knight move patterns (hard-coded)
    KNIGHT_PATTERNS = [
        ((1, 0, -1), (0, 1, -1)),  # NE, N
        ((1, 0, -1), (1, -1, 0)),  # NE, SE
        ((0, 1, -1), (-1, 1, 0)),  # N, NW
        ((0, 1, -1), (1, 0, -1)),  # N, NE
        ((-1, 1, 0), (-1, 0, 1)),  # NW, SW
        ((-1, 1, 0), (0, 1, -1)),  # NW, N
        ((-1, 0, 1), (0, -1, 1)),  # SW, S
        ((-1, 0, 1), (-1, 1, 0)),  # SW, NW
        ((0, -1, 1), (1, -1, 0)),  # S, SE
        ((0, -1, 1), (-1, 0, 1)),  # S, SW
        ((1, -1, 0), (1, 0, -1)),  # SE, NE
        ((1, -1, 0), (0, -1, 1)),  # SE, S
    ]

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

    # Tile labels
    q_labels = {q: letter for q, letter in zip(range(-5, 6), string.ascii_uppercase[:11])}
    r_labels = {r: str(r + 6) for r in range(-5, 6)}

    def __init__(self):
        """Initializes the board and sets up the pieces."""
        self.board = {}  # Dictionary: {Hex: Piece}
        self._king_positions = {"white": None, "black": None}  # Initialize before setup_board
        self.current_player = "white"
        self.move_number = 1  # Start at move 1
        self.moves_history = []  # List of (start_hex, end_hex, move_str) tuples
        self.setup_board()  # Call setup_board last
        self._move_cache = {}  # Cache for possible moves

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
        
        # Initialize king position cache
        for hex, piece in self.board.items():
            if piece.type == "K":
                self._king_positions[piece.color] = hex

    def is_occupied(self, hex):
        """Checks if a hex is occupied by a piece."""
        return hex in self.board

    def get_piece(self, hex):
        """Returns the piece at a given hex, or None if empty."""
        return self.board.get(hex)

    def move_piece(self, start_hex, end_hex):
        """Moves a piece from one hex to another and updates game state."""
        # print(f"Attempting to move piece from {start_hex} to {end_hex}")  # Debug line
        piece = self.get_piece(start_hex)
        if piece.color != self.current_player:
            raise ValueError(f"It's {self.current_player}'s turn to move")

        # Update board
        self.board[end_hex] = self.board.pop(start_hex).move(end_hex)
        
        # Update king position if king moved
        if piece.type == "K":
            self._king_positions[piece.color] = end_hex
        
        # Record the move in algebraic notation
        move_str = self.format_move(piece, start_hex, end_hex)
        self.moves_history.append((start_hex, end_hex, move_str))
        
        # Update turn counter if black just moved
        if self.current_player == "black":
            self.move_number += 1
            
        # Switch current player
        self.current_player = "black" if self.current_player == "white" else "white"

        # Handle pawn promotion
        if piece.type == "P":
            if (piece.color == "white" and end_hex.r == self.BOARD_RADIUS) or \
               (piece.color == "black" and end_hex.r == -self.BOARD_RADIUS):
                self.promote_pawn(end_hex, "Q")

        # Clear the move cache after a move
        self._move_cache.clear()
        self._last_move = (start_hex, end_hex)

    def get_possible_moves(self, hex):
        """Returns a set of legal moves for the piece at the given hex."""
        if hex in self._move_cache:
            return self._move_cache[hex]

        # print(f"Getting possible moves for piece at {hex}")  # Debug line
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
        if piece.type not in move_functions:
            return set()
        all_moves = move_functions[piece.type](self, piece)
        legal_moves = set()
        for move in all_moves:
            temp_board = deepcopy(self)
            temp_board.move_piece(hex, move)
            if not temp_board.is_check(self.current_player):
                legal_moves.add(move)

        self._move_cache[hex] = legal_moves
        return legal_moves

    def has_position_changed(self, hex):
        """Check if the position of the piece at the given hex has changed."""
        last_move = self._last_move if hasattr(self, '_last_move') else None
        return last_move and (hex == last_move[0] or hex == last_move[1])

    def get_pawn_moves(self, piece):
        """Calculate all valid moves for a pawn.
        
        Pawns move forward one step (or two on first move) and capture
        diagonally forward.
        
        Args:
            board: The game board
            piece: The pawn piece to move
            
        Returns:
            set: Valid destination hexes for the pawn
        """
        # print(f"Calculating pawn moves for piece at {piece.position}")  # Debug line
        moves = set()
        forward = hex_directions[0] if piece.color == "white" else hex_directions[3]
        one_step = piece.position + forward  # Using __add__
        # print(f"Checking one step move {one_step} from {piece.position} using direction {forward}")  # Debug line

        if self.is_valid_hex(one_step) and not self.is_occupied(one_step):
            moves.add(one_step)

            # Double first move
            if not piece.has_moved:
                two_step = one_step + forward  # Using __add__
                # print(f"Checking two step move {two_step} from {one_step} using direction {forward}")  # Debug line
                if self.is_valid_hex(two_step) and not self.is_occupied(two_step):
                    moves.add(two_step)

        # Captures
        capture_left = piece.position + (hex_directions[5] if piece.color == "white" else hex_directions[2])  # Using __add__
        capture_right = piece.position + (hex_directions[1] if piece.color == "white" else hex_directions[4])  # Using __add__
        # print(f"Checking capture moves {capture_left} and {capture_right} from {piece.position}")  # Debug line

        for capture_move in [capture_left, capture_right]:
            if self.is_valid_hex(capture_move) and self.is_occupied(capture_move) and self.get_piece(capture_move).color != piece.color:
                moves.add(capture_move)

        return moves

    def is_check(self, color: str) -> bool:
        """Checks if the given color's king is in check.
        
        Uses precomputed attack patterns for efficiency.
        Short-circuits as soon as check is detected.
        
        Args:
            color: The color ("white" or "black") to check

        Returns:
            bool: True if king is in check, False otherwise
        """
        king_pos = self._king_positions.get(color)
        if not king_pos:
            return False

        opponent = "black" if color == "white" else "white"
        
        # Check nearby squares for enemy king
        for direction in hex_directions:
            adjacent = king_pos + direction
            if (self.is_valid_hex(adjacent) and 
                (piece := self.get_piece(adjacent)) and 
                piece.type == "K" and piece.color == opponent):
                return True

        # Check pawn attacks
        for direction in self.PAWN_ATTACKS[opponent]:
            attack_pos = king_pos + direction
            if (self.is_valid_hex(attack_pos) and 
                (piece := self.get_piece(attack_pos)) and 
                piece.type == "P" and piece.color == opponent):
                return True

        # Check knight attacks using precomputed patterns
        for d1, d2 in self.KNIGHT_PATTERNS:
            attack_pos = king_pos + d1 + d2
            if (self.is_valid_hex(attack_pos) and 
                (piece := self.get_piece(attack_pos)) and 
                piece.type == "N" and piece.color == opponent):
                return True

        # Check sliding pieces (rooks and queens along primary directions)
        for direction in hex_directions:
            current = king_pos
            while True:
                current = current + direction
                if not self.is_valid_hex(current):
                    break
                    
                if piece := self.get_piece(current):
                    if piece.color == opponent:
                        if piece.type == "Q" or piece.type == "R":
                            return True
                    break  # Blocked by any piece

        # Check sliding pieces (bishops and queens along diagonal directions)
        for direction in self.BISHOP_DIRECTIONS:
            current = king_pos
            while True:
                current = current + direction
                if not self.is_valid_hex(current):
                    break
                    
                if piece := self.get_piece(current):
                    if piece.color == opponent:
                        if piece.type == "Q" or piece.type == "B":
                            return True
                    break  # Blocked by any piece
                
        return False

    def is_checkmate(self, color):
        """Checks if the given color's king is checkmated.
        
        A checkmate occurs when:
        1. The king is in check
        2. No legal move by any piece can get the king out of check

        Args:
            color: The color ("white" or "black") to check for checkmate

        Returns:
            bool: True if checkmated, False if:
            - The king is not in check
            - There exists at least one legal move to escape check
            - No king of that color exists on the board
            - The color is invalid
        """
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

    def evaluate_position(self) -> int:
        """Evaluates the board position based on several factors:
        
        - Piece values: Each piece type has a specific value (e.g., pawn = 1, queen = 9).
        - Proximity to the center: Pieces closer to the center receive bonus points.
        - Mobility: The number of legal moves available for each piece.
        - King exposure: Penalty points for each missing friendly piece around the king.
        
        The evaluation score is positive if the current player has an advantage,
        and negative if the opponent has an advantage.

        Returns:
            int: The evaluation score (positive for current player, negative for opponent).
        """
        score = 0
        center = Hex(0, 0, 0)
        for hex, piece in self.board.items():
            value = PIECE_VALUES[piece.type]
            distance_to_center = abs(hex - center)
            center_bonus = (self.BOARD_RADIUS - distance_to_center) * CENTER_BONUS
            mobility_bonus = len(self.get_possible_moves(hex)) * MOBILITY_BONUS
            king_exposure_penalty = 0

            if piece.type == "K":
                friendly_pieces_nearby = 0
                for direction in hex_directions:
                    adjacent = hex + direction
                    if self.is_valid_hex(adjacent):
                        adjacent_piece = self.get_piece(adjacent)
                        if adjacent_piece and adjacent_piece.color == piece.color:
                            friendly_pieces_nearby += 1
                king_exposure_penalty = (6 - friendly_pieces_nearby) * KING_EXPOSURE_PENALTY

            if piece.color == self.current_player:
                score += value + center_bonus + mobility_bonus - king_exposure_penalty
            else:
                score -= value + center_bonus + mobility_bonus - king_exposure_penalty

        return score

    def evaluate_position_for(self, player_color: str) -> float:
        """Evaluates the board position from a specific player's perspective."""
        score = 0
        center = Hex(0, 0, 0)
        for hex, piece in self.board.items():
            value = PIECE_VALUES[piece.type]
            distance_to_center = abs(hex - center)
            center_bonus = (self.BOARD_RADIUS - distance_to_center) * CENTER_BONUS
            mobility_bonus = len(self.get_possible_moves(hex)) * MOBILITY_BONUS
            king_exposure_penalty = 0

            if piece.type == "K":
                friendly_pieces_nearby = 0
                for direction in hex_directions:
                    adjacent = hex + direction
                    if self.is_valid_hex(adjacent):
                        adjacent_piece = self.get_piece(adjacent)
                        if adjacent_piece and adjacent_piece.color == piece.color:
                            friendly_pieces_nearby += 1
                king_exposure_penalty = (6 - friendly_pieces_nearby) * KING_EXPOSURE_PENALTY

        piece_score = value + center_bonus + mobility_bonus - king_exposure_penalty
        if piece.color == player_color:
            score += piece_score
        else:
            score -= piece_score

        return round(score, 2)  # Round to 2 decimal places

    def get_turn_info(self) -> str:
        """Returns a string describing the current game state."""
        return f"Move {self.move_number}, {self.current_player} to play"

    def get_last_move(self) -> tuple:
        """Returns the last move made (start_hex, end_hex) or None if no moves made."""
        return self.moves_history[-1] if self.moves_history else None

    def __repr__(self):
        """Returns an unambiguous string representation of the board."""
        return (f"Board({len(self.board)} pieces, "
                f"move {self.move_number}, {self.current_player} to play)")

    def display(self, use_unicode=True, show_coords=False, use_colors=True, border_style="simple") -> str:
        """Returns a hexagonal string representation of the board.
        
        The board uses cubic coordinates (q,r,s) where:
        - q increases from left to right
        - r increases from top to bottom
        - s = -q - r (derived from q and r)
        
        The display shows:
        - White pieces at the bottom (South)
        - Black pieces at the top (North)
        - Empty cells as dots (·) or spaces depending on unicode setting
        
        Args:
            use_unicode: Whether to use Unicode chess symbols
            show_coords: Whether to show r-coordinates on the right
            use_colors: Whether to use ANSI colors in terminal output
            border_style: Border style ("simple" or "double")
        
        Returns:
            str: A multi-line string representation of the board
            
        Note:
            The coordinate system displayed (when show_coords=True)
            shows the r-coordinate, which increases from top to bottom.
        """
        borders = HEX_BORDERS[border_style]
        output = []
        empty = EMPTY_CELL if use_unicode else ASCII_EMPTY_CELL
        cell_width = get_cell_width(use_unicode)

        # Create board content - iterate from top (black) to bottom (white)
        for r in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):
            # Calculate row indentation
            indent = " " * abs(r) + " " * ROW_INDENT
            row = []

            for q in range(-self.BOARD_RADIUS, self.BOARD_RADIUS + 1):
                s = -q - r
                if not self.is_valid_hex(Hex(q, r, s)):
                    continue
                hex = Hex(q, r, s)
                piece = self.get_piece(hex)
                if piece:
                    cell = format_piece(str(piece), use_unicode, use_colors)
                    row.append(f"{cell:^{cell_width}}")
                else:
                    row.append(f"{empty:^{cell_width}}")

            # Add hex borders
            hex_row = []
            for i, cell in enumerate(row):
                if i > 0 and row[i-1].strip():  # Only add vertical borders between valid cells
                    hex_row.append("X")
                hex_row.append(cell)

            # Add coordinates if requested
            coord_suffix = f" r={r:2d}" if show_coords else ""
            
            # Determine the appropriate edge characters
            if r < 0:
                edge_left = borders['nw_edge']
                edge_right = borders['ne_edge']
            elif r == 0:
                edge_left = '<'
                edge_right = '>'
            else:
                edge_left = borders['ne_edge']
                edge_right = borders['nw_edge']

            # Join the row parts and check if it contains any non-space characters
            row_str = "".join(hex_row)
            if row_str.strip():  # Only add non-empty rows
                output.append(f"{indent}{edge_left}{row_str}{edge_right}{coord_suffix}")

        return "\n".join(output)

    def __str__(self):
        """Returns a formatted string representation of the board."""
        return self.display()

    def format_move(self, piece, start_hex, end_hex):
        """Formats a move in algebraic notation."""
        piece_str = piece.type if piece.type != "P" else ""
        capture_str = "x" if self.is_occupied(end_hex) else ""
        end_pos_str = f"{self.q_labels[end_hex.q]}{self.r_labels[end_hex.r]}"
        return f"{piece_str}{capture_str}{end_pos_str}"