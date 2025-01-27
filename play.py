# -*- coding: utf-8 -*-
# play.py

from board import Board
from hex import Hex
import random


def get_random_valid_moves(board, num_moves=5):
    """Get a list of random valid moves from the current board state."""
    valid_moves = []
    for hex, piece in board.board.items():
        if piece.color == board.current_player:
            possible_moves = board.get_possible_moves(hex)
            for move in possible_moves:
                valid_moves.append((piece, hex, move))
    return random.sample(valid_moves, min(num_moves, len(valid_moves)))

def play_game(board):
    """Plays a game of hexagonal chess."""
    while True:
        print(board.display())  # Display the board
        print(board.get_turn_info()) # Display turn info
        
        try:
            # Get random valid moves for example
            examples = get_random_valid_moves(board)
            example_moves = " | ".join([f"{piece.type} ({start.q},{start.r},{start.s} {end.q},{end.r},{end.s})" for piece, start, end in examples])
            print(f"Example moves: {example_moves}")

            # Get user input for move
            move_input = input("Enter your move (e.g., '0,-1,1 1,-2,1'): ").strip()
            start_str, end_str = move_input.split()
            start_q, start_r, start_s = map(int, start_str.split(','))
            end_q, end_r, end_s = map(int, end_str.split(','))
            start_hex = Hex(start_q, start_r, start_s)
            end_hex = Hex(end_q, end_r, end_s)

            # Move the piece
            board.move_piece(start_hex, end_hex)
            
            # Check for checkmate
            if board.is_checkmate(board.current_player):
                winner = "black" if board.current_player == "white" else "white"
                print(board.display())  # Display the final board
                print(f"Checkmate! {winner} wins!")
                break
            
            # Check for check
            if board.is_check(board.current_player):
                print("Check!")

        except ValueError as e:
            print(f"Invalid input: {e}")
        except EOFError: #handle ctrl+d
            print("Exiting game")
            break
        except KeyboardInterrupt: #handle ctrl+c
            print("Exiting game")
            break

def main():
    # Create the board
    board = Board()
    
    # Play the game
    play_game(board)

if __name__ == "__main__":
    main()