from hex import Hex, hex_directions
from piece import Piece  # Ensure to import Piece class
import math

def get_bishop_moves(board, piece):
    """Gets all valid bishop moves along diagonals."""
    moves = set()
    for direction in board.BISHOP_DIRECTIONS:
        current = piece.position
        while True:
            current = current + direction
            if not board.is_valid_hex(current):
                break
            target = board.get_piece(current)
            if target:
                if target.color != piece.color:
                    moves.add(current)
                break
            moves.add(current)
    return moves

def get_knight_moves(board, piece):
    """Calculate all valid moves for a knight.
    
    A knight moves in an L-shape pattern: 2 steps in one direction, then 1 step 
    at a 120-degree angle.
    
    Args:
        board: The game board
        piece: The knight piece to move
        
    Returns:
        set: Valid destination hexes for the knight
    """
    moves = set()
    for d1_index, d1 in enumerate(hex_directions):
        for d2_index in [(d1_index + 2) % 6, (d1_index + 4) % 6]:
            d2 = hex_directions[d2_index]
            move = piece.position + d1 + d2  # More readable!
            if board.is_valid_hex(move):
                target_piece = board.get_piece(move)
                if target_piece is None or target_piece.color != piece.color:
                    moves.add(move)
    return moves

def get_rook_moves(board, piece):
    """Calculate all valid moves for a rook.
    
    A rook moves any number of steps along the six primary hex directions.
    Movement is blocked by other pieces.
    
    Args:
        board: The game board
        piece: The rook piece to move
        
    Returns:
        set: Valid destination hexes for the rook
    """
    moves = set()
    for direction in hex_directions:
        current = piece.position
        while True:
            current = current + direction  # Using __add__ instead of hex_add
            if not board.is_valid_hex(current):
                break
            target = board.get_piece(current)
            if target:
                if target.color != piece.color:
                    moves.add(current)
                break  # Blocked by a piece
            moves.add(current)
    return moves

def get_queen_moves(board, piece):
    """Calculate all valid moves for a queen.
    
    A queen combines rook and bishop movements.
    
    Args:
        board: The game board
        piece: The queen piece to move
        
    Returns:
        set: Valid destination hexes for the queen
    """
    return get_rook_moves(board, piece) | get_bishop_moves(board, piece)

def get_king_moves(board, piece):
    """Calculate all valid moves for a king.
    
    A king moves one step in any of the six primary hex directions.
    
    Args:
        board: The game board
        piece: The king piece to move
        
    Returns:
        set: Valid destination hexes for the king
    """
    moves = set()
    for direction in hex_directions:
        move = piece.position + direction  # Using __add__
        if board.is_valid_hex(move):
            target_piece = board.get_piece(move)
            if target_piece is None or target_piece.color != piece.color:
                moves.add(move)
    return moves

def get_pawn_moves(board, piece):
    """Calculate all valid moves for a pawn.
    
    Pawns move forward one step (or two on first move) and capture
    diagonally forward.
    
    Args:
        board: The game board
        piece: The pawn piece to move
        
    Returns:
        set: Valid destination hexes for the pawn
    """
    moves = set()
    forward = hex_directions[0] if piece.color == "white" else hex_directions[3]
    one_step = piece.position + forward  # Using __add__

    if board.is_valid_hex(one_step) and not board.is_occupied(one_step):
        moves.add(one_step)

        # Double first move
        if not piece.has_moved:
            two_step = one_step + forward  # Using __add__
            if board.is_valid_hex(two_step) and not board.is_occupied(two_step):
                moves.add(two_step)

    # Captures
    capture_left = piece.position + (hex_directions[5] if piece.color == "white" else hex_directions[2])  # Using __add__
    capture_right = piece.position + (hex_directions[1] if piece.color == "white" else hex_directions[4])  # Using __add__

    for capture_move in [capture_left, capture_right]:
        if board.is_valid_hex(capture_move) and board.is_occupied(capture_move) and board.get_piece(capture_move).color != piece.color:
            moves.add(capture_move)

    return moves

def promote_pawn(board, hex, new_type): # Now takes hex as argument
    """Promotes a pawn to a new piece type at given hex."""
    piece = board.get_piece(hex)
    if piece is None or piece.type != "P":
        raise ValueError("No pawn to promote at given hex")

    if new_type not in ("R", "N", "B", "Q"):
        raise ValueError("Invalid promotion type")

    board.board[hex] = Piece(new_type, piece.color, hex)  # Creates new piece object

