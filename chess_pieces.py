# -*- coding: utf-8 -*-
"""
Chess pieces implementation for Chess960 (Fischer Random Chess)
All pieces maintain standard movement rules, only starting positions differ
"""

from __future__ import annotations

__all__ = ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']

from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from chess_board import Square
    from chess_engine import Move

# Movement directions for all piece types
DIRECTIONS = {
    'DIAGONAL': (
        (1, -1),   # Up Left
        (-1, -1),  # Up Right
        (-1, 1),   # Down Left
        (1, 1),    # Down Right
    ),
    'HORIZONTAL': (
        (-1, 0),  # Left
        (1, 0),   # Right
    ),
    'VERTICAL': (
        (0, -1),  # Up
        (0, 1),   # Down
    ),
    'KNIGHT': (
        (-1, -2),  # Up 2, Left 1
        (1, -2),   # Up 2, Right 1
        (-1, 2),   # Down 2, Left 1 
        (1, 2),    # Down 2, Right 1
        (-2, -1),  # Left 2, Up 1
        (-2, 1),   # Left 2, Down 1
        (2, -1),   # Right 2, Up 1
        (2, 1),    # Right 2, Down 1
    ),
}

class Piece:
    """
    Base class for all chess pieces in Chess960
    Maintains standard movement rules - only starting positions differ
    """
    
    def __init__(self, color: str) -> None:
        """
        Initialize piece with color ('white' or 'black')
        """
        if color.lower().startswith('w'):
            self.color = 'white'
        elif color.lower().startswith('b'):
            self.color = 'black'
        else:
            raise ValueError("Piece color must be 'white' or 'black'")
        
        self.square = None        # Current square the piece occupies
        self.first_move = None    # Track first move for castling/en passant
        self.pin_direction = ()   # Direction from which piece is pinned
        self.image_name = self.color[0] + self.symbol  # For GUI rendering

    def __eq__(self, other) -> bool:
        """Pieces are equal if they are the same object"""
        return id(self) == id(other)
    
    def __hash__(self) -> int:
        return hash((self.name, self.color, id(self)))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.color}')"
    
    def __str__(self) -> str:
        return self.get_fullname()

    def get_color(self) -> str:
        """Returns piece color ('white' or 'black')"""
        return self.color
    
    def get_square(self) -> Square:
        """Returns current square object"""
        return self.square
    
    def get_coords(self) -> Tuple[int]:
        """Returns (file, rank) coordinates if on board"""
        if self.is_on_board():
            return self.square.get_coords()
        return ()
    
    def get_square_name(self) -> str:
        """Returns algebraic notation of current square"""
        if self.is_on_board():
            return self.square.get_name()
        return ''
    
    def get_square_color(self) -> str:
        """Returns color of current square ('light' or 'dark')"""
        return self.square.get_color()
    
    def set_square(self, square: Square) -> None:
        """Places piece on a square"""
        self.square = square
        square.piece = self
    
    def is_on_board(self) -> bool:
        """Returns True if piece is placed on board"""
        return self.square is not None
        
    def get_name(self) -> str:
        """Returns piece name (e.g., 'Queen')"""
        return self.name
    
    def get_symbol(self) -> str:
        """Returns algebraic notation symbol (e.g., 'Q' for Queen)"""
        return self.symbol
    
    def get_fullname(self) -> str:
        """Returns descriptive string (e.g., 'White Queen on d1')"""
        parts = []
        if not self.is_on_board():
            parts.append('Off-the-board')
        parts.append(self.color.title())
        parts.append(self.name.title())
        if self.is_on_board():
            parts.extend(['on', self.get_square_name()])
        return ' '.join(parts)
    
    def get_image_name(self) -> str:
        """Returns image filename prefix (e.g., 'wQ' for white Queen)"""
        return self.image_name
    
    def remove(self) -> None:
        """Removes piece from board"""
        if self.is_on_board():
            self.square.remove_piece()
    
    def has_moved(self) -> bool:
        """Returns True if piece has moved from starting position"""
        return self.first_move is not None
    
    def get_first_move(self) -> Move:
        """Returns first move if piece has moved"""
        return self.first_move if self.has_moved() else None
    
    def is_pinned(self) -> bool:
        """Returns True if piece is pinned to king"""
        return len(self.pin_direction) > 0
    
    def get_pin_direction(self) -> Tuple[int]:
        """Returns direction of pin if pinned"""
        return self.pin_direction
    
    def get_directions(self) -> Tuple[Tuple[int]]:
        """Returns tuple of movement direction vectors"""
        return self.directions

class Rook(Piece):
    """Rook piece - moves horizontally/vertically any distance"""
    
    def __init__(self, color: str) -> None:
        self.name = 'Rook'
        self.symbol = 'R'
        super().__init__(color)
        self.directions = DIRECTIONS['HORIZONTAL'] + DIRECTIONS['VERTICAL']

class King(Piece):
    """King piece - moves one square in any direction"""
    
    def __init__(self, color: str) -> None:
        self.name = 'King'
        self.symbol = 'K'
        super().__init__(color)
        self.directions = (
            DIRECTIONS['HORIZONTAL'] 
            + DIRECTIONS['VERTICAL'] 
            + DIRECTIONS['DIAGONAL']
        )

class Queen(Piece):
    """Queen piece - moves any distance in any direction"""
    
    def __init__(self, color: str) -> None:
        self.name = 'Queen'
        self.symbol = 'Q'
        super().__init__(color)
        self.directions = (
            DIRECTIONS['HORIZONTAL'] 
            + DIRECTIONS['VERTICAL'] 
            + DIRECTIONS['DIAGONAL']
        )

class Knight(Piece):
    """Knight piece - moves in L-shape (2 squares one way, 1 square perpendicular)"""
    
    def __init__(self, color: str) -> None:
        self.name = 'Knight'
        self.symbol = 'N'
        super().__init__(color)
        self.directions = DIRECTIONS['KNIGHT']

class Bishop(Piece):
    """Bishop piece - moves diagonally any distance"""
    
    def __init__(self, color: str) -> None:
        self.name = 'Bishop'
        self.symbol = 'B'
        super().__init__(color)
        self.directions = DIRECTIONS['DIAGONAL']

class Pawn(Piece):
    """Pawn piece - moves forward, captures diagonally"""
    
    def __init__(self, color: str) -> None:
        self.name = 'Pawn'
        self.symbol = 'P'
        super().__init__(color)
        
        # Pawns move differently based on color
        if self.color == 'white':
            self.directions = DIRECTIONS['VERTICAL'][0]  # (0, -1)
            self.promotion_rank = 0  # Rank 1 (0 in zero-based)
        else:
            self.directions = DIRECTIONS['VERTICAL'][1]  # (0, 1)
            self.promotion_rank = 7  # Rank 8 (7 in zero-based)
    
    def get_promotion_rank(self) -> int:
        """Returns rank index where pawn promotes"""
        return self.promotion_rank
    
    def can_promote(self) -> bool:
        """Returns True if pawn is on promotion square"""
        if not self.is_on_board():
            return False
        current_rank = self.get_coords()[1]
        return (current_rank + self.directions[1] == self.promotion_rank)