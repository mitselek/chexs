# Gliński's Hexagonal Chess

## Core Classes

### `Hex`

Represents a single hexagon on the board using cubic coordinates.

**Attributes:**

*   `q` (int): The q coordinate.
*   `r` (int): The r coordinate.
*   `s` (int): The s coordinate (calculated as `-q - r`).

**Methods:**

*   `__init__(self, q: int, r: int, s: int)`: Initializes a `Hex` object.

    *   Args:
        *   `q` (int): The q coordinate.
        *   `r` (int): The r coordinate.
        *   `s` (int): The s coordinate.
    *   Raises:
        *   `ValueError`: If `q + r + s != 0`.

*   `__eq__(self, other: object) -> bool`: Checks if two `Hex` objects are equal.

    *   Args:
        *   `other` (object): The object to compare with.
    *   Returns:
        *   `bool`: `True` if the coordinates are equal, `False` otherwise.

*   `__hash__(self) -> int`: Returns a hash value for the `Hex` object. This is necessary for using `Hex` objects as keys in dictionaries and sets.

    *   Returns:
        *   `int`: A hash value.

*   `to_tuple(self) -> Tuple[int, int, int]`: Returns the coordinates of the hex as a tuple.

    *   Returns:
        *   `Tuple[int, int, int]`: A tuple containing the `q`, `r`, and `s` coordinates.

*   `get_color(self) -> str`: Calculates and returns the color of the hex.

    *   Returns:
        *   `str`: A string representing the color of the hex ("green", "blue", or "red").

*   `__add__(self, other: Union[Hex, Tuple[int, int, int]]) -> Hex`: Adds a hex to another hex or a direction tuple.

    *   Args:
        *   `other` (Union[Hex, Tuple[int, int, int]]): Either a `Hex` object or a tuple of (q, r, s) coordinates.
    *   Returns:
        *   `Hex`: A new `Hex` object representing the sum.
    *   Raises:
        *   `TypeError`: If `other` is neither `Hex` nor `tuple`.
        *   `ValueError`: If tuple does not have exactly 3 integer coordinates or if direction coordinates are not integers.

*   `__sub__(self, other: Hex) -> Hex`: Subtracts one hex from another.

    *   Args:
        *   `other` (Hex): A `Hex` object to subtract.
    *   Returns:
        *   `Hex`: A new `Hex` object representing the difference.
    *   Raises:
        *   `TypeError`: If `other` is not a `Hex` object.

*   `__abs__(self) -> int`: Calculates the Manhattan distance from the origin to this hex.

    *   Returns:
        *   `int`: The distance in hex steps.

*   `normalize(self) -> Hex`: Normalizes the hex vector to its smallest equivalent direction.

    *   Returns:
        *   `Hex`: A new `Hex` with the same direction but minimal coordinates. Returns (0, 0, 0) for the zero vector.
    *   Raises:
        *   `ValueError`: If coordinates are not valid integers.

*   `__repr__(self) -> str`: Returns a string representation of the `Hex` object.

    *   Returns:
        *   `str`: A string representation.

### `Piece`

Represents a chess piece.

**Attributes:**

*   `type` (Literal["P", "R", "N", "B", "Q", "K"]): The piece type.
*   `color` (Literal["white", "black"]): The piece color.
*   `position` (`Hex`): The piece's current position on the board.
*   `has_moved` (bool): Whether the piece has moved (used for special moves like castling and pawn double moves).

**Methods:**

*   `move(self, new_position: Hex) -> Piece`: Creates a new `Piece` at the new position with `has_moved=True`.

    *   Args:
        *   `new_position` (`Hex`): The new position for the piece.
    *   Returns:
        *   `Piece`: A new `Piece` instance at the new position with `has_moved=True`.
    *   Note: Since the class is frozen, this method returns a new instance instead of modifying the existing one.

*   `__str__(self) -> str`: Returns the piece's string representation (e.g., "wP" for white pawn).

    *   Returns:
        *   `str`: The string representation.

### `Board`

Manages game state and board representation.

**Attributes:**

*   `board` (Dict[`Hex`, `Piece`]): A dictionary mapping `Hex` objects to `Piece` objects.
*   `current_player` (str): The current player's color ("white" or "black").
*   `BOARD_RADIUS` (int): The radius of the board.

**Methods:**

*   `__init__(self)`: Initializes the board and sets up the initial game state.
*   `setup_board(self)`: Sets up the initial board configuration (Gliński's setup).
*   `is_valid_hex(self, hex: Hex) -> bool`: Checks if a given `Hex` is within the board boundaries.

    *   Args:
        *   `hex` (`Hex`): The `Hex` to check.
    *   Returns:
        *   `bool`: `True` if the hex is valid, `False` otherwise.

*   `is_occupied(self, hex: Hex) -> bool`: Checks if a given `Hex` is occupied by a piece.

    *   Args:
        *   `hex` (`Hex`): The `Hex` to check.
    *   Returns:
        *   `bool`: `True` if the hex is occupied, `False` otherwise.

*   `get_piece(self, hex: Hex) -> Optional[Piece]`: Returns the piece at a given `Hex`, or `None` if the hex is empty.

    *   Args:
        *   `hex` (`Hex`): The `Hex` to retrieve the piece from.
    *   Returns:
        *   `Optional[Piece]`: The `Piece` object at the given hex, or `None`.

*   `move_piece(self, start_hex: Hex, end_hex: Hex) -> None`: Moves a piece from one `Hex` to another.

    *   Args:
        *   `start_hex` (`Hex`): The starting `Hex`.
        *   `end_hex` (`Hex`): The destination `Hex`.

*   `get_possible_moves(self, hex: Hex) -> Set[Hex]`: Returns a set of legal moves for the piece at the given `Hex`.

    *   Args:
        *   `hex` (`Hex`): The `Hex` to get possible moves for.
    *   Returns:
        *   `Set[Hex]`: A set of legal move `Hex` objects.

*   `is_check(self, color: str) -> bool`: Checks if the given color's king is in check.

    *   Args:
        *   `color` (str): The color to check ("white" or "black").
    *   Returns:
        *   `bool`: True if the king is in check, False otherwise.

*   `is_checkmate(self, color: str) -> bool`: Checks if the given color is checkmated.

    *   Args:
        *   `color` (str): The color to check ("white" or "black").
    *   Returns:
        *   `bool`: True if the color is checkmated, False otherwise.

*   `display(self, use_unicode: bool = True, use_colors: bool = True) -> str`: Returns a formatted string representation of the board.

    *   Args:
        *   `use_unicode` (bool): Whether to use Unicode chess symbols.
        *   `use_colors` (bool): Whether to use ANSI colors in terminal output.
    *   Returns:
        *   `str`: The formatted string representation of the board.

*   `__str__(self) -> str`: Returns a formatted string representation of the board.

    *   Returns:
        *   `str`: The formatted string representation of the board.

## Thinking in HEX

### Challenges of Hexagonal Grids

1. **Multiple Coordinate Systems**: There are several ways to represent hexagonal grids (axial/cubic, flat-topped/pointy-topped, offset coordinates). This variety can be confusing when switching between different resources or implementations.

2. **Direction and Movement**: The distinction between direction (a unit vector) and movement (which can involve multiple steps) is crucial and easy to mix up.

3. **Diagonal Movement**: Diagonal movement is different than in square grids. There are three sets of parallel "diagonal" lines, not just two.

4. **Distance Calculation**: Calculating distances between hexes is different. Euclidean distance doesn't work directly; you need to use specific hexagonal distance formulas based on the chosen coordinate system.

5. **Visual Representation**: Representing a hexagonal grid on a square screen or in text can be challenging. It often involves compromises that can obscure the true hexagonal nature of the grid.

### Strategies for Thinking About Hexagonal Grids

1. **Focus on the Geometry**: Visualize the hexagons themselves. Think about how they connect and the relationships between adjacent hexes.

2. **Choose a Consistent Coordinate System**: Stick to one coordinate system (e.g., cubic coordinates) throughout your implementation. This avoids confusion when converting between different representations.

3. **Distinguish Direction and Movement**: Be very clear about the difference between a direction vector (a unit vector representing a single step) and a movement (which can be multiple steps in a given direction).

4. **Use Diagrams**: Draw diagrams! Visualizing the grid and the movements of pieces can be incredibly helpful for understanding the logic.

5. **Break Down Complex Movements**: Decompose complex movements (like the bishop's two-hex jump) into sequences of single-step movements. This can help you understand how the unit vectors relate to the overall movement.

6. **Test Thoroughly**: Test your code with various scenarios, especially edge cases and situations that might be counterintuitive. This helps uncover errors early on.

### Specific to Bishop Movement

Remember these key points:

1. The bishop moves two hexes along a diagonal.
2. The direction of that movement is represented by a unit vector.
3. In `is_check()`, we're checking for attacks along a line using the precomputed bishop directions.
4. In `get_possible_moves()`, we're generating actual moves, so we simulate the two-hex jump by repeatedly adding the unit vector.

