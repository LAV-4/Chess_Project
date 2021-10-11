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
    screen.fill(p.Color("gray"))
    bs = ChessEngine.BoardState()
    loadImages()
    running = True
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
                column = location[0]//TileSize
                row = location[1]//TileSize
                if tileSelected == (row, column):
                    # This is responsible for checking if the player clicked the same square twice
                    tileSelected = ()       # deselects the clicked tile
                    playerClicks = []       # clears player's clicks
                else:
                    tileSelected = (row, column)
                    playerClicks.append(tileSelected)       # Append for both the first and second clicks
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], bs.board)
                    print(move.getChessNotation())
                    bs.makeMove(move)
                    tileSelected = ()       # resets the player's clicks
                    playerClicks = []

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:      # undoes a move when the left arrow key is pressed
                    bs.undoMove()

            DrawBoardState(screen, bs)
            clock.tick(MaxFPS)
            p.display.flip()


'''
This is responsible for all the graphics on the board
'''


def DrawBoardState(screen, bs):
    DrawTiles(screen)
    # This is responsible for drawing the board tiles
    DrawPieces(screen, bs.board)
    # This is responsible for drawing pieces on top of the tiles
    # Piece highlighting can be added later on


'''
This is responsible for drawing the tiles of the board
'''


def DrawTiles(screen):
    colors = [p.Color(215, 185, 105), p.Color(95, 60, 30)]
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


if __name__ == "__main__":
    main()
