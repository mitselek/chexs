from dataclasses import dataclass, replace
from typing import Literal
from hex import Hex

@dataclass(frozen=True)
class Piece:
    """
    Represents an immutable chess piece.
    
    Attributes:
        type: The piece type (P=pawn, R=rook, N=knight, B=bishop, Q=queen, K=king)
        color: The piece color (white or black)
        position: Current position on the board
        has_moved: Whether the piece has moved (for pawns and castling)
    """
    type: Literal["P", "R", "N", "B", "Q", "K"]
    color: Literal["white", "black"]
    position: Hex
    has_moved: bool = False

    def move(self, new_position: Hex) -> 'Piece':
        """Create a new piece at the new position with has_moved=True.
        
        Args:
            new_position: The new position for the piece
            
        Returns:
            A new Piece instance at the new position with has_moved=True
        """
        print(f"Moving {self.color} {self.type} from {self.position} to {new_position}")
        return replace(self, position=new_position, has_moved=True)

    def __str__(self) -> str:
        """Return the piece's string representation (e.g., 'wP' for white pawn)."""
        return f"{self.color[0]}{self.type}"
