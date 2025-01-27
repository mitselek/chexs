# -*- coding: utf-8 -*-
from board import Board

def main():
    # Create and display the board
    board = Board()
    
    print("\nGliński's Hexagonal Chess")
    print("------------------------")
    print("\nDefault display (Unicode + Colors):")
    print(board.display())
    
    print("\nASCII display:")
    print(board.display(use_unicode=False, use_colors=False))
    
    print("\nWith coordinates:")
    print(board.display(show_coords=True))

if __name__ == "__main__":
    main()
