"""
This is the main driver file.
It is responsible for handling the user input and displaying the current BoardState object.
"""

import pygame as p
from Chess import ChessEngine

Width = Height = 800
# This number is a power of 2 and allows easier operations
Dimension = 8
# A chessboard is a 8x8 grid
TileSize = Height // Dimension
MaxFPS = 30
# this is relevant for the animations of the pieces
Images = {}
colors = [p.Color(215, 185, 105), p.Color(95, 60, 30)]

'''
This initializes a dictionary of the chess images. It is an expensive operation, therefore it is only called once.
'''

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (TileSize, TileSize))
        # This is responsible for downloading images

'''
This is responsible for the title and the icon of the output
'''

p.display.set_caption("Chess Engine")
icon = p.image.load("images/mechanical-gears.png")
p.display.set_icon(icon)

'''
This is the main driver of the code. It is responsible for handling user input and uploading the graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((Width, Height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    bs = ChessEngine.BoardState()
    validMoves = bs.getValidMoves()
    moveMade = False    # Flag variable for when a move is made
    animate = False     # Flag variable for when an animation must be made
    loadImages()
    running = True
    gameOver = False
    tileSelected = ()
    # This is responsible for storing the selected tile, it stores row,column
    playerClicks = []
    # This is responsible for keeping track of the player's clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                # this is responsible for x,y location of the mouse
                col = location[0]//TileSize
                row = location[1]//TileSize
                if tileSelected == (row, col):
                    # This is responsible for checking if the player clicked the same square twice
                    tileSelected = ()       # deselects the clicked tile
                    playerClicks = []       # clears player's clicks
                else:
                    tileSelected = (row, col)
                    playerClicks.append(tileSelected)       # Append for both the first and second clicks
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], bs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            print(move.getChessNotation())
                            bs.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            tileSelected = ()       # resets the player's clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [tileSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:      # undoes a move when the left arrow key is pressed
                    bs.undoMove()
                    moveMade = True
                    animate = False
                elif e.key == p.K_r:
                    bs = ChessEngine.BoardState()
                    validMoves = bs.getValidMoves()
                    tileSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

            if moveMade:
                if animate:
                    animateMove(bs.moveLog[-1], screen, bs.board, clock)
                validMoves = bs.getValidMoves()
                moveMade = False
                animate = False

            DrawBoardState(screen, bs, validMoves, tileSelected)

            if bs.checkmate:
                gameOver = True
                if bs.whiteToMove:
                    drawText(screen, "Black wins, Congratulations!")
                else:
                    drawText(screen, "White wins, Congratulations!")
            elif bs.stalemate:
                drawText(screen, "Stalemate")
            clock.tick(MaxFPS)
            p.display.flip()

'''
This is responsible for all the graphics on the board
'''

def DrawBoardState(screen, bs, validMoves, tileSelected):
    DrawTiles(screen)
    # This is responsible for drawing the board tiles
    HighlightTiles(screen, bs, validMoves, tileSelected)
    DrawPieces(screen, bs.board)
    # This is responsible for drawing pieces on top of the tiles


'''
This is responsible for drawing the tiles of the board
'''

def DrawTiles(screen):
    for r in range(Dimension):
        for c in range(Dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*TileSize, r*TileSize, TileSize, TileSize))

'''
This is responsible for drawing the pieces on the board
'''

def DrawPieces(screen, board):
    for r in range(Dimension):
        for c in range(Dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(Images[piece], p.Rect(c * TileSize, r * TileSize, TileSize, TileSize))

'''
This is responsible for highlighting tiles when a move is to be made
'''

def HighlightTiles(screen, bs, validMoves, tileSelected):
    if tileSelected != ():
        r, c = tileSelected
        if bs.board[r][c][0] == ("w" if bs.whiteToMove else "b"):   # Checks that the selected piece is an ally
            s = p.Surface((TileSize, TileSize))
            s.set_alpha(80)
            s.fill(p.Color("green"))
            screen.blit(s, (c*TileSize, r*TileSize))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*TileSize, move.endRow*TileSize))

def animateMove(move, screen, board, clock):
    global colors
    change_row = move.endRow - move.startRow
    change_col = move.endCol - move.startCol
    framesPerSquare = 5
    # frameCount = (abs(change_row) + abs(change_col))*framesPerSquare
    frameCount = max(abs(change_row), abs(change_col)) * framesPerSquare
    if change_row != 0 and change_col != 0 or (change_row == 1 or change_col == 1):
        frameCount += framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + change_row*frame/frameCount, move.startCol + change_col*frame/frameCount)
        DrawTiles(screen)
        DrawPieces(screen, board)
        # Erase the moving piece in the ending tile
        color = colors[(move.endRow + move.endCol) % 2]
        endTile = p.Rect(move.endCol*TileSize, move.endRow*TileSize, TileSize, TileSize)
        p.draw.rect(screen, color, endTile)
        # Draw captured piece
        if move.pieceCaptured != "--":
            screen.blit(Images[move.pieceCaptured], endTile)
        # Draw moving piece
        screen.blit(Images[move.pieceMoved], p.Rect(c*TileSize, r*TileSize, TileSize, TileSize))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Verdana", 40, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, Width, Height).move(Width/2-textObject.get_width()/2, Height/2-textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, (180, 180, 180))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
