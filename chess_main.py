#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Chess960 (Fischer Random Chess) GUI implementation with sound effects
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
BOARD_WIDTH = HEIGHT = 720              # Board size in pixels
SIDEBAR_WIDTH = 200                     # Width of the sidebar for instructions
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH     # Total window width
DIMENSION = 8                           # 8x8 chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 120                           # For animations
IMAGES = {}                             # Stores piece images
SOUNDS = {}                             # Stores sound effects
FLIPPEDBOARD = [i for i in reversed(range(DIMENSION))]  # For black perspective
UPSIDEDOWN = False                      # Board orientation
selectedSquare = None                   # Currently selected square
checkSoundPlayed = False                # Track if check sound has been played for current check state
gameEndSoundPlayed = False              # Track if game-end sound has been played

def main():
    """
    Main driver for Chess960 game.
    Handles user input and updates graphics.
    """
    global screen, clock, theme, gs, highlight_last_move, UPSIDEDOWN, selectedSquare, humanWhite, humanBlack, checkSoundPlayed, gameEndSoundPlayed
    
    # Initialize game settings
    humanWhite, humanBlack, theme_name = mainMenu()
    if theme_name not in themes:
        theme_name = "blue"
    
    p.init()
    # Initialize Pygame mixer for sound playback
    p.mixer.init()
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
    
    # Load piece images and sounds
    loadImages()
    loadSounds()
    
    # Game state variables
    squareClicked = ()          # Last square clicked
    playerClicks = []           # Track player clicks (two squares per move)
    highlight_last_move = True  # Highlight last move
    
    # Set board orientation based on player color
    if humanBlack:
        UPSIDEDOWN = True
    
    # Main game loop
    while True:
        humanTurn = (gs.white_to_move and humanWhite) or (not gs.white_to_move and humanBlack)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                exitGame()
            
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location
                # Check if click is in sidebar for undo/redo buttons or quit button
                if location[0] >= BOARD_WIDTH:
                    sidebar_x = location[0] - BOARD_WIDTH
                    sidebar_y = location[1]
                    # Undo button area: 20-100, 80-140
                    if (sidebar_x >= 20 and sidebar_x <= 100 and
                        sidebar_y >= 80 and sidebar_y <= 140):
                        if gs.move_log:
                            gs.board.update_pieces(gs.undo_move())
                            move = gs.undo_log.copy().pop()[0]
                            animateMove(move, validMoves, undo=True)
                            print(f'Undid {move}', end=' ')
                            moveMade = True
                    # Redo button area: 100-180, 80-140
                    elif (sidebar_x >= 100 and sidebar_x <= 180 and
                          sidebar_y >= 80 and sidebar_y <= 140):
                        if gs.undo_log:
                            gs.redo_move()
                            move = gs.move_log.copy().pop()[0]
                            animateMove(move, validMoves)
                            print(f'Redid {move}', end=' ')
                            moveMade = True
                    # Quit button area: 20-180, 650-680
                    elif (sidebar_x >= 20 and sidebar_x <= 180 and
                          sidebar_y >= 650 and sidebar_y <= 680):
                        # Reset game state and return to main menu
                        p.quit()
                        main()
                        return
                
                if not gs.gameover and humanTurn:
                    file = location[0] // SQ_SIZE
                    rank = location[1] // SQ_SIZE
                    
                    # Ensure clicks are within the board area
                    if location[0] >= BOARD_WIDTH:  # Ignore other sidebar clicks
                        continue
                    
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

            # Key handler for undo/redo with arrow keys
            elif e.type == p.KEYDOWN:
                # Undo with left arrow key
                if e.key == p.K_LEFT:
                    if gs.move_log:
                        gs.board.update_pieces(gs.undo_move())
                        move = gs.undo_log.copy().pop()[0]
                        animateMove(move, validMoves, undo=True)
                        print(f'Undid {move}', end=' ')
                        moveMade = True
                # Redo with right arrow key
                elif e.key == p.K_RIGHT:
                    if gs.undo_log:
                        gs.redo_move()
                        move = gs.move_log.copy().pop()[0]
                        animateMove(move, validMoves)
                        print(f'Redid {move}', end=' ')
                        moveMade = True

        # AI move finder
        if not moveMade and not gs.gameover and not humanTurn:
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
        
        # Draw the sidebar and instructions
        drawSidebar()

        # Display game over message and play game-end sound
        if gs.gameover:
            s = p.Surface((BOARD_WIDTH, HEIGHT))
            s.fill((0, 0, 0))
            s.set_alpha(150)
            screen.blit(s, (0, 0))
            
            if gs.checkmate:
                # Determine if the human or computer won
                if gs.white_to_move:  # White is checkmated, Black wins
                    if humanBlack:
                        winner_text = "You won by checkmate!"
                    else:
                        winner_text = "Computer Won by checkmate!"
                else:  # Black is checkmated, White wins
                    if humanWhite:
                        winner_text = "You won by checkmate!"
                    else:
                        winner_text = "Computer Won by checkmate!"
                drawText(winner_text, 48)
            elif gs.stalemate:
                if gs.stalemate_counter > 100:
                    drawText('Draw by 50-move rule', 36)
                else:
                    drawText('Stalemate - Draw', 36)
            
            # Play game-end sound only once
            if not gameEndSoundPlayed:
                SOUNDS['game_end'].play()
                gameEndSoundPlayed = True

        # Reset game-end sound flag if the game is no longer over (e.g., after undo)
        if not gs.gameover and gameEndSoundPlayed:
            gameEndSoundPlayed = False

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

def loadSounds():
    """Initialize dictionary of sound effects."""
    sound_files = ['move', 'capture', 'check', 'game_end']
    
    # Use absolute path relative to this file
    sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')

    for sound in sound_files:
        try:
            sound_path = os.path.join(sounds_dir, f"{sound}.wav")
            SOUNDS[sound] = p.mixer.Sound(sound_path)
            # Set volume (0.0 to 1.0)
            SOUNDS[sound].set_volume(0.5)
        except Exception as e:
            print(f"Warning: Could not load sound for {sound}. Error: {e}")
            # Create a silent sound as fallback
            SOUNDS[sound] = p.mixer.Sound(p.mixer.Sound(buffer=b'\x00' * 1000))

def playSound(move, undo=False):
    """Play appropriate sound based on the move."""
    if undo:
        return  # Don't play sounds when undoing moves
    
    # Check for capture (including en passant)
    if move.piece_captured is not None or move.contains_enpassant():
        SOUNDS['capture'].play()
    else:
        SOUNDS['move'].play()

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
    """Draw pieces on their current squares and play check sound if needed."""
    global checkSoundPlayed
    
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
            # Draw red border around king if in check and play sound
            if gs.in_check and (piece.get_name() == 'King' and piece.get_color() == ('white' if gs.white_to_move else 'black')):
                border_width = 2
                border_color = p.Color('red')
                border_rect = p.Rect(
                    file * SQ_SIZE - border_width,
                    rank * SQ_SIZE - border_width,
                    SQ_SIZE + 2 * border_width,
                    SQ_SIZE + 2 * border_width
                )
                p.draw.rect(screen, border_color, border_rect, border_width)
                # Play check sound only once per check state
                if not checkSoundPlayed:
                    SOUNDS['check'].play()
                    checkSoundPlayed = True
    # Reset check sound flag if no longer in check
    if not gs.in_check and checkSoundPlayed:
        checkSoundPlayed = False

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
    """Animate piece movement and play sound."""
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
    
    # Play sound at the start of the move animation
    playSound(move, undo)
    
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
        
        # Draw sidebar during animation
        drawSidebar()
        
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
    font = p.font.SysFont(font, size=font_size, bold=True, italic=False)
    textObject = font.render(text, True, (245, 245, 245))
    textRect = textObject.get_rect()
    textRect.centerx = BOARD_WIDTH // 2 + xoffset
    textRect.centery = HEIGHT // 2 - HEIGHT // 15 + yoffset
    screen.blit(textObject, textRect)

def drawTurnIndicator():
    """Draws a turn indicator at the top of the sidebar showing whose turn it is."""
    # Position and size of the turn indicator
    indicator_x = BOARD_WIDTH + SIDEBAR_WIDTH // 2
    indicator_y = 25  # Slightly higher for better alignment
    radius = 15  # Smaller radius for cleaner look

    # Draw the circle background
    turn_color = p.Color('white') if gs.white_to_move else p.Color('black')
    p.draw.circle(screen, turn_color, (indicator_x, indicator_y), radius)

    # Draw a border around the circle
    border_color = p.Color('black') if gs.white_to_move else p.Color('white')
    p.draw.circle(screen, border_color, (indicator_x, indicator_y), radius, 2)

    # Determine turn text based on player color
    humanTurn = (gs.white_to_move and humanWhite) or (not gs.white_to_move and humanBlack)
    text = "Your turn" if humanTurn else "Computer's turn"
    
    # Add text label below the circle with adjusted spacing
    font = p.font.SysFont('Helvetica', 16, True)
    text_color = p.Color('white')  # White text for better contrast on dark background
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(indicator_x, indicator_y + radius + 20))
    screen.blit(text_surface, text_rect)

def drawSidebar():
    """Draw a sidebar with turn indicator, undo/redo buttons, and quit button with adjusted spacing."""
    # Draw sidebar background with a cool metallic gradient
    sidebar_rect = p.Rect(BOARD_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    # Create a surface for the gradient
    sidebar_surface = p.Surface((SIDEBAR_WIDTH, HEIGHT))
    for y in range(HEIGHT):
        r = 50 + (y / HEIGHT) * 20  # Subtle red gradient
        g = 50 + (y / HEIGHT) * 20  # Subtle green gradient
        b = 60 + (y / HEIGHT) * 30  # Subtle blue gradient
        p.draw.line(sidebar_surface, (r, g, b), (0, y), (SIDEBAR_WIDTH, y))
    screen.blit(sidebar_surface, (BOARD_WIDTH, 0))

    # Draw shadow effect
    shadow_surface = p.Surface((SIDEBAR_WIDTH + 10, HEIGHT + 10), p.SRCALPHA)
    p.draw.rect(shadow_surface, (0, 0, 0, 100), (5, 5, SIDEBAR_WIDTH, HEIGHT))  # Semi-transparent shadow
    screen.blit(shadow_surface, (BOARD_WIDTH - 5, -5))

    # Draw stylish border
    border_color_inner = (80, 80, 80)  # Dark gray inner border
    border_color_outer = (120, 120, 120)  # Light gray outer border
    p.draw.rect(screen, border_color_inner, (BOARD_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT), 2)  # Inner border
    p.draw.rect(screen, border_color_outer, (BOARD_WIDTH - 2, -2, SIDEBAR_WIDTH + 4, HEIGHT + 4), 4)  # Outer border

    # Draw turn indicator at the top
    drawTurnIndicator()

    # Undo button (adjusted spacing below turn indicator)
    undo_button_rect = p.Rect(BOARD_WIDTH + 20, 80, 80, 60)
    p.draw.rect(screen, (40, 40, 40), undo_button_rect)  # Darker button background for contrast
    p.draw.rect(screen, (150, 150, 150), undo_button_rect, 2)  # Lighter border
    # Draw left arrow
    arrow_points = [
        (BOARD_WIDTH + 40, 110),
        (BOARD_WIDTH + 60, 90),
        (BOARD_WIDTH + 60, 130)
    ]
    p.draw.polygon(screen, (200, 200, 200), arrow_points)

    # Redo button (aligned with undo button)
    redo_button_rect = p.Rect(BOARD_WIDTH + 100, 80, 80, 60)
    p.draw.rect(screen, (40, 40, 40), redo_button_rect)
    p.draw.rect(screen, (150, 150, 150), redo_button_rect, 2)
    # Draw right arrow
    arrow_points = [
        (BOARD_WIDTH + 140, 110),
        (BOARD_WIDTH + 120, 90),
        (BOARD_WIDTH + 120, 130)
    ]
    p.draw.polygon(screen, (200, 200, 200), arrow_points)

    # Quit button (adjusted spacing from the bottom)
    quit_button_rect = p.Rect(BOARD_WIDTH + 20, 668, 160, 30)
    p.draw.rect(screen, (150, 40, 40), quit_button_rect)  # Deeper red for a cool effect
    font = p.font.SysFont('Helvetica', 18, True, False)
    quit_text = "Quit to Menu"
    quit_object = font.render(quit_text, True, (245, 245, 245))
    quit_rect = quit_object.get_rect()
    quit_rect.centerx = BOARD_WIDTH + SIDEBAR_WIDTH // 2
    quit_rect.centery = 683
    screen.blit(quit_object, quit_rect)

def exitGame():
    """Clean up and exit."""
    # Stop all sounds before exiting
    p.mixer.stop()
    p.quit()
    sys.exit()

if __name__ == '__main__':
    main()