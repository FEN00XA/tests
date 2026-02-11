
from constants import *

class Bitboard:
    
    def __init__(self):
        self.boards = {
            WHITE: {
                PAWN: 0,
                ROOK: 0,
                KNIGHT: 0,
                BISHOP: 0,
                QUEEN: 0,
                KING: 0
            },
            BLACK: {
                PAWN: 0,
                ROOK: 0,
                KNIGHT: 0,
                BISHOP: 0,
                QUEEN: 0,
                KING: 0
            }
        }
        
        # Combined boards 
        self.white_pieces = 0
        self.black_pieces = 0
        self.all_pieces = 0
        
        # Castling rights
        self.castling_rights = 0
        
        # En passant target square
        self.en_passant_target = None
        
        # Halfmove and fullmove counters
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
    def set_initial_position(self):

        self.boards[WHITE][PAWN] = RANK_2
        self.boards[WHITE][ROOK] = (1 << A1) | (1 << H1)
        self.boards[WHITE][KNIGHT] = (1 << B1) | (1 << G1)
        self.boards[WHITE][BISHOP] = (1 << C1) | (1 << F1)
        self.boards[WHITE][QUEEN] = 1 << D1
        self.boards[WHITE][KING] = 1 << E1
        
        self.boards[BLACK][PAWN] = RANK_7
        self.boards[BLACK][ROOK] = (1 << A8) | (1 << H8)
        self.boards[BLACK][KNIGHT] = (1 << B8) | (1 << G8)
        self.boards[BLACK][BISHOP] = (1 << C8) | (1 << F8)
        self.boards[BLACK][QUEEN] = 1 << D8
        self.boards[BLACK][KING] = 1 << E8
        
        self._update_combined_boards()
        
        self.castling_rights = WHITE_KINGSIDE | WHITE_QUEENSIDE | BLACK_KINGSIDE | BLACK_QUEENSIDE
        
    def _update_combined_boards(self):
        self.white_pieces = 0
        self.black_pieces = 0
        
        for piece_type in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]:
            self.white_pieces |= self.boards[WHITE][piece_type]
            self.black_pieces |= self.boards[BLACK][piece_type]
            
        self.all_pieces = self.white_pieces | self.black_pieces
        
    def get_piece_at_square(self, square):
        square_bit = 1 << square
        
        for color in [WHITE, BLACK]:
            for piece_type in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]:
                if self.boards[color][piece_type] & square_bit:
                    return (color, piece_type)
        return None
        
    def set_piece(self, square, color, piece_type):
        square_bit = 1 << square
        
        self.clear_square(square)
        
        self.boards[color][piece_type] |= square_bit
        self._update_combined_boards()
        
    def clear_square(self, square):
        square_bit = 1 << square
        
        for color in [WHITE, BLACK]:
            for piece_type in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]:
                self.boards[color][piece_type] &= ~square_bit
                
        self._update_combined_boards()
        
    def move_piece(self, from_square, to_square):
        piece = self.get_piece_at_square(from_square)
        if piece:
            color, piece_type = piece
            self.clear_square(from_square)
            self.set_piece(to_square, color, piece_type)
            return True
        return False
        
    def is_square_occupied(self, square):
        square_bit = 1 << square
        return bool(self.all_pieces & square_bit)
        
    def is_square_occupied_by_color(self, square, color):
        square_bit = 1 << square
        pieces = self.white_pieces if color == WHITE else self.black_pieces
        return bool(pieces & square_bit)
        
    def get_attacks_to_square(self, square, attacking_color):
        attacks = []
        square_bit = 1 << square
        
        for piece_type in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]:
            if self.boards[attacking_color][piece_type] & square_bit:
                attacks.append((piece_type, square))
                
        return attacks
        
    def is_king_in_check(self, color):
        king_square = None
        for square in range(64):
            piece = self.get_piece_at_square(square)
            if piece and piece == (color, KING):
                king_square = square
                break
                
        if king_square is None:
            return False
            
        enemy_color = BLACK if color == WHITE else WHITE
        return self._square_under_attack(king_square, enemy_color)
        
    def _square_under_attack(self, square, attacking_color):
        return (self._pawn_attacks_square(square, attacking_color) or
                self._rook_attacks_square(square, attacking_color) or
                self._bishop_attacks_square(square, attacking_color) or
                self._queen_attacks_square(square, attacking_color) or
                self._knight_attacks_square(square, attacking_color) or
                self._king_attacks_square(square, attacking_color))
               
    def _pawn_attacks_square(self, square, attacking_color):
        square_bit = 1 << square
        pawn_board = self.boards[attacking_color][PAWN]
        
        if attacking_color == WHITE:
            attacks = ((pawn_board & ~FILE_A) << 7) | ((pawn_board & ~FILE_H) << 9)
        else:
            attacks = ((pawn_board & ~FILE_A) >> 9) | ((pawn_board & ~FILE_H) >> 7)
            
        return bool(attacks & square_bit)
        
    def _king_attacks_square(self, square, attacking_color):
        king_board = self.boards[attacking_color][KING]
        if not king_board:
            return False
            
        king_square = self._bit_scan_forward(king_board)
        if king_square is None:
            return False
            
        king_attacks = self._get_king_attacks(king_square)
        return bool(king_attacks & (1 << square))
        
    def _get_king_attacks(self, square):
        attacks = 0
        
        if square % 8 > 0:  # Not on A file
            attacks |= 1 << (square - 1)
        if square % 8 < 7:  # Not on H file
            attacks |= 1 << (square + 1)
        if square >= 8:     # Not on rank 1
            attacks |= 1 << (square - 8)
        if square < 56:     # Not on rank 8
            attacks |= 1 << (square + 8)
            
        if square % 8 > 0 and square >= 8:  # Not on A file or rank 1
            attacks |= 1 << (square - 9)
        if square % 8 < 7 and square >= 8:  # Not on H file or rank 1
            attacks |= 1 << (square - 7)
        if square % 8 > 0 and square < 56:  # Not on A file or rank 8
            attacks |= 1 << (square + 7)
        if square % 8 < 7 and square < 56:  # Not on H file or rank 8
            attacks |= 1 << (square + 9)
            
        return attacks
        
    def _rook_attacks_square(self, square, attacking_color):
        rook_board = self.boards[attacking_color][ROOK]
        if not rook_board:
            return False
            
        file, rank = square % 8, square // 8
        
        for i in range(8):
            if i != file:
                test_square = rank * 8 + i
                if (rook_board & (1 << test_square)) and self._clear_path_between(test_square, square):
                    return True
                    
        for i in range(8):
            if i != rank:
                test_square = i * 8 + file
                if (rook_board & (1 << test_square)) and self._clear_path_between(test_square, square):
                    return True
                    
        return False
        
    def _bishop_attacks_square(self, square, attacking_color):
        bishop_board = self.boards[attacking_color][BISHOP]
        if not bishop_board:
            return False
            
        file, rank = square % 8, square // 8
        
        for file_dir in [-1, 1]:
            for rank_dir in [-1, 1]:
                for i in range(1, 8):
                    test_file = file + file_dir * i
                    test_rank = rank + rank_dir * i
                    
                    if 0 <= test_file <= 7 and 0 <= test_rank <= 7:
                        test_square = test_rank * 8 + test_file
                        if (bishop_board & (1 << test_square)) and self._clear_path_between(test_square, square):
                            return True
                    else:
                        break
                        
        return False
        
    def _queen_attacks_square(self, square, attacking_color):
        queen_board = self.boards[attacking_color][QUEEN]
        if not queen_board:
            return False
            
        return (self._rook_attacks_square(square, attacking_color) or 
                self._bishop_attacks_square(square, attacking_color))
                
    def _knight_attacks_square(self, square, attacking_color):
        knight_board = self.boards[attacking_color][KNIGHT]
        if not knight_board:
            return False
            
        file, rank = square % 8, square // 8
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
                       
        for file_offset, rank_offset in knight_moves:
            test_file = file + file_offset
            test_rank = rank + rank_offset
            
            if 0 <= test_file <= 7 and 0 <= test_rank <= 7:
                test_square = test_rank * 8 + test_file
                if knight_board & (1 << test_square):
                    return True
                    
        return False
        
    def _clear_path_between(self, from_square, to_square):
        from_file, from_rank = from_square % 8, from_square // 8
        to_file, to_rank = to_square % 8, to_square // 8
        
        file_dir = 1 if to_file > from_file else -1 if to_file < from_file else 0
        rank_dir = 1 if to_rank > from_rank else -1 if to_rank < from_rank else 0
        
        current_file, current_rank = from_file + file_dir, from_rank + rank_dir
        while (current_file != to_file or current_rank != to_rank):
            if current_file < 0 or current_file > 7 or current_rank < 0 or current_rank > 7:
                return False
                
            current_square = current_rank * 8 + current_file
            if self.all_pieces & (1 << current_square):
                return False
                
            current_file += file_dir
            current_rank += rank_dir
            
        return True
        
    def _bit_scan_forward(self, bb):
        if bb == 0:
            return None
        return (bb & -bb).bit_length() - 1
        
    def get_all_pieces_of_color(self, color):
        pieces = []
        for square in range(64):
            piece = self.get_piece_at_square(square)
            if piece and piece[0] == color:
                pieces.append((square, piece[1]))
        return pieces
        
    def copy(self):
        new_bb = Bitboard()
        new_bb.boards = {
            WHITE: {pt: self.boards[WHITE][pt] for pt in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]},
            BLACK: {pt: self.boards[BLACK][pt] for pt in [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]}
        }
        new_bb.white_pieces = self.white_pieces
        new_bb.black_pieces = self.black_pieces
        new_bb.all_pieces = self.all_pieces
        new_bb.castling_rights = self.castling_rights
        new_bb.en_passant_target = self.en_passant_target
        new_bb.halfmove_clock = self.halfmove_clock
        new_bb.fullmove_number = self.fullmove_number
        return new_bb
