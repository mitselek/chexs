import math

class Hex:
    """
    Represents a single hexagon on the board using cubic coordinates.
    """
    def __init__(self, q, r, s):
        """
        Initializes a Hex object.

        Args:
          q: The q coordinate.
          r: The r coordinate.
          s: The s coordinate.

        Raises:
          ValueError: If q + r + s is not equal to 0.
        """
        if q + r + s != 0:
            raise ValueError("q + r + s must equal 0")
        self.q = q
        self.r = r
        self.s = s

    def __eq__(self, other):
        """
        Checks if two Hex objects are equal.

        Args:
          other: Another Hex object.

        Returns:
          True if the coordinates of both hexes are equal, False otherwise.
        """
        if not isinstance(other, Hex):
            return False  # Handle comparison with non-Hex objects
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __hash__(self):
        """
        Returns a hash value for the Hex object.

        This is necessary for using Hex objects as keys in dictionaries.
        """
        return hash((self.q, self.r, self.s))

    def to_tuple(self):
        """
        Returns the coordinates of the hex as a tuple.
        """
        return (self.q, self.r, self.s)

    def get_color(self):
        """
        Calculates and returns the color of the hex.

        Returns:
          A string representing the color of the hex.
        """
        color_index = (self.q + self.r + self.s) % 3
        colors = ["green", "blue", "red"]
        return colors[color_index]

    def __add__(self, other):
        """Add two Hex objects or a Hex and a direction tuple."""
        if isinstance(other, tuple):
            return Hex(self.q + other[0], self.r + other[1], self.s + other[2])
        if isinstance(other, Hex):
            return Hex(self.q + other.q, self.r + other.r, self.s + other.s)
        return NotImplemented # Important for correct type handling

    def __sub__(self, other):
        """Subtract two Hex objects."""
        if isinstance(other, Hex):
            return Hex(self.q - other.q, self.r - other.r, self.s - other.s)
        return NotImplemented

    def __abs__(self):
        """Returns the Manhattan distance from origin to this hex."""
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def normalize(self):
        """Returns normalized direction vector as Hex."""
        gcd = math.gcd(math.gcd(abs(self.q), abs(self.r)), abs(self.s))
        if gcd == 0:
            return Hex(0, 0, 0)
        return Hex(self.q//gcd, self.r//gcd, self.s//gcd)

    def __repr__(self):
        return f"Hex({self.q}, {self.r}, {self.s})"


# Basic hex direction vectors
hex_directions = [
    (1, 0, -1),  # NE
    (0, 1, -1),  # N
    (-1, 1, 0),  # NW
    (-1, 0, 1),  # SW
    (0, -1, 1),  # S
    (1, -1, 0)   # SE
]

def hex_distance(hex1, hex2):
    """Calculates the distance between two Hex objects."""
    return abs(hex1 - hex2)  # Now uses __abs__ and __sub__

