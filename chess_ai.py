# -*- coding: utf-8 -*-
"""
Chess960 AI Implementation using Negamax with Alpha-Beta Pruning
"""

import random
from copy import copy

# Piece values for Chess960 (same as standard chess)
PIECE_VALUES = {
    'King': 20000,  # High value to prioritize checkmate
    'Queen': 9,
    'Rook': 5,
    'Bishop': 3.25,  # Slightly higher than knight in Chess960
    'Knight': 3,
    'Pawn': 1
}

CHECKMATE = PIECE_VALUES['King'] + 1
STALEMATE = 0
MAX_DEPTH = 3  # Increase for stronger AI (slower)

# Global variable for tracking best move
nextMove = None

def getRandomMove(validMoves):
    """Returns a random valid move."""
    return random.choice(validMoves) if validMoves else None

def getBestMove(gs):
    """
    Finds the best move using Negamax with Alpha-Beta pruning.
    Args:
        gs: GameState object
    Returns:
        Move: Best move found
    """
    global nextMove
    gs_copy = copy(gs)
    validMoves = gs_copy.valid_moves
    
    # Randomize move order to make AI less predictable
    random.shuffle(validMoves)
    
    nextMove = None
    negamaxAlphaBeta(gs_copy, validMoves, MAX_DEPTH, -CHECKMATE, CHECKMATE, 
                    1 if gs_copy.white_to_move else -1)
    
    return nextMove if nextMove else getRandomMove(validMoves)

def negamaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    """
    Negamax algorithm with Alpha-Beta pruning.
    """
    global nextMove
    
    # Base case - return board evaluation at leaf nodes
    if depth == 0 or gs.gameover:
        return turnMultiplier * evaluateBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        # Make the move
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        
        # Recursive call
        score = -negamaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        
        # Undo the move
        gs.undo_move()
        
        # Update best move if at root level
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
        
        # Alpha-Beta pruning
        alpha = max(alpha, maxScore)
        if alpha >= beta:
            break
    
    return maxScore

def evaluateBoard(gs):
    """
    Evaluates the board position for the AI.
    Positive score is good for white, negative for black.
    """
    if gs.checkmate:
        return -CHECKMATE if gs.white_to_move else CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    board = gs.board
    
    # Material evaluation
    for piece in board.get_pieces():
        if piece.is_on_board():
            pieceValue = PIECE_VALUES[piece.get_name()]
            
            # Add bonuses for specific Chess960 considerations
            if piece.get_name() == 'Bishop':
                # Bonus for bishop pair
                if len(board.piece_lists['Bishop'][piece.get_color()]) >= 2:
                    pieceValue += 0.5
            elif piece.get_name() == 'Rook':
                # Small penalty for undeveloped rooks in Chess960
                if not piece.has_moved() and gs.move_number > 10:
                    pieceValue -= 0.3
            
            # Add value based on color
            if piece.get_color() == 'white':
                score += pieceValue
            else:
                score -= pieceValue
    
    return score

def scoreMaterial(board):
    """
    Quick material evaluation without positional considerations.
    """
    score = 0
    for piece in board.get_pieces():
        if piece.is_on_board():
            pieceValue = PIECE_VALUES[piece.get_name()]
            if piece.get_color() == 'white':
                score += pieceValue
            else:
                score -= pieceValue
    return score