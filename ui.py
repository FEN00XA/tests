
from constants import *

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class GameUI:
    
    def __init__(self):
        if PYGAME_AVAILABLE:
            self.font = pygame.font.Font(None, 24)
            self.times_font = pygame.font.Font(None, 48)  
        else:
            self.font = None
            self.times_font = None
        
        self.piece_images = {}
        if PYGAME_AVAILABLE:
            self._load_piece_images()
        # History scroll: number of rows scrolled up from the bottom (0 = show most recent page)
        self.history_scroll = 0
        
    def _load_piece_images(self):
        piece_types = [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]
        colors = [WHITE, BLACK]
        
        for color in colors:
            for piece_type in piece_types:
                image_path = self._get_piece_image_path(color, piece_type)
                try:
                    surface = pygame.image.load(image_path)
                    if surface.get_size() != (70, 70):
                        surface = pygame.transform.scale(surface, (70, 70))
                    #print(f"✓ Loaded image: {image_path}")
                except pygame.error as e:
                    pass
                    
                self.piece_images[(color, piece_type)] = surface
                
    def _get_piece_image_path(self, color, piece_type):
        color_name = "white" if color == WHITE else "black"
        piece_names = {PAWN: "pawn", ROOK: "rook", KNIGHT: "knight", 
                      BISHOP: "bishop", QUEEN: "queen", KING: "king"}
        return f"assets/pieces/{color_name}_{piece_names[piece_type]}.png"
                
    def draw_board(self, screen, board):
        for rank in range(8):
            for file in range(8):
                display_rank = 7 - rank
                square_rect = pygame.Rect(
                    BOARD_X + file * SQUARE_SIZE,
                    BOARD_Y + display_rank * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
                
                if (file + rank) % 2 == 0:
                    color = BOARD_LIGHT
                else:
                    color = BOARD_DARK
                    
                pygame.draw.rect(screen, color, square_rect)
                
                square = rank * 8 + file
                piece = board.get_piece(square)
                if piece:
                    piece_image = self.piece_images.get((piece.color, piece.type))
                    if piece_image:
                        piece_rect = piece_image.get_rect(center=square_rect.center)
                        screen.blit(piece_image, piece_rect)
                        
        self._draw_labels(screen)
        
    def _draw_labels(self, screen):

        for i, file in enumerate(FILES):
            text = self.font.render(file, True, (255, 255, 255))
            text_rect = text.get_rect(center=(BOARD_X + i * SQUARE_SIZE + SQUARE_SIZE // 2,
                                            BOARD_Y + BOARD_SIZE + 10))
            screen.blit(text, text_rect)
            
        for i, rank in enumerate(RANKS):
            text = self.font.render(rank, True, (255, 255, 255))
            text_rect = text.get_rect(center=(BOARD_X - 15,
                                            BOARD_Y + i * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(text, text_rect)
            
    def draw_legal_moves(self, screen, legal_moves):
        for square in legal_moves:
            rank, file = square // 8, square % 8
            display_rank = 7 - rank
            square_rect = pygame.Rect(
                BOARD_X + file * SQUARE_SIZE,
                BOARD_Y + display_rank * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            overlay.set_alpha(128)
            overlay.fill(HIGHLIGHT_LEGAL)
            screen.blit(overlay, square_rect)
            
    def draw_dragged_piece(self, screen, piece, mouse_pos):
        piece_image = self.piece_images.get((piece.color, piece.type))
        if piece_image:
            piece_rect = piece_image.get_rect(center=mouse_pos)
            screen.blit(piece_image, piece_rect)
            
    def draw_move_history(self, screen, move_history):
        history_rect = pygame.Rect(HISTORY_X, HISTORY_Y, HISTORY_WIDTH, HISTORY_HEIGHT)
        
        pygame.draw.rect(screen, (30, 30, 35), history_rect, border_radius=12)
        
        pygame.draw.rect(screen, (60, 60, 70), history_rect, 1, border_radius=12)
        
        inner_rect = pygame.Rect(HISTORY_X + 2, HISTORY_Y + 2, HISTORY_WIDTH - 4, HISTORY_HEIGHT - 4)
        pygame.draw.rect(screen, (20, 20, 25), inner_rect, border_radius=10)
        
        title_rect = pygame.Rect(HISTORY_X + 15, HISTORY_Y + 15, HISTORY_WIDTH - 30, 30)
        pygame.draw.rect(screen, (45, 45, 50), title_rect, border_radius=8)
        
        title_text = self.font.render("MOVE HISTORY", True, (180, 180, 190))
        title_text_rect = title_text.get_rect(center=title_rect.center)
        screen.blit(title_text, title_text_rect)
        
        # Render move pairs (white / black) in two columns, make scrollable
        row_height = 28
        y_offset = 60

        pairs = move_history.get_move_pairs()
        total_rows = len(pairs)
        max_rows = max(1, (HISTORY_HEIGHT - 80) // row_height)

        # Compute start index so that history_scroll==0 shows the last page
        max_scroll = max(0, total_rows - max_rows)
        scroll = max(0, min(self.history_scroll, max_scroll))
        start_idx = max(0, total_rows - max_rows - scroll)
        end_idx = start_idx + max_rows

        visible_pairs = pairs[start_idx:end_idx]

        # Column positions
        num_w = 40
        white_col_x = HISTORY_X + 10
        black_col_x = HISTORY_X + HISTORY_WIDTH // 2 + 5

        for idx, (white_move, black_move) in enumerate(visible_pairs):
            if y_offset + row_height > HISTORY_Y + HISTORY_HEIGHT - 20:
                break

            move_num = start_idx + idx + 1

            # Move number box
            num_rect = pygame.Rect(HISTORY_X + 10, HISTORY_Y + y_offset, num_w, row_height - 4)
            pygame.draw.rect(screen, (35, 35, 40), num_rect, border_radius=6)
            pygame.draw.rect(screen, (60, 60, 70), num_rect, 1, border_radius=6)
            num_text = self.font.render(f"{move_num}.", True, (180, 180, 190))
            num_text_rect = num_text.get_rect(center=num_rect.center)
            screen.blit(num_text, num_text_rect)

            # White move box
            white_rect = pygame.Rect(white_col_x + num_w + 5, HISTORY_Y + y_offset, HISTORY_WIDTH // 2 - num_w - 30, row_height - 4)
            pygame.draw.rect(screen, (40, 40, 45), white_rect, border_radius=6)
            pygame.draw.rect(screen, (70, 70, 80), white_rect, 1, border_radius=6)
            white_text = self.font.render(white_move if white_move else "", True, (220, 220, 230))
            white_text_rect = white_text.get_rect(center=white_rect.center)
            screen.blit(white_text, white_text_rect)

            # Black move box
            black_rect = pygame.Rect(HISTORY_X + HISTORY_WIDTH // 2 + 5, HISTORY_Y + y_offset, HISTORY_WIDTH // 2 - 15, row_height - 4)
            pygame.draw.rect(screen, (35, 35, 40), black_rect, border_radius=6)
            pygame.draw.rect(screen, (60, 60, 70), black_rect, 1, border_radius=6)
            black_text = self.font.render(black_move if black_move else "", True, (180, 180, 190))
            black_text_rect = black_text.get_rect(center=black_rect.center)
            screen.blit(black_text, black_text_rect)

            y_offset += row_height

        # Draw scrollbar thumb
        if total_rows > max_rows:
            scrollbar_x = HISTORY_X + HISTORY_WIDTH - 14
            scrollbar_y = HISTORY_Y + 60
            scrollbar_h = HISTORY_HEIGHT - 80
            pygame.draw.rect(screen, (50, 50, 60), (scrollbar_x, scrollbar_y, 8, scrollbar_h), border_radius=4)
            thumb_h = max(10, int(scrollbar_h * (max_rows / total_rows)))
            thumb_pos = int((scrollbar_h - thumb_h) * (start_idx / max(1, total_rows - max_rows)))
            pygame.draw.rect(screen, (120, 120, 140), (scrollbar_x, scrollbar_y + thumb_pos, 8, thumb_h), border_radius=4)

        # Show '...' when there are off-screen rows above or below
        if start_idx > 0:
            up_text = self.font.render("^", True, (150, 150, 160))
            up_rect = up_text.get_rect(center=(HISTORY_X + HISTORY_WIDTH // 2, HISTORY_Y + 45))
            screen.blit(up_text, up_rect)
        if end_idx < total_rows:
            down_text = self.font.render("v", True, (150, 150, 160))
            down_rect = down_text.get_rect(center=(HISTORY_X + HISTORY_WIDTH // 2, HISTORY_Y + HISTORY_HEIGHT - 15))
            screen.blit(down_text, down_rect)

    def scroll_history(self, delta, total_rows=None, max_rows=None):
        """Adjust history scroll. delta is positive to scroll up (older moves)."""
        if total_rows is None:
            total_rows = 0
        if max_rows is None:
            max_rows = 1
        max_scroll = max(0, total_rows - max_rows)
        self.history_scroll = max(0, min(self.history_scroll + delta, max_scroll))
                
    def draw_promotion_popup(self, screen, color):
        popup_width = 200
        popup_height = 100
        popup_x = (WINDOW_WIDTH - popup_width) // 2
        popup_y = (WINDOW_HEIGHT - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, PROMOTION_BG, popup_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), popup_rect, 2, border_radius=10)
        
        piece_types = [QUEEN, ROOK, BISHOP, KNIGHT]
        piece_names = {QUEEN: 'Q', ROOK: 'R', BISHOP: 'B', KNIGHT: 'N'}
        
        for i, piece_type in enumerate(piece_types):
            piece_rect = pygame.Rect(
                popup_x + 20 + i * 40,
                popup_y + 30,
                30,
                30
            )
            
            mouse_pos = pygame.mouse.get_pos()
            if piece_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, PROMOTION_HOVER, piece_rect, border_radius=5)
            else:
                pygame.draw.rect(screen, (150, 150, 150), piece_rect, border_radius=5)
                
            text = self.font.render(piece_names[piece_type], True, (255, 255, 255))
            text_rect = text.get_rect(center=piece_rect.center)
            screen.blit(text, text_rect)
            
    def draw_game_over_popup(self, screen, game_result, winner):
        popup_width = 300
        popup_height = 150
        popup_x = (WINDOW_WIDTH - popup_width) // 2
        popup_y = (WINDOW_HEIGHT - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, (50, 50, 50), popup_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), popup_rect, 3, border_radius=10)
        
        if game_result == 'checkmate':
            text = f"Checkmate! {winner.title()} wins!"
        else:  # stalemate
            text = "Stalemate! No winner."
            
        text_surface = self.times_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2,
                                                popup_y + popup_height // 2))
        screen.blit(text_surface, text_rect)
        
    def get_square_from_pos(self, pos):
        x, y = pos
        if (BOARD_X <= x <= BOARD_X + BOARD_SIZE and 
            BOARD_Y <= y <= BOARD_Y + BOARD_SIZE):
            file = (x - BOARD_X) // SQUARE_SIZE
            display_rank = (y - BOARD_Y) // SQUARE_SIZE
            rank = 7 - display_rank
            if 0 <= file <= 7 and 0 <= rank <= 7:
                return rank * 8 + file
        return None
        
    def get_promotion_piece(self, pos):
        popup_width = 200
        popup_height = 100
        popup_x = (WINDOW_WIDTH - popup_width) // 2
        popup_y = (WINDOW_HEIGHT - popup_height) // 2
        
        x, y = pos
        if (popup_x <= x <= popup_x + popup_width and 
            popup_y <= y <= popup_y + popup_height):
            
            piece_types = [QUEEN, ROOK, BISHOP, KNIGHT]
            for i, piece_type in enumerate(piece_types):
                piece_rect = pygame.Rect(
                    popup_x + 20 + i * 40,
                    popup_y + 30,
                    30,
                    30
                )
                if piece_rect.collidepoint(pos):
                    return piece_type
                    
        return None
