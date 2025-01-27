# Gliński's Hexagonal Chess

## Core Classes

### Hex
Represents a single hexagon on the board using cubic coordinates.

**Attributes:**
- `q, r, s`: Cubic coordinates (integers)

**Methods:**
- `__init__(self, q, r, s)`: Constructor, ensures q + r + s == 0
- `__eq__(self, other)`: Equality check
- `__hash__(self)`: Hash function for sets/dictionaries
- `to_tuple(self)`: Returns coordinates as tuple
- `get_color(self)`: Returns hex color ("green", "blue", "red")

### Piece
Represents a chess piece.

**Attributes:**
- `type`: Piece type ("P", "R", "N", "B", "Q", "K")
- `color`: Piece color ("white" or "black")
- `position`: Hex object for piece location
- `has_moved`: Boolean for tracking first move

**Methods:**
- `__init__(self, type, color, position)`: Constructor
- `__repr__(self)`: String representation

### Board
Manages game state and board representation.

**Attributes:**
- `board`: Dictionary mapping Hex objects to Piece objects
- `current_player`: Current turn ("white" or "black")

**Methods:**
- `__init__()`: Constructor and board initialization
- `setup_board()`: Initial piece setup (Gliński's configuration)
- `is_valid_hex(hex)`: Boundary validation
- `is_occupied(hex)`: Position occupation check
- `get_piece(hex)`: Piece retrieval
- `move_piece(start_hex, end_hex)`: Move execution
- `get_possible_moves(hex)`: Legal move calculation
- `is_check(color)`: Check detection
- `is_checkmate(color)`: Checkmate detection