# -*- coding: utf-8 -*-
"""
Modified for Chess960 (Fischer Random Chess)
"""

import numpy as np
from typing import Union, List, Tuple
import random

from chess_pieces import Piece, King, Queen, Rook, Bishop, Knight, Pawn

FILE = 'abcdefgh'
RANK = '87654321'

def defineFILEandRANK(files: int, ranks: int) -> Tuple[List[str]]:
    """
    Creates FILE and RANK globals for converting between computer and
    algebraic notations.
    """
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    fileList = []
    rankList = []
    for file in range(files):
        fileList.append(alpha[file])
    for rank in reversed(range(0, ranks)):
        rankList.append(str(rank))
    return fileList, rankList
    
def algebraicToComputer(coordinate: str) -> Tuple[int]:
    """Converts algebraic notation to computer coordinates."""
    file = FILE.index(coordinate[0])
    rank = RANK.index(coordinate[1])
    return file, rank
    
def computerToAlgebraic(file: int, rank: int) -> str:
    """Converts computer coordinates to algebraic notation."""
    file = FILE[file]
    rank = RANK[rank]
    return file + rank
    
def getSquareColor(file: int, rank: int) -> str:
    """Returns the color of the square."""
    if (rank % 2 == file % 2):
        return 'light'
    else:
        return 'dark'

def generate_chess960_position():
    """Generates a valid Chess960 starting position array."""
    pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    
    while True:
        random.shuffle(pieces)
        
        # Find bishops and check opposite colors
        bishop_positions = [i for i, p in enumerate(pieces) if p == 'B']
        if (bishop_positions[1] - bishop_positions[0]) % 2 == 0:
            continue
            
        # Find king between rooks
        king_pos = pieces.index('K')
        rook_positions = [i for i, p in enumerate(pieces) if p == 'R']
        if not (rook_positions[0] < king_pos < rook_positions[1]):
            continue
            
        break
        
    return pieces

def makeChess960Board():
    """
    Sets up a chessboard with Chess960 starting position.
    Returns a Board object populated with pieces.
    """
    board = Board()
    position = generate_chess960_position()
    
    # Set white pieces according to Chess960 position
    for file, piece_symbol in enumerate(position):
        rank = 7
        if piece_symbol == 'R':
            board.squares[file, rank].set_piece(Rook('white'))
        elif piece_symbol == 'N':
            board.squares[file, rank].set_piece(Knight('white'))
        elif piece_symbol == 'B':
            board.squares[file, rank].set_piece(Bishop('white'))
        elif piece_symbol == 'Q':
            board.squares[file, rank].set_piece(Queen('white'))
        elif piece_symbol == 'K':
            board.white_king = King('white')
            board.squares[file, rank].set_piece(board.white_king)
    
    # Set black pieces (mirror of white's position)
    for file, piece_symbol in enumerate(position):
        rank = 0
        if piece_symbol == 'R':
            board.squares[file, rank].set_piece(Rook('black'))
        elif piece_symbol == 'N':
            board.squares[file, rank].set_piece(Knight('black'))
        elif piece_symbol == 'B':
            board.squares[file, rank].set_piece(Bishop('black'))
        elif piece_symbol == 'Q':
            board.squares[file, rank].set_piece(Queen('black'))
        elif piece_symbol == 'K':
            board.black_king = King('black')
            board.squares[file, rank].set_piece(board.black_king)
    
    # Set pawns
    for file in range(8):
        board.squares[file, 6].set_piece(Pawn('white'))
        board.squares[file, 1].set_piece(Pawn('black'))
    
    board.update_pieces()
    return board

class Square():
    """A square on the chess board."""
    def __init__(self, file: int, rank: int, board) -> None:
        self.file = file
        self.rank = rank
        self.board = board
        self.color = getSquareColor(file, rank)
        self.piece = None
        self.name = computerToAlgebraic(file, rank)
        self.selected = False
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Square):
            if (self.board, self.file, self.rank) == (
                    other.board, other.file, other.rank):
                return True
        return False
        
    def __hash__(self) -> int:
        return hash((self.board, self.file, self.rank))
    
    def __repr__(self) -> str:
        return f"Square({self.file}, {self.rank})"
    
    def __str__(self):
        return f"{self.name} square"        
    
    def get_file(self) -> int:
        return self.file
    
    def get_rank(self) -> int:
        return self.rank
    
    def get_coords(self) -> Tuple[int]:
        return self.file, self.rank
    
    def get_color(self) -> str:
        return self.color
    
    def get_name(self) -> str:
        return self.name
    
    def get_piece(self) -> Union[Piece, None]:
        return self.piece
    
    def has_piece(self) -> bool:
        return self.piece is not None
    
    def get_piece_name(self) -> str:
        if self.has_piece():
            return self.piece.get_name()
        return f'No piece on {self.get_name()}'
    
    def set_piece(self, piece: Piece) -> None:
        self.piece = piece        
        piece.square = self
        
    def remove_piece(self) -> None:
        if self.has_piece():
            self.piece.square = None
            self.piece = None
        
    def get_board(self):
        return self.board
    
    def has_friendly_piece(self, piece) -> bool:
        if self.has_piece():
            return piece.get_color() == self.get_piece().get_color()
        return False
    
    def has_enemy_piece(self, piece) -> bool:
        if self.has_piece():
            return piece.get_color() != self.get_piece().get_color()
        return False
    
    def is_selected(self) -> bool:
        return self.selected

class Board():
    """Chess board object for Chess960."""
    def __init__(self, numFiles: int=8, numRanks: int=8) -> None:
        if (numFiles != 8 or numRanks != 8):
            global FILE, RANK
            FILE, RANK = defineFILEandRANK(numFiles, numRanks)
        
        self.files = numFiles
        self.ranks = numRanks
        self.pieces = []
        self.queens = {'white': [], 'black': []}
        self.rooks = {'white': [], 'black': []}
        self.knights = {'white': [], 'black': []}
        self.bishops = {'white': [], 'black': []}
        self.piece_lists = {
            'Queen': self.queens,
            'Rook': self.rooks,
            'Knight': self.knights,
            'Bishop': self.bishops
        }
        
        emptyBoard = []
        for file in range(numFiles):
            for rank in range(numRanks):
                emptyBoard.append(Square(file, rank, self))
        self.squares = np.array(emptyBoard, dtype=Square).reshape((self.files, self.ranks))
        self.white_king = None
        self.black_king = None
    
    def get_size(self) -> Tuple[int]:
        return self.files, self.ranks
    
    def update_pieces(self, /, pieces_set: list=[], pieces_removed: list=[]) -> None:
        if not self.pieces:
            for square in self.squares.flat:
                if square.has_piece():
                    piece = square.get_piece()
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.append(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].append(piece)
        else:
            if pieces_set:
                for piece in reversed(pieces_set):
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.append(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].append(piece)
                        self.piece_lists[name][color] = list(set(
                            self.piece_lists[name][color]))
            if pieces_removed:
                for piece in reversed(pieces_removed):
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.remove(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].remove(piece)
                        self.piece_lists[name][color] = list(set(
                            self.piece_lists[name][color]))
        
        self.pieces = list(set(self.pieces))
    
    def get_pieces(self) -> list:
        return self.pieces

