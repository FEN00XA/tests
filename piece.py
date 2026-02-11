
from constants import *

try:
    import pygame
    PYGAME_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Pygame not available: {e}")
    PYGAME_AVAILABLE = False

class Piece:
    
    def __init__(self, color, piece_type):

        self.color = color
        self.type = piece_type
        self.has_moved = False
        
    def get_symbol(self):
        return PIECE_SYMBOLS[self.color][self.type]
        
    def get_image_path(self):
        color_name = "white" if self.color == WHITE else "black"
        piece_names = {PAWN: "pawn", ROOK: "rook", KNIGHT: "knight", 
                      BISHOP: "bishop", QUEEN: "queen", KING: "king"}
        return f"assets/pieces/{color_name}_{piece_names[self.type]}.png"        
            
    def get_legal_moves(self, square, board):
        return []

class Pawn(Piece):
    
    def __init__(self, color):
        super().__init__(color, PAWN)
        
    def get_legal_moves(self, square, board):
        moves = []
        file, rank = square % 8, square // 8
        
        direction = 1 if self.color == WHITE else -1
        start_rank = 1 if self.color == WHITE else 6
        
        new_rank = rank + direction
        if 0 <= new_rank <= 7:
            forward_square = new_rank * 8 + file
            if not board.is_square_occupied(forward_square):
                moves.append(forward_square)
                
                if rank == start_rank:
                    new_rank = rank + 2 * direction
                    if 0 <= new_rank <= 7:
                        double_square = new_rank * 8 + file
                        if not board.is_square_occupied(double_square):
                            moves.append(double_square)
                            
        for file_offset in [-1, 1]:
            new_file = file + file_offset
            if 0 <= new_file <= 7:
                new_rank = rank + direction
                if 0 <= new_rank <= 7:
                    capture_square = new_rank * 8 + new_file
                    if (board.is_square_occupied_by_color(capture_square, 
                                                         BLACK if self.color == WHITE else WHITE)):
                        moves.append(capture_square)
                        
        if board.en_passant_target is not None:
            ep_file, ep_rank = board.en_passant_target % 8, board.en_passant_target // 8
            if abs(file - ep_file) == 1 and rank == (4 if self.color == WHITE else 3):
                moves.append(board.en_passant_target)
                
        return moves

class Rook(Piece):
    
    def __init__(self, color):
        super().__init__(color, ROOK)
        
    def get_legal_moves(self, square, board):
        moves = []
        file, rank = square % 8, square // 8
        
        for direction in [-1, 1]:
            for i in range(1, 8):
                new_file = file + direction * i
                if not (0 <= new_file <= 7):
                    break
                new_square = rank * 8 + new_file
                if board.is_square_occupied(new_square):
                    if board.is_square_occupied_by_color(new_square, 
                                                       BLACK if self.color == WHITE else WHITE):
                        moves.append(new_square)
                    break
                moves.append(new_square)
                
        for direction in [-1, 1]:
            for i in range(1, 8):
                new_rank = rank + direction * i
                if not (0 <= new_rank <= 7):
                    break
                new_square = new_rank * 8 + file
                if board.is_square_occupied(new_square):
                    if board.is_square_occupied_by_color(new_square, 
                                                       BLACK if self.color == WHITE else WHITE):
                        moves.append(new_square)
                    break
                moves.append(new_square)
                
        return moves

class Knight(Piece):
    
    def __init__(self, color):
        super().__init__(color, KNIGHT)
        
    def get_legal_moves(self, square, board):
        moves = []
        file, rank = square % 8, square // 8
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
                       
        for file_offset, rank_offset in knight_moves:
            new_file = file + file_offset
            new_rank = rank + rank_offset
            
            if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                new_square = new_rank * 8 + new_file
                if not board.is_square_occupied_by_color(new_square, self.color):
                    moves.append(new_square)
                    
        return moves

class Bishop(Piece):
    
    def __init__(self, color):
        super().__init__(color, BISHOP)
        
    def get_legal_moves(self, square, board):
        moves = []
        file, rank = square % 8, square // 8
        
        for file_dir in [-1, 1]:
            for rank_dir in [-1, 1]:
                for i in range(1, 8):
                    new_file = file + file_dir * i
                    new_rank = rank + rank_dir * i
                    
                    if not (0 <= new_file <= 7 and 0 <= new_rank <= 7):
                        break
                        
                    new_square = new_rank * 8 + new_file
                    if board.is_square_occupied(new_square):
                        if board.is_square_occupied_by_color(new_square, 
                                                           BLACK if self.color == WHITE else WHITE):
                            moves.append(new_square)
                        break
                    moves.append(new_square)
                    
        return moves

class Queen(Piece):
    
    def __init__(self, color):
        super().__init__(color, QUEEN)
        
    def get_legal_moves(self, square, board):
        rook = Rook(self.color)
        bishop = Bishop(self.color)
        return rook.get_legal_moves(square, board) + bishop.get_legal_moves(square, board)

class King(Piece):
    
    def __init__(self, color):
        super().__init__(color, KING)
        
    def get_legal_moves(self, square, board):
        moves = []
        file, rank = square % 8, square // 8
        
        for file_offset in [-1, 0, 1]:
            for rank_offset in [-1, 0, 1]:
                if file_offset == 0 and rank_offset == 0:
                    continue
                    
                new_file = file + file_offset
                new_rank = rank + rank_offset
                
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    new_square = new_rank * 8 + new_file
                    if not board.is_square_occupied_by_color(new_square, self.color):
                        moves.append(new_square)
                        
        moves.extend(self._get_castling_moves(square, board))
        
        return moves
        
    def _get_castling_moves(self, square, board):
        moves = []
        
        if self.has_moved:
            return moves
            
        if self.color == WHITE and (board.castling_rights & WHITE_KINGSIDE):
            if (not board.is_square_occupied(5) and 
                not board.is_square_occupied(6) and
                not board._square_under_attack(5, BLACK) and
                not board._square_under_attack(6, BLACK)):
                moves.append(6)
                
        if self.color == WHITE and (board.castling_rights & WHITE_QUEENSIDE):
            if (not board.is_square_occupied(1) and 
                not board.is_square_occupied(2) and
                not board.is_square_occupied(3) and
                not board._square_under_attack(2, BLACK) and
                not board._square_under_attack(3, BLACK)):
                moves.append(2)
                
        if self.color == BLACK and (board.castling_rights & BLACK_KINGSIDE):
            if (not board.is_square_occupied(61) and 
                not board.is_square_occupied(62) and
                not board._square_under_attack(61, WHITE) and
                not board._square_under_attack(62, WHITE)):
                moves.append(62)
                
        if self.color == BLACK and (board.castling_rights & BLACK_QUEENSIDE):
            if (not board.is_square_occupied(57) and 
                not board.is_square_occupied(58) and
                not board.is_square_occupied(59) and
                not board._square_under_attack(58, WHITE) and
                not board._square_under_attack(59, WHITE)):
                moves.append(58)
                
        return moves
