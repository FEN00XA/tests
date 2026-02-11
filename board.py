
from bitboard import Bitboard
from piece import Pawn, Rook, Knight, Bishop, Queen, King
from constants import *

class ChessBoard:
    
    
    def __init__(self):
        
        self.bitboard = Bitboard()
        self.pieces = {}  # Square -> Piece mapping
        self.en_passant_target = None  # En passant target square
        self.castling_rights = WHITE_KINGSIDE | WHITE_QUEENSIDE | BLACK_KINGSIDE | BLACK_QUEENSIDE
        self.set_initial_position()
        
    def set_initial_position(self):
        
        self.bitboard.set_initial_position()
        self._create_pieces()
        
    def _create_pieces(self):
    
        self.pieces = {}
        
        # White pieces (at bottom - ranks 0-1)
        for square in range(8, 16):  # Rank 1 (second rank from bottom)
            self.pieces[square] = Pawn(WHITE)
        self.pieces[0] = Rook(WHITE)      # A1
        self.pieces[1] = Knight(WHITE)    # B1
        self.pieces[2] = Bishop(WHITE)    # C1
        self.pieces[3] = Queen(WHITE)     # D1
        self.pieces[4] = King(WHITE)      # E1
        self.pieces[5] = Bishop(WHITE)    # F1
        self.pieces[6] = Knight(WHITE)    # G1
        self.pieces[7] = Rook(WHITE)      # H1
        
        # Black pieces (at top - ranks 6-7)
        for square in range(48, 56):  # Rank 6 (second rank from top)
            self.pieces[square] = Pawn(BLACK)
        self.pieces[56] = Rook(BLACK)     # A8
        self.pieces[57] = Knight(BLACK)  # B8
        self.pieces[58] = Bishop(BLACK)  # C8
        self.pieces[59] = Queen(BLACK)   # D8
        self.pieces[60] = King(BLACK)    # E8
        self.pieces[61] = Bishop(BLACK)  # F8
        self.pieces[62] = Knight(BLACK)  # G8
        self.pieces[63] = Rook(BLACK)    # H8
        
    def get_piece(self, square):
        return self.pieces.get(square)
        
    def is_square_occupied(self, square):
        return square in self.pieces
        
    def is_square_occupied_by_color(self, square, color):
        piece = self.get_piece(square)
        return piece is not None and piece.color == color
        
    def get_legal_moves(self, square):
        piece = self.get_piece(square)
        if not piece:
            return []
            
        possible_moves = piece.get_legal_moves(square, self)
        legal_moves = []
        for move in possible_moves:
            if self._is_legal_move(square, move):
                legal_moves.append(move)
                
        return legal_moves
        
    def _is_legal_move(self, from_square, to_square):
        piece = self.get_piece(from_square)
        if not piece:
            return False
            
        temp_board = self._make_temp_move(from_square, to_square)
        king_in_check = temp_board.is_king_in_check(piece.color)
        
        return not king_in_check
        
    def _make_temp_move(self, from_square, to_square):
        temp_board = ChessBoard()
        temp_board.bitboard = self.bitboard.copy()
        temp_board.pieces = self.pieces.copy()
        temp_board.en_passant_target = self.en_passant_target
        temp_board.castling_rights = self.castling_rights
        
        piece = temp_board.pieces.get(from_square)
        if piece:
            if from_square in temp_board.pieces:
                del temp_board.pieces[from_square]
            temp_board.pieces[to_square] = piece
            
        temp_board.bitboard.move_piece(from_square, to_square)
        
        return temp_board
        
    def _update_castling_rights(self, from_square, to_square, piece, captured_piece):
        if piece.type == KING:
            if piece.color == WHITE:
                self.castling_rights &= ~(WHITE_KINGSIDE | WHITE_QUEENSIDE)
            else:
                self.castling_rights &= ~(BLACK_KINGSIDE | BLACK_QUEENSIDE)

        elif piece.type == ROOK:
            if from_square == 0:  # A1
                self.castling_rights &= ~WHITE_QUEENSIDE
            elif from_square == 7:  # H1
                self.castling_rights &= ~WHITE_KINGSIDE
            elif from_square == 56:  # A8
                self.castling_rights &= ~BLACK_QUEENSIDE
            elif from_square == 63:  # H8
                self.castling_rights &= ~BLACK_KINGSIDE

        if captured_piece and captured_piece.type == ROOK:
            if to_square == 0:  # A1
                self.castling_rights &= ~WHITE_QUEENSIDE
            elif to_square == 7:  # H1
                self.castling_rights &= ~WHITE_KINGSIDE
            elif to_square == 56:  # A8
                self.castling_rights &= ~BLACK_QUEENSIDE
            elif to_square == 63:  # H8
                self.castling_rights &= ~BLACK_KINGSIDE
        
    def make_move(self, from_square, to_square):
        piece = self.get_piece(from_square)
        if not piece:
            return None
        
        target_piece = self.get_piece(to_square)
        if target_piece and target_piece.type == KING:
            return None

        if to_square not in self.get_legal_moves(from_square):
            return None
            
        captured_piece = self.get_piece(to_square)
        
        move_notation = self._get_move_notation(from_square, to_square, piece)
        
        self._handle_special_moves(from_square, to_square, piece)
        
        self.pieces[to_square] = piece
        if from_square in self.pieces:
            del self.pieces[from_square]
            
        self.bitboard.move_piece(from_square, to_square)
        
        piece.has_moved = True
        
        self._update_castling_rights(from_square, to_square, piece, captured_piece)
        
        return move_notation
        
    def _handle_special_moves(self, from_square, to_square, piece):

        if piece.type == KING and abs(to_square - from_square) == 2:
            self._handle_castling(from_square, to_square)
            
        elif (piece.type == PAWN and 
              to_square == self.bitboard.en_passant_target):
            self._handle_en_passant(from_square, to_square)
            
        if (piece.type == PAWN and 
            abs(to_square - from_square) == 16):
            self.bitboard.en_passant_target = (from_square + to_square) // 2
        else:
            self.bitboard.en_passant_target = None
            
    def _handle_castling(self, from_square, to_square):
        """Handle castling moves."""
        if to_square > from_square:  # Kingside
            rook_from = to_square + 1
            rook_to = to_square - 1
        else:  # Queenside
            rook_from = to_square - 2
            rook_to = to_square + 1
            
        rook = self.pieces.get(rook_from)
        if rook:
            self.pieces[rook_to] = rook
            del self.pieces[rook_from]
            self.bitboard.move_piece(rook_from, rook_to)
            
    def _handle_en_passant(self, from_square, to_square):
        captured_square = to_square + (8 if self.get_piece(from_square).color == WHITE else -8)
        if captured_square in self.pieces:
            del self.pieces[captured_square]
            self.bitboard.clear_square(captured_square)
            
    def promote_pawn(self, square, piece_type):
        piece = self.get_piece(square)
        if piece and piece.type == PAWN:
            color = piece.color
            if piece_type == QUEEN:
                self.pieces[square] = Queen(color)
            elif piece_type == ROOK:
                self.pieces[square] = Rook(color)
            elif piece_type == BISHOP:
                self.pieces[square] = Bishop(color)
            elif piece_type == KNIGHT:
                self.pieces[square] = Knight(color)
                
            self.bitboard.clear_square(square)
            self.bitboard.set_piece(square, color, piece_type)
            
    def is_checkmate(self, color):
        if not self.bitboard.is_king_in_check(color):
            return False
            
        for square in range(64):
            piece = self.get_piece(square)
            if piece and piece.color == color:
                if self.get_legal_moves(square):
                    return False
                    
        return True
        
    def is_stalemate(self, color):
        if self.bitboard.is_king_in_check(color):
            return False
            
        for square in range(64):
            piece = self.get_piece(square)
            if piece and piece.color == color:
                if self.get_legal_moves(square):
                    return False
                    
        return True
        
    def is_king_in_check(self, color):
        king_square = None
        for square in range(64):
            piece = self.get_piece(square)
            if piece and piece.color == color and piece.type == KING:
                king_square = square
                break
                
        if king_square is None:
            return False
            
        enemy_color = BLACK if color == WHITE else WHITE
        return self._square_under_attack(king_square, enemy_color)
        
    def _square_under_attack(self, square, attacking_color):
        for piece_square in range(64):
            piece = self.get_piece(piece_square)
            if piece and piece.color == attacking_color:
                legal_moves = piece.get_legal_moves(piece_square, self)
                if square in legal_moves:
                    return True
        return False
        
    def _get_move_notation(self, from_square, to_square, piece):
        from_file = FILES[from_square % 8]
        # square // 8 gives rank index where 0 is rank 1 (bottom), so add 1
        from_rank = str((from_square // 8) + 1)
        to_file = FILES[to_square % 8]
        to_rank = str((to_square // 8) + 1)
        
        if piece.type == PAWN:
            notation = f"{to_file}{to_rank}"
        else:
            notation = f"{piece.get_symbol()}{to_file}{to_rank}"
            
        if self.bitboard.is_king_in_check(BLACK if piece.color == WHITE else WHITE):
            notation += "+"
            
        return notation
        
    def reset(self):
        self.bitboard = Bitboard()
        self.bitboard.set_initial_position()
        self.en_passant_target = None
        self.castling_rights = WHITE_KINGSIDE | WHITE_QUEENSIDE | BLACK_KINGSIDE | BLACK_QUEENSIDE
        self._create_pieces()
