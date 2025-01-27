class Piece:
    """
    Represents a chess piece.
    """
    def __init__(self, type, color, position):
        """
        Initializes a Piece object.

        Args:
          type: The piece type (e.g., "P", "R", "N", "B", "Q", "K").
          color: The piece color ("white" or "black").
          position: A Hex object representing the piece's location.

        Raises:
            ValueError: If the type is not valid.
            ValueError: If the color is not valid.
        """
        valid_types = {"P", "R", "N", "B", "Q", "K"}
        if type not in valid_types:
          raise ValueError(f"Invalid piece type: {type}")  # More informative error message
        valid_colors = {"white", "black"}
        if color not in valid_colors:
          raise ValueError(f"Invalid piece color: {color}")  # More informative error message
        self.type = type
        self.color = color
        self.position = position
        self.has_moved = False

    def __repr__(self):
        """
        Returns a string representation of the piece.
        """
        return f"{self.color[0]}{self.type}"

    def move(self, new_position):
        """
        Moves the piece to a new position.

        Args:
            new_position: A Hex object representing the new position.
        """
        self.position = new_position
        self.has_moved = True

    def __eq__(self, other):
        """Checks if two pieces are equal."""
        if not isinstance(other, Piece):
            return False
        return (self.type == other.type and
                self.color == other.color and
                self.position == other.position)

    def __hash__(self):
        """Returns a hash value for the Piece object."""
        return hash((self.type, self.color, self.position))
