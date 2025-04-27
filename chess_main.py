#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Chess960 (Fischer Random Chess) GUI implementation
"""

import os
import sys
import pygame as p
import random

import chess_engine
import chess_ai as ai
from chess_themes import themes
from chess_menu import mainMenu

# Constants
CAPTION = 'Chess960 (Fischer Random Chess)'
WIDTH = HEIGHT = 720                    # Board size in pixels
DIMENSION = 8                           # 8x8 chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 120                           # For animations
IMAGES = {}                             # Stores piece images
FLIPPEDBOARD = [i for i in reversed(range(DIMENSION))]  # For black perspective
UPSIDEDOWN = False                      # Board orientation
selectedSquare = None                   # Currently selected square

def main():
    """
    Main driver for Chess960 game.
    Handles user input and updates graphics.
    """
    global screen, clock, theme, gs, highlight_last_move, UPSIDEDOWN, selectedSquare
    
    # Initialize game settings
    humanWhite, humanBlack, theme_name = mainMenu()
    if theme_name not in themes:
        theme_name = "blue"
    
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption(CAPTION)
    clock = p.time.Clock()
    screen.fill(p.Color(28, 28, 28))
    theme = themes[theme_name]
    
    # Initialize Chess960 game state
    gs = chess_engine.GameState()
    gs.valid_moves = gs.get_valid_moves()
    validMoves = gs.valid_moves
    moveMade = False
    
    # Load piece images only once
    loadImages()
    
    # Game state variables
    squareClicked = ()          # Last square clicked
    playerClicks = []           # Track player clicks (two squares per move)
    highlight_last_move = True  # Highlight last move
    
    # Set board orientation based on player color
    if humanBlack and not humanWhite:
        UPSIDEDOWN = True
    
    # Main game loop
    while True:
        humanTurn = (gs.white_to_move and humanWhite) or (not gs.white_to_move and humanBlack)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                exitGame()
            
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gs.gameover and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location
                    file = location[0] // SQ_SIZE
                    rank = location[1] // SQ_SIZE
                    
                    if UPSIDEDOWN:
                        file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
                    
                    # Handle square selection
                    if squareClicked == (file, rank):
                        deselectSquare(gs.board.squares[file, rank])
                        squareClicked = ()
                        playerClicks = []
                    else:
                        squareClicked = (file, rank)
                        playerClicks.append(squareClicked)
                        selectSquare(gs.board.squares[file, rank])

                    # Handle move after two clicks
                    if len(playerClicks) == 2:
                        startSquare = gs.board.squares[playerClicks[0]]
                        endSquare = gs.board.squares[playerClicks[1]]
                        
                        # Only register move if first square has a piece
                        if startSquare.has_piece():
                            move = chess_engine.Move(startSquare, endSquare, gs.move_number)
                            
                            # Check if move is valid
                            for validMove in validMoves:
                                if move == validMove:
                                    # Handle pawn promotion
                                    pieceMoved = validMove.piece_moved
                                    if pieceMoved.get_name() == 'Pawn' and pieceMoved.can_promote():
                                        promoteMenu(validMove)
                                    
                                    # Execute move
                                    gs.make_new_move(validMove)
                                    animateMove(validMove, validMoves)
                                    printMove(validMove)
                                    moveMade = True
                                    break
                            
                            if not moveMade:
                                # Invalid move - reset selection
                                deselectSquare(startSquare)
                                if endSquare.has_piece():
                                    selectSquare(endSquare)
                                    playerClicks = [playerClicks[1]]
                                else:
                                    squareClicked = ()
                                    playerClicks = []

            # Key handler
            elif e.type == p.KEYDOWN:
                # Undo move
                if ((e.mod & p.KMOD_CTRL and e.key == p.K_z) or 
                    e.key == p.K_LEFT or e.key == p.K_a):
                    if gs.move_log:
                        gs.board.update_pieces(gs.undo_move())
                        move = gs.undo_log.copy().pop()[0]
                        animateMove(move, validMoves, undo=True)
                        print(f'Undid {move}', end=' ')
                        moveMade = True
                
                # Redo move
                elif ((e.mod & p.KMOD_CTRL and e.key == p.K_y) or 
                      e.key == p.K_RIGHT or e.key == p.K_d):
                    if gs.undo_log:
                        gs.redo_move()
                        move = gs.move_log.copy().pop()[0]
                        animateMove(move, validMoves)
                        print(f'Redid {move}', end=' ')
                        moveMade = True

        # AI move finder
        if not moveMade and not gs.gameover and not humanTurn and not gs.undo_log:
            AIMove = ai.getBestMove(gs)
            if AIMove is None:
                AIMove = ai.getRandomMove(validMoves)
            p.time.wait(200)
            gs.make_new_move(AIMove)
            animateMove(AIMove, validMoves)
            printMove(AIMove)
            moveMade = True
        
        # Update game state after move
        if moveMade:
            gs.valid_moves = gs.get_valid_moves()
            validMoves = gs.valid_moves
            if playerClicks:
                deselectSquare(gs.board.squares[playerClicks[0]])
            squareClicked = ()
            playerClicks = []
            moveMade = False
            selectedSquare = None

        # Check game status
        gs.find_mate(validMoves)
        drawGameState(validMoves)

        # Display game over message
        if gs.gameover:
            s = p.Surface((WIDTH, HEIGHT))
            s.fill((0, 0, 0))
            s.set_alpha(150)
            screen.blit(s, (0, 0))
            
            if gs.checkmate:
                winner = "Black" if gs.white_to_move else "White"
                drawText(f'{winner} wins by checkmate!', 48)
            elif gs.stalemate:
                if gs.stalemate_counter > 100:
                    drawText('Draw by 50-move rule', 36)
                else:
                    drawText('Stalemate - Draw', 36)

        clock.tick(MAX_FPS)
        p.display.flip()


def loadImages():
    """Initialize dictionary of piece images."""
    pieces = ['K', 'Q', 'R', 'B', 'N', 'P']  # King, Queen, Rook, Bishop, Knight, Pawn
    colors = ['w', 'b']                      # White, Black

    # Use absolute path relative to this file
    images_dir = os.path.join(os.path.dirname(__file__), 'images')

    for color in colors:
        for piece in pieces:
            pieceName = color + piece
            try:
                IMAGES[pieceName] = p.transform.smoothscale(
                    p.image.load(os.path.join(images_dir, pieceName + '.png')),
                    (SQ_SIZE, SQ_SIZE)
                )
                IMAGES[pieceName].convert()
            except:
                print(f"Warning: Could not load image for {pieceName}")
                # Create blank surface if image missing
                IMAGES[pieceName] = p.Surface((SQ_SIZE, SQ_SIZE))
                IMAGES[pieceName].fill((200, 200, 200))


def drawGameState(validMoves):
    """Draw complete game state including board, pieces, highlights."""
    drawBoard(validMoves)
    if highlight_last_move:
        highlightLastMove()
    if selectedSquare is not None:
        highlightSquares(validMoves)
    drawPieces()

def drawBoard(validMoves):
    """Draw squares on the board."""
    global selectedSquare
    selectedSquare = None
    
    for square in gs.board.squares.T.flat:
        file, rank = getSquareCoordinates(square)
        if square.is_selected():
            selectedSquare = square
        color = getSquareThemeColor(square)
        
        p.draw.rect(
            screen, color, p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE,
                SQ_SIZE, SQ_SIZE
            )
        )

def highlightLastMove():
    """Highlight squares involved in last move."""
    if gs.move_log:
        lastMove = gs.move_log.copy().pop()[0]
        startSquare = lastMove.start_square
        endSquare = lastMove.castle[1] if lastMove.contains_castle() else lastMove.end_square
        
        startFile, startRank = getSquareCoordinates(startSquare)
        endFile, endRank = getSquareCoordinates(endSquare)
        
        startColor = p.Color(theme[4] if startSquare.get_color() == 'light' else theme[5])
        endColor = p.Color(theme[4] if endSquare.get_color() == 'light' else theme[5])
        
        startSurface = p.Surface((SQ_SIZE, SQ_SIZE))
        startSurface.fill(startColor)
        endSurface = p.Surface((SQ_SIZE, SQ_SIZE))
        endSurface.fill(endColor)
        
        screen.blit(startSurface, (startFile * SQ_SIZE, startRank * SQ_SIZE))
        screen.blit(endSurface, (endFile * SQ_SIZE, endRank * SQ_SIZE))

def highlightSquares(validMoves):
    """Highlight selected square and possible moves."""
    file, rank = getSquareCoordinates(selectedSquare)
    color = getSquareThemeHighlightColor(selectedSquare)
    
    p.draw.rect(
        screen, color, p.Rect(
            file * SQ_SIZE, rank * SQ_SIZE,
            SQ_SIZE, SQ_SIZE
        )
    )
    
    # Highlight possible moves
    moveSquares, captureSquares = markMovementSquares(selectedSquare, validMoves)
    
    for square in moveSquares:
        file, rank = getSquareCoordinates(square)
        surface = p.Surface((SQ_SIZE, SQ_SIZE))
        surface.set_alpha(80)
        surface.fill(p.Color('green'))
        screen.blit(surface, (file * SQ_SIZE, rank * SQ_SIZE))
    
    for square in captureSquares:
        file, rank = getSquareCoordinates(square)
        attackSquare = p.Surface((SQ_SIZE, SQ_SIZE))
        attackSquare.fill((230, 118, 118))
        attackSquare.set_alpha(255)
        screen.blit(attackSquare, (file * SQ_SIZE, rank * SQ_SIZE))

def drawPieces():
    """Draw pieces on their current squares."""
    for piece in gs.board.get_pieces():
        if piece.is_on_board():
            file, rank = getSquareCoordinates(piece.get_square())
            pieceName = piece.get_image_name()
            screen.blit(
                IMAGES[pieceName], p.Rect(
                    file * SQ_SIZE, rank * SQ_SIZE,
                    SQ_SIZE, SQ_SIZE
                )
            )

def markMovementSquares(square, validMoves):
    """Find squares this piece can move to/capture on."""
    moveSquares = []
    captureSquares = []
    
    for move in validMoves:
        if square == move.start_square:
            if move.piece_captured is not None or move.contains_enpassant():
                captureSquares.append(move.end_square)
            else:
                moveSquares.append(move.end_square)
    
    return moveSquares, captureSquares

def animateMove(move, validMoves, undo=False):
    """Animate piece movement."""
    pieceMoved = move.piece_moved
    pieceCaptured = move.piece_captured
    startSquare, endSquare = (move.end_square, move.start_square) if undo else (move.start_square, move.end_square)
    
    startFile, startRank = getSquareCoordinates(startSquare)
    endFile, endRank = getSquareCoordinates(endSquare)
    
    dFile = endFile - startFile
    dRank = endRank - startRank
    
    if move.contains_castle():
        rook, rookStartSquare, rookEndSquare = move.castle
        if undo:
            rookStartSquare, rookEndSquare = rookEndSquare, rookStartSquare
        rookStartFile, rookStartRank = getSquareCoordinates(rookStartSquare)
        rookEndFile, rookEndRank = getSquareCoordinates(rookEndSquare)
        dRookFile = rookEndFile - rookStartFile
        dRookRank = rookEndRank - rookStartRank
    
    framesPerMove = MAX_FPS // 10 + 1
    
    for frame in range(1, framesPerMove + 1):
        drawBoard(validMoves)
        drawPieces()
        
        # Clear end square
        color = getSquareThemeColor(endSquare)
        p.draw.rect(screen, color, p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        
        # Draw captured piece if needed
        if move.contains_enpassant() and not undo:
            epFile, epRank = getSquareCoordinates(move.enpassant_square)
            screen.blit(IMAGES[pieceCaptured.get_image_name()],
                p.Rect(epFile*SQ_SIZE, epRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        elif pieceCaptured is not None:
            screen.blit(IMAGES[pieceCaptured.get_image_name()],
                p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        
        # Handle castling animation
        if move.contains_castle():
            color = getSquareThemeColor(rookEndSquare)
            p.draw.rect(screen, color,
                p.Rect(rookEndFile*SQ_SIZE, rookEndRank*SQ_SIZE,
                    SQ_SIZE, SQ_SIZE))
            drawAnimationFrame(rook, None, rookStartFile, rookStartRank,
                dRookFile, dRookRank, rookEndFile, rookEndRank, frame,
                framesPerMove)
        
        # Draw moving piece
        drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank,
            dFile, dRank, endFile, endRank, frame, framesPerMove)
        
        p.display.flip()
        clock.tick(MAX_FPS)

def drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank, dFile, dRank, endFile, endRank, frame, framesPerMove):
    """Draw single frame of animation."""
    file, rank = (startFile + dFile*frame/framesPerMove,
                  startRank + dRank*frame/framesPerMove)
    screen.blit(IMAGES[pieceMoved.get_image_name()],
        p.Rect(file*SQ_SIZE, rank*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def selectSquare(square):
    """Highlight selected square if it's player's piece."""
    if not square.is_selected() and square.has_piece():  # First check if square has a piece
        piece = square.get_piece()
        if piece:  # Additional safety check
            color = piece.get_color()
            if ((color == 'white' and gs.white_to_move) or
                (color == 'black' and not gs.white_to_move)):
                square.selected = True

def deselectSquare(square):
    """Remove selection from square."""
    if square.is_selected():
        square.selected = False

def getSquareThemeColor(square):
    """Get base color for square."""
    return theme[0] if square.get_color() == 'light' else theme[1]

def getSquareThemeHighlightColor(square):
    """Get highlight color for square."""
    return theme[2] if square.get_color() == 'light' else theme[3]

def getSquareCoordinates(square):
    """Convert board coordinates to screen coordinates."""
    file, rank = square.get_coords()
    if UPSIDEDOWN:
        file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
    return (file, rank)

def promoteMenu(move):
    """Handle pawn promotion selection."""
    choices = 'qkrb'  # Queen, Knight, Rook, Bishop
    print('Promote pawn to: q=Queen, k=Knight, r=Rook, b=Bishop')
    while True:
        try:
            i = input('Choice: ').lower()[0]
            if i in choices:
                gs.promote(i, move)
                return
            print("Invalid choice. Try again.")
        except:
            print("Invalid input. Try again.")

def printMove(move):
    """Print move in algebraic notation."""
    number = str(move.move_number//2 + 1)
    spacer = '...' if move.piece_moved.get_color() == 'black' else '. '
    print(''.join([number, spacer, move.name]), end=' ')

def drawText(text, font_size, font='Helvetica', xoffset=0, yoffset=0):
    """Draw centered text with outline."""
    font = p.font.SysFont(font, font_size, True, False)
    textObject = font.render(text, True, (245, 245, 245))
    textRect = textObject.get_rect()
    textRect.centerx = screen.get_rect().centerx + xoffset
    textRect.centery = screen.get_rect().centery - HEIGHT//15 + yoffset
    screen.blit(textObject, textRect)

def exitGame():
    """Clean up and exit."""
    p.quit()
    sys.exit()

if __name__ == '__main__':
    main()