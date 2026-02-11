# Chess Game

A 2-player chess game built with Python and pygame using object-oriented programming and bitboard representation.

## Features

- **Bitboard Representation**: Highly optimized bitboard implementation for fast move generation and validation
- **Object-Oriented Design**: Each class in separate files for clean code organization
- **Chess.com Styling**: Board colors and labeling match chess.com
- **Piece Dragging**: Drag and drop pieces with legal move highlighting
- **Special Moves**: Castling, en passant, and pawn promotion
- **Move History**: Scrollable move history with chess notation
- **Game States**: Check, checkmate, and stalemate detection
- **Visual Feedback**: Legal move highlighting and piece dragging

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Adding Piece Images

To add PNG images for chess pieces, create the following directory structure:

```
assets/
  pieces/
    white_pawn.png
    white_rook.png
    white_knight.png
    white_bishop.png
    white_queen.png
    white_king.png
    black_pawn.png
    black_rook.png
    black_knight.png
    black_bishop.png
    black_queen.png
    black_king.png
```

### Image Requirements

- **Format**: PNG with transparency support
- **Size**: Recommended 60x60 pixels (will be scaled automatically)
- **Naming Convention**: `{color}_{piece}.png`
  - Colors: `white`, `black`
  - Pieces: `pawn`, `rook`, `knight`, `bishop`, `queen`, `king`

### Where to Get Images

You can find chess piece images from:
- Chess.com piece sets (extract from their website)
- Lichess piece sets
- Free chess piece image collections
- Create your own using image editing software

### Image Integration

The images are automatically loaded in the `GameUI` class. The `_load_piece_images()` method in `ui.py` handles the loading:

```python
def _load_piece_images(self):
    """Load piece images from PNG files."""
    # Images are loaded based on the naming convention
    # white_pawn.png, black_rook.png, etc.
```

If images are not found, the game will use colored placeholder rectangles.

## Running the Game

```bash
python main.py
```

## Controls

- **Left Click + Drag**: Move pieces
- **R Key (twice)**: Reset the game
- **Mouse Hover**: Highlight legal moves during piece dragging

## Game Rules

The game follows standard chess rules including:
- All standard piece movements
- Castling (kingside and queenside)
- En passant captures
- Pawn promotion (queen, rook, bishop, knight)
- Check, checkmate, and stalemate detection

## Project Structure

```
├── main.py              # Entry point
├── game.py              # Main game controller
├── board.py             # Chess board with bitboard
├── bitboard.py          # Bitboard implementation
├── piece.py             # Piece classes
├── ui.py                # User interface
├── move_history.py      # Move tracking
├── constants.py         # Game constants
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Technical Details

### Bitboard Implementation

The game uses bitboards for efficient position representation and move generation:
- 64-bit integers represent piece positions
- Fast bitwise operations for move generation
- Optimized attack detection and validation

### Move Validation

- Legal move generation for each piece type
- Check detection using bitboard operations
- Move validation to prevent illegal moves
- Special move handling (castling, en passant, promotion)

### Performance Optimizations

- Bitboard operations for fast position updates
- Efficient move generation algorithms
- Optimized rendering with pygame
- Minimal memory allocation during gameplay
