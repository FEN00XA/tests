
import pygame
from board import ChessBoard
from ui import GameUI
from move_history import MoveHistory
from constants import *

class ChessGame:

    
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Chess")
            print(f" Game window created: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        except Exception as e:
            print(f" Failed to create game window: {e}")
            raise
        
        self.board = ChessBoard()
        self.ui = GameUI()
        self.move_history = MoveHistory()
        
        self.current_player = WHITE
        self.game_over = False
        self.winner = None
        self.game_result = None 
        
        self.dragging = False
        self.dragged_piece = None
        self.dragged_square = None
        self.legal_moves = []
        
        self.reset_pressed = False
        self.reset_timer = 0
        

        self.promotion_active = False
        self.promotion_square = None
        
    def handle_event(self, event):
        if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset_game()
            return
            
        if self.promotion_active:
            self._handle_promotion_event(event)
            return
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.reset_pressed:
                self.reset_game()
            else:
                self.reset_pressed = True
                self.reset_timer = pygame.time.get_ticks()
        elif event.type == pygame.KEYUP and event.key == pygame.K_r:
            self.reset_pressed = False
            
        if self.game_over:
            return
            
        if event.type == pygame.MOUSEWHEEL:
            # Modern pygame wheel event
            mx, my = pygame.mouse.get_pos()
            if (HISTORY_X <= mx <= HISTORY_X + HISTORY_WIDTH and
                HISTORY_Y <= my <= HISTORY_Y + HISTORY_HEIGHT):
                pairs = self.move_history.get_move_pairs()
                max_rows = max(1, (HISTORY_HEIGHT - 80) // 28)
                self.ui.scroll_history(event.y, total_rows=len(pairs), max_rows=max_rows)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            # Older pygame mouse wheel emulation (button 4 = up, 5 = down)
            mx, my = pygame.mouse.get_pos()
            if (HISTORY_X <= mx <= HISTORY_X + HISTORY_WIDTH and
                HISTORY_Y <= my <= HISTORY_Y + HISTORY_HEIGHT):
                delta = 1 if event.button == 4 else -1
                pairs = self.move_history.get_move_pairs()
                max_rows = max(1, (HISTORY_HEIGHT - 80) // 28)
                self.ui.scroll_history(delta, total_rows=len(pairs), max_rows=max_rows)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
            
    def _handle_mouse_down(self, event):
        if self.dragging:
            return
            
        pos = pygame.mouse.get_pos()
        square = self.ui.get_square_from_pos(pos)
        
        if square is not None:
            piece = self.board.get_piece(square)
            if piece and piece.color == self.current_player:
                self.dragging = True
                self.dragged_piece = piece
                self.dragged_square = square
                self.legal_moves = self.board.get_legal_moves(square)
                
    def _handle_mouse_up(self, event):
        if not self.dragging:
            return
            
        pos = pygame.mouse.get_pos()
        target_square = self.ui.get_square_from_pos(pos)
        
        if target_square is not None and target_square in self.legal_moves:
            if (self.dragged_piece.type == PAWN and 
                ((self.dragged_piece.color == WHITE and target_square // 8 == 7) or
                 (self.dragged_piece.color == BLACK and target_square // 8 == 0))):
                self.promotion_active = True
                self.promotion_square = target_square
                self.board.make_move(self.dragged_square, target_square)
            else:
                self._make_move(self.dragged_square, target_square)
        else:
            pass
            
        self.dragging = False
        self.dragged_piece = None
        self.dragged_square = None
        self.legal_moves = []
        
    def _handle_mouse_motion(self, event):
        """Handle mouse motion events."""
        if self.dragging:
            pass 
            
    def _handle_promotion_event(self, event):
        """Handle events during pawn promotion."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            piece_type = self.ui.get_promotion_piece(pos)
            if piece_type:
                self.board.promote_pawn(self.promotion_square, piece_type)
                self.promotion_active = False
                self.promotion_square = None
                self._switch_player()
                
    def _make_move(self, from_square, to_square):
        """Make a move and update game state."""
        move_notation = self.board.make_move(from_square, to_square)
        if move_notation:
            self.move_history.add_move(move_notation, self.current_player)
            # show latest moves after making a move
            self.ui.history_scroll = 0
            self._switch_player()
            self._check_game_state()
            
    def _switch_player(self):
        """Switch to the other player."""
        self.current_player = BLACK if self.current_player == WHITE else WHITE
        
    def _check_game_state(self):
        """Check for checkmate, stalemate, or check."""
        if self.board.is_checkmate(self.current_player):
            self.game_over = True
            self.winner = BLACK if self.current_player == WHITE else WHITE
            self.game_result = 'checkmate'
        elif self.board.is_stalemate(self.current_player):
            self.game_over = True
            self.game_result = 'stalemate'
            
    def reset_game(self):
        """Reset the game to initial state."""
        self.board.reset()
        self.move_history.clear()
        self.current_player = WHITE
        self.game_over = False
        self.winner = None
        self.game_result = None
        self.dragging = False
        self.dragged_piece = None
        self.dragged_square = None
        self.legal_moves = []
        self.promotion_active = False
        self.promotion_square = None
        
    def update(self):
        if self.reset_pressed and pygame.time.get_ticks() - self.reset_timer > 1000:
            self.reset_pressed = False
            
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.ui.draw_board(self.screen, self.board)
        
        if self.dragging and self.legal_moves:
            self.ui.draw_legal_moves(self.screen, self.legal_moves)
            
        if self.dragging and self.dragged_piece:
            mouse_pos = pygame.mouse.get_pos()
            self.ui.draw_dragged_piece(self.screen, self.dragged_piece, mouse_pos)
            
        self.ui.draw_move_history(self.screen, self.move_history)
        
        if self.promotion_active:
            self.ui.draw_promotion_popup(self.screen, self.current_player)
            
        if self.game_over:
            self.ui.draw_game_over_popup(self.screen, self.game_result, self.winner)
            
        pygame.display.flip()
