
from constants import *

class MoveHistory:
    
    def __init__(self):
        self.moves = []
        
    def add_move(self, move_notation, color):
        self.moves.append((move_notation, color))
        
    def get_move_count(self):
        return len(self.moves)
        
    def get_last_move(self):
        if self.moves:
            return self.moves[-1]
        return None
        
    def clear(self):
        self.moves = []
        
    def get_moves_for_color(self, color):
        # return moves only for the specified color
        return [move for (move, move_color) in self.moves if move_color == color]
        
    def get_move_pair(self, move_number):
        # return the (white_move, black_move) tuple for the given 1-based move_number
        pairs = self.get_move_pairs()
        if 1 <= move_number <= len(pairs):
            return pairs[move_number - 1]
        return None, None

    def get_move_pairs(self):
        """Return a list of (white_move, black_move) tuples in order."""
        pairs = []
        white = None
        black = None
        for move, color in self.moves:
            if color == WHITE:
                if white is not None:
                    # consecutive white move (shouldn't normally happen) -> flush previous
                    pairs.append((white, black))
                    black = None
                white = move
            else:
                black = move
                pairs.append((white, black))
                white = None
                black = None

        # if there's a trailing white move without a black response
        if white is not None:
            pairs.append((white, None))

        return pairs
        
    def export_pgn(self):
        pgn_moves = []
        move_number = 1
        for white_move, black_move in self.get_move_pairs():
            if white_move and black_move:
                pgn_moves.append(f"{move_number}. {white_move} {black_move}")
            elif white_move:
                pgn_moves.append(f"{move_number}. {white_move}")
            move_number += 1
            
        return " ".join(pgn_moves)
        
    def is_empty(self):
        return len(self.moves) == 0
