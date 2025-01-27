# hex.py
"""
Provides classes and functions for representing and manipulating hexagonal coordinates.
"""

import math

class Hex:
    """
    Represents a hexagonal coordinate using axial coordinates (q, r).

    Attributes:
        q (int): The q coordinate.
        r (int): The r coordinate.
    """
    def __init__(self, q, r, s):
        """Initialize a hex with cubic coordinates.

        Args:
            q: The q coordinate
            r: The r coordinate
            s: The s coordinate
        """
        if not self.is_valid_cubic_coordinates(q, r, s):
            raise ValueError(f"Invalid cubic coordinates: {q}+{r}+{s}≠0")
        self.q = q
        self.r = r
        self.s = s

    @staticmethod
    def is_valid_cubic_coordinates(q: int, r: int, s: int) -> bool:
        """Check if coordinates satisfy the cubic coordinate constraint q + r + s = 0.
        
        Args:
            q: The q coordinate
            r: The r coordinate
            s: The s coordinate
            
        Returns:
            bool: True if coordinates are valid
        """
        return q + r + s == 0

    @staticmethod
    def is_within_radius(q: int, r: int, s: int, radius: int) -> bool:
        """Check if coordinates are within given radius from origin.
        
        Args:
            q: The q coordinate
            r: The r coordinate
            s: The s coordinate
            radius: The maximum allowed distance from origin
            
        Returns:
            bool: True if coordinates are within radius
        """
        return max(abs(q), abs(r), abs(s)) <= radius

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
        """Calculates and returns the color of the hex.
        
        Returns:
            str: A string representing the color of the hex ("green", "blue", or "red").
            
        Raises:
            ValueError: If coordinates are not valid integers.
        """
        try:
            color_index = (int(self.q) + int(self.r) + int(self.s)) % 3
            colors = ["green", "blue", "red"]
            return colors[color_index]
        except (TypeError, ValueError):
            raise ValueError("Coordinates must be valid integers")

    def __add__(self, other):
        """Add a hex to another hex or direction tuple.
        
        Args:
            other: Either a Hex object or a tuple of (q, r, s) coordinates

        Returns:
            Hex: A new hex representing the sum
            
        Raises:
            TypeError: If other is neither Hex nor tuple
            ValueError: If tuple does not have exactly 3 integer coordinates
        """
        if isinstance(other, tuple):
            if len(other) != 3:
                raise ValueError("Direction tuple must have exactly 3 coordinates")
            try:
                return Hex(self.q + int(other[0]), 
                         self.r + int(other[1]), 
                         self.s + int(other[2]))
            except (TypeError, ValueError):
                raise ValueError("Direction coordinates must be integers")
        if isinstance(other, Hex):
            return Hex(self.q + other.q, self.r + other.r, self.s + other.s)
        raise TypeError(f"Cannot add Hex and {type(other).__name__}")

    def __sub__(self, other):
        """Subtract one hex from another.
        
        Args:
            other: A Hex object to subtract

        Returns:
            Hex: A new hex representing the difference
            
        Raises:
            TypeError: If other is not a Hex object
        """
        if isinstance(other, Hex):
            return Hex(self.q - other.q, self.r - other.r, self.s - other.s)
        return NotImplemented

    def __abs__(self):
        """Calculate the Manhattan distance from origin to this hex.
        
        Returns:
            int: The distance in hex steps
        """
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def normalize(self):
        """Normalize the hex vector to its smallest equivalent direction.
        
        Returns:
            Hex: A new hex with same direction but minimal coordinates.
            
        Raises:
            ValueError: If coordinates are not valid integers.
        """
        try:
            coordinates = [abs(int(self.q)), abs(int(self.r)), abs(int(self.s))]
            gcd = math.gcd(math.gcd(coordinates[0], coordinates[1]), coordinates[2])
            if gcd == 0:
                return Hex(0, 0, 0)
            return Hex(self.q//gcd, self.r//gcd, self.s//gcd)
        except (TypeError, ValueError):
            raise ValueError("Coordinates must be valid integers")

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
    """Calculate the distance between two hex positions.
    
    Args:
        hex1: First hex position
        hex2: Second hex position
        
    Returns:
        int: The number of steps from hex1 to hex2
        
    Raises:
        TypeError: If either argument is not a Hex object
    """
    if not isinstance(hex1, Hex) or not isinstance(hex2, Hex):
        raise TypeError("Both arguments must be Hex objects")
    return abs(hex1 - hex2)

