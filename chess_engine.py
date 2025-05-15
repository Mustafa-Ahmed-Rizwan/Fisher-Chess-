# -*- coding: utf-8 -*-
"""
Modified for Chess960 (Fischer Random Chess)
"""

from typing import Union, Tuple
from chess_pieces import Queen, Rook, Bishop, Knight
from chess_pieces import DIRECTIONS
from chess_board import makeChess960Board, Square

class GameState():
    """
    Modified for Chess960 rules:
    - Random starting positions
    - Flexible castling rules
    """
    
    def __init__(self):
        self.board = makeChess960Board()
        self.file_size, self.rank_size = self.board.get_size()
        self.white_to_move = True
        self.move_log = []
        self.undo_log = []
        self.move_branches = []
        self.move_number = 0
        self.pins = []
        self.checks = []
        self.in_check = False
        self.check_color = None 
        self.gameover = False
        self.checkmate = False
        self.stalemate = False
        self.stalemate_counter = 0
        self.enpassant_coords = ()
        self.valid_moves = []
        
        # Track starting positions for castling
        self.white_king_start_pos = self.board.white_king.get_coords()
        self.black_king_start_pos = self.board.black_king.get_coords()
        self.white_rooks_start_pos = [
            piece.get_coords() for piece in self.board.piece_lists['Rook']['white']
        ]
        self.black_rooks_start_pos = [
            piece.get_coords() for piece in self.board.piece_lists['Rook']['black']
        ]
    
    def make_new_move(self, move):
        if self.undo_log:
            self.move_branches.append(self.undo_log)
            self.undo_log.clear()
        if (move.piece_moved.get_name() == 'Pawn'
                or move.piece_captured is not None):
            self.stalemate_counter = 0
        else:
            self.stalemate_counter += 1
        
        if move.name == '':
            move.name = move.get_chess_notation(self)

        self.make_move(move)

    def make_move(self, move):
        pieces_set, pieces_removed = [], []
        if move.contains_enpassant():
            move.enpassant_square.remove_piece()
        elif move.piece_captured is not None:
            pieces_removed.append(move.piece_captured)
            move.end_square.remove_piece()
        move.start_square.remove_piece()
        if move.contains_promotion():
            move.end_square.set_piece(move.promotion_piece)
            pieces_set.append(move.promotion_piece)
            pieces_removed.append(move.piece_moved)
        elif move.contains_castle():
            rook, rookStartSquare, rookEndSquare = move.castle
            rookStartSquare.remove_piece()
            rookEndSquare.set_piece(rook)
            move.end_square.set_piece(move.piece_moved)
        else:
            move.end_square.set_piece(move.piece_moved)

        self.move_log.append((move, self.stalemate_counter))
        if not move.piece_moved.has_moved():
            move.piece_moved.first_move = move
            if (move.piece_moved.get_name() == 'Pawn'
                and (abs(move.end_square.get_rank()
                         - move.start_square.get_rank()) == 2)):
                self.enpassant_coords = move.piece_moved.get_coords()
            elif (self.enpassant_coords
                  or move.piece_moved.get_name() != "Pawn"):
                self.enpassant_coords = ()
        elif self.enpassant_coords:
            self.enpassant_coords = ()

        self.white_to_move = not self.white_to_move
        self.move_number += 1
        self.board.update_pieces(pieces_set, pieces_removed)
    
    def undo_move(self):
        if self.move_log:
            pieces_set, pieces_removed = [], []
            move, stalemate_counter = self.move_log.pop()
            move.end_square.remove_piece()
            move.start_square.set_piece(move.piece_moved)
            if move.piece_captured is not None:
                pieces_set.append(move.piece_captured)
                if move.contains_enpassant():
                    move.enpassant_square.set_piece(move.piece_captured)
                else:
                    move.end_square.set_piece(move.piece_captured)
            if move == move.piece_moved.get_first_move():
                move.piece_moved.first_move = None
            if move.contains_castle():
                rook, rookStartSquare, rookEndSquare = move.castle
                rookEndSquare.remove_piece()
                rookStartSquare.set_piece(rook)
            if move.contains_promotion():
                pieces_removed.append(move.promotion_piece)
            if self.move_log:
                previousMove, _ = self.move_log.copy().pop()
                if (previousMove.piece_moved.get_name() == 'Pawn'
                        and (abs(previousMove.end_square.get_rank()
                             - previousMove.start_square.get_rank()) == 2)):
                    self.enpassant_coords = (
                        (previousMove.end_square.get_coords())
                    )
                else:
                    self.enpassant_coords = ()

            if self.checkmate:
                self.checkmate = False
            if self.stalemate:
                self.stalemate = False
            self.white_to_move = not self.white_to_move
            self.move_number -= 1
            self.undo_log.append((move, stalemate_counter))
            self.board.update_pieces(pieces_set, pieces_removed)

    def redo_move(self):
        if self.undo_log:
            move, _ = self.undo_log.pop()
            self.make_move(move)

    def get_valid_moves(self):
        moves = []
        if self.white_to_move:
            king = self.board.white_king
        else:
            king = self.board.black_king
        if king.get_square() is None:
            return []
        self.pins, self.checks = self.get_pins_and_checks(king)

        s = self.board.squares
        kingFile, kingRank = king.get_coords()
        if self.checks:
            self.in_check = True
            self.check_color = 'white' if self.white_to_move else 'black'
            if len(self.checks) == 1:
                moves = self.get_all_moves()
                check = self.checks[0]
                checkSquare, checkDirection = check
                pieceChecking = checkSquare.get_piece()
                
                validSquares = []
                if pieceChecking.get_name() == 'Knight':
                    validSquares = [checkSquare]
                else:
                    for x, y in zip(range(self.file_size),
                        range(self.rank_size)):
                        endFile, endRank = (kingFile + checkDirection[0]*x,
                            kingRank + checkDirection[1]*y)
                        if (0 <= endFile < self.file_size
                                and 0 <= endRank < self.rank_size):
                            validSquare = s[(endFile, endRank)]
                            validSquares.append(validSquare)
                            if validSquare == checkSquare:
                                break
                for move in reversed(moves):
                    if move.piece_moved.get_name() != 'King':
                        if move.end_square not in validSquares:
                            moves.remove(move)
            else:
                self.get_king_and_knight_moves(king, moves)
        else:
            self.in_check = False
            self.check_color = None  # Not in check, so no color
            moves = self.get_all_moves()

        if moves:
            for move in reversed(moves):
                if move.piece_moved.get_name() == 'King':
                    if self.get_pins_and_checks(king, move.end_square)[1]:
                        moves.remove(move)

        if not king.has_moved() and not self.in_check:
            self.get_castle_moves(king, moves)
            for move in reversed(moves):
                if move.piece_moved.get_name() == 'King':
                    if self.get_pins_and_checks(king, move.end_square)[1]:
                        moves.remove(move)
        
        return moves

    def get_castle_moves(self, king, moves):
        """Chess960 castling implementation"""
        s = self.board.squares
        king_file, king_rank = king.get_coords()
        king_square = king.get_square()
        
        if self.in_check or king.has_moved():
            return
            
        rook_positions = (self.white_rooks_start_pos if king.get_color() == 'white' 
                        else self.black_rooks_start_pos)
        rank = 7 if king.get_color() == 'white' else 0
            
        for rook_file, _ in rook_positions:
            rook_square = s[rook_file, rank]
            rook = rook_square.get_piece()
            
            if rook is None or rook.has_moved():
                continue
                
            # Determine castling direction
            direction = 1 if rook_file > king_file else -1
            steps = abs(rook_file - king_file)
                
            # Check path is clear between king and rook
            path_clear = True
            for i in range(1, steps):
                check_file = king_file + (i * direction)
                if not (0 <= check_file < self.file_size):
                    path_clear = False
                    break
                # Skip checking the rook square itself
                if check_file != rook_file and s[check_file, rank].has_piece():
                    path_clear = False
                    break
                    
            if not path_clear:
                continue
                
            # Check safety of squares king moves through
            safe = True
            for i in range(1, min(3, steps) + 1):
                check_file = king_file + (i * direction)
                if not (0 <= check_file < self.file_size) or self.get_pins_and_checks(king, s[check_file, rank])[1]:
                    safe = False
                    break
                    
            if safe:
                castle_file = king_file + (2 * direction)
                # Ensure castle_file is within bounds and doesn't overlap with rook
                if 0 <= castle_file < self.file_size and castle_file != rook_file:
                    castle_square = s[castle_file, rank]
                    # Only add castle move if destination square is empty or is the rook's square
                    if not castle_square.has_piece() or castle_square == rook_square:
                        rook_end_file = king_file + (1 * direction)
                        if 0 <= rook_end_file < self.file_size and rook_end_file != castle_file:
                            rook_end_square = s[rook_end_file, rank]
                            if not rook_end_square.has_piece() or rook_end_square == rook_square:
                                moves.append(Move(
                                    king_square,
                                    castle_square,
                                    self.move_number,
                                    castle=(rook, rook_square, rook_end_square)
                                ))

    def get_all_moves(self):
        moves = []
        for piece in self.board.get_pieces():
            if piece.is_on_board():
                turn = piece.get_color()
                name = piece.get_name()
                if ((turn == 'white' and self.white_to_move)
                    or (turn == 'black' and not self.white_to_move)):
                    if name != 'King':
                        self.is_piece_pinned(piece)
                    if name == 'Pawn':
                        self.get_pawn_moves(piece, moves)
                    elif name in ('King', 'Knight'):
                        self.get_king_and_knight_moves(piece, moves)
                    else:
                        self.find_moves_on_path(piece, moves)
        return moves

    def is_piece_pinned(self, piece):
        if piece.get_name() != 'King':
            piece.pin_direction = ()
            for pin in reversed(self.pins):
                if pin[0] == piece.get_square():
                    piece.pin_direction = pin[1]
                    self.pins.remove(pin)
                    break

    def get_pawn_moves(self, pawn, moves):
        board = self.board
        s = board.squares
        f, r = pawn.get_coords()
        startSquare = s[f, r]
        y = pawn.get_directions()[1]

        if (not pawn.is_pinned()
            or pawn.get_pin_direction() == (0, y)
            or pawn.get_pin_direction() == (0, -y)):
            if (r + y < self.rank_size
                and not s[f, r + y].has_piece()):
                moves.append(Move(startSquare, s[f, r + y],
                        self.move_number))
                if ((not pawn.has_moved())
                    and not s[f, r + 2*y].has_piece()):
                    moves.append(Move(startSquare, s[f, r + 2*y],
                        self.move_number))

        for x, _ in DIRECTIONS['HORIZONTAL']:
            if (not pawn.is_pinned()
                or pawn.get_pin_direction() == (x, y)):
                if ((0 <= f+x < self.file_size)
                    and (0 <= r+y < self.rank_size)):
                    captureSquare = s[f+x, r+y]
                    if (captureSquare.has_piece()
                        and captureSquare.has_enemy_piece(pawn)):
                        moves.append(Move(startSquare, captureSquare,
                                          self.move_number))

        if (self.enpassant_coords != ()
                and abs(f - self.enpassant_coords[0]) == 1
                and r == self.enpassant_coords[1]):
            epSquare = s[self.enpassant_coords]
            endSquare = s[self.enpassant_coords[0], r+y]
            move = Move(
                startSquare, endSquare, self.move_number,
                enpassantSquare=epSquare
            )
            move.piece_captured = epSquare.get_piece()
            moves.append(move)

    def get_king_and_knight_moves(self, piece, moves):
        if piece.is_on_board():
            if not piece.is_pinned():
                f, r = piece.get_coords()
                s = self.board.squares
                for x, y in piece.get_directions():
                    endFile, endRank = f+x, r+y
                    if ((0 <= endFile < self.file_size)
                        and (0 <= endRank < self.rank_size)):
                        if not s[endFile, endRank].has_friendly_piece(piece):
                            moves.append(
                                Move(s[f, r], s[endFile, endRank],
                                     self.move_number)
                            )

    def find_moves_on_path(self, piece, moves):
        if piece.is_on_board():
            start_square = piece.get_square()
            f, r = start_square.get_coords()
            pathRange = max(self.file_size, self.rank_size)
            for direction in piece.get_directions():
                x, y = direction
                if (not piece.is_pinned()
                    or piece.get_pin_direction() == direction
                    or piece.get_pin_direction() == (-x, -y)):
                    for i in range(1, pathRange):
                        file, rank = f + x*i, r + y*i
                        if (0 <= file < self.file_size
                            and 0 <= rank < self.rank_size):
                            path_square = self.board.squares[file, rank]
                            if path_square.has_piece():
                                if path_square.has_friendly_piece(piece):
                                    break
                                elif path_square.has_enemy_piece(piece):
                                    moves.append(Move(
                                        start_square, path_square,
                                        self.move_number
                                        ))
                                    break
                            else:
                                moves.append(
                                    Move(start_square, path_square,
                                         self.move_number)
                                )

    def get_pins_and_checks(self, king, king_end_square=None):
        pins = []
        checks = []
        if king_end_square is None:
            kingFile, kingRank = king.get_square().get_coords()
        else:
            kingFile, kingRank = king_end_square.get_coords()
        
        directions = (
            DIRECTIONS['HORIZONTAL']
            + DIRECTIONS['VERTICAL']
            + DIRECTIONS['DIAGONAL']
        )
        
        for x, y in directions:
            possiblePin = ()
            for i, j in zip(range(1, self.file_size),
                range(1, self.rank_size)):
                (endFile, endRank) = (kingFile + x*i, kingRank + y*j)
                if ((0 <= endFile < self.file_size)
                    and (0 <= endRank < self.rank_size)):
                    square = self.board.squares[endFile, endRank]
                    if square.has_friendly_piece(king):
                        piece = square.get_piece()
                        if piece is not king:
                            if not possiblePin:
                                possiblePin = (square, (x, y))
                            else:
                                possiblePin = ()
                                break
                    elif square.has_enemy_piece(king):
                        piece = square.get_piece()
                        name = piece.get_name()
                        color = square.get_piece().get_color()
                        
                        if ((name, i, j) == ('King', 1, 1)
                             or (name == 'Pawn' 
                                     and ((color == 'black'
                                           and (x, y) in ((1, -1), (-1, -1)) 
                                           and j == 1)
                                     or (color == 'white' 
                                         and (x, y) in ((1, 1), (-1, 1)) 
                                         and j == 1)))
                            or (name not in ('King', 'Pawn')
                                and (x, y) in piece.get_directions())):
                            if not possiblePin:
                                checks.append((square, (x, y)))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = DIRECTIONS['KNIGHT']
        for x, y in knightMoves:
            endFile, endRank = kingFile + x, kingRank + y
            if ((0 <= endFile < self.file_size)
                and (0 <= endRank < self.rank_size)):
                square = self.board.squares[endFile, endRank]
                if (square.has_enemy_piece(king)
                    and square.get_piece().get_name() == 'Knight'):
                    checks.append((square, (x, y)))

        return pins, checks

    def promote(self, choice, move):
        if move.piece_moved.get_name() == 'Pawn':
            PROMOTION = dict(
                q = Queen,
                k = Knight,
                r = Rook,
                b = Bishop,
            )
            color = move.piece_moved.get_color()
            if choice in PROMOTION.keys():
                promotionPiece = PROMOTION[choice](color)
                move.promotion_piece = promotionPiece
        else:
            raise ValueError('Only Pawns can be promoted.')

    def find_mate(self, validMoves):
        if not validMoves:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        elif self.stalemate_counter > 100:
            self.stalemate = True

        self.gameover = True if self.checkmate or self.stalemate else False

class Move():
    """Object to store chess moves in."""
    def __init__(self, startSquare: Square, endSquare: Square, moveNumber: int,
            castle: Tuple[Union[Rook, Square]]=(),
            enpassantSquare: Union[Square, None]=None):
        if not startSquare.has_piece():
            raise ValueError(f'Square {startSquare.get_name()} has no piece to move.')
        else:
            self.start_square = startSquare
        self.end_square = endSquare
        self.move_number = moveNumber
        self.piece_moved = self.start_square.get_piece()
        self.enpassant_square = enpassantSquare
        self.piece_captured = self.end_square.get_piece()
        self.promotion_piece = None
        self.castle = castle
        self.id = (
            self.move_number,
            id(self.piece_moved),
            self.start_square.get_file() * 1000
            + self.start_square.get_rank() * 100
            + self.end_square.get_file() * 10
            + self.end_square.get_rank() * 1,
            id(self.piece_captured),
        )
        self.name = ''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)

    def get_chess_notation(self, gs: GameState):
        if self.contains_castle():
            rookFile = self.castle[1].get_coords()[0]
            kingFile = self.start_square.get_coords()[0]
            if rookFile < kingFile:
                return 'O-O-O'
            else:
                return 'O-O'
        
        piece_moved = self.piece_moved
        name = piece_moved.get_name()
        spacer = ''
        startSquare = self.start_square
        endSquare = self.end_square
        
        if name == 'Pawn':
            startFile = ''
            promoSymbol, ep = '', ''
            if self.piece_captured is not None:
                startFile = startSquare.get_name()[0]
                spacer = 'x'
                if self.contains_enpassant():
                    ep = ' e.p.'
            if self.contains_promotion():
                promoSymbol = '=' + self.promotion_piece.get_symbol()

            return ''.join([
                    startFile,
                    spacer,
                    endSquare.get_name(),
                    promoSymbol,
                    ep,
                ])
        else:
            symbol = piece_moved.get_symbol()
            startSquareName = ''
            if name != 'King':
                color = piece_moved.get_color()
                pieceList = gs.board.piece_lists[name][color]
                if len(pieceList) > 1:
                    file, rank = '', ''
                    for piece in pieceList:
                        if file and rank:
                            break
                        if piece is not piece_moved:
                            for move in gs.valid_moves:
                                if (move.end_square is endSquare
                                        and move.piece_moved is piece):
                                    startFile, startRank = (
                                        startSquare.get_name()[0],
                                        startSquare.get_name()[1]
                                    )
                                    otherFile, otherRank = (
                                        move.start_square.get_name()[0],
                                        move.start_square.get_name()[1]
                                    )
                                    if (startFile != otherFile 
                                            and not file):
                                        file = startFile
                                    elif (startRank != otherRank
                                            and not rank):
                                        rank = startRank
                    
                    startSquareName = ''.join([file, rank])
                
            if self.piece_captured is not None:
                spacer = 'x'

            return ''.join([
                symbol,
                startSquareName,
                spacer,
                endSquare.get_name(),
            ])

    def __str__(self):
        number = str(self.move_number//2 + 1)
        spacer = '...' if self.piece_moved.get_color() == 'black' else '. '
        return ''.join([number, spacer, self.name])

    def contains_promotion(self):
        return self.promotion_piece is not None

    def contains_castle(self):
        return bool(self.castle)

    def contains_enpassant(self):
        return self.enpassant_square is not None