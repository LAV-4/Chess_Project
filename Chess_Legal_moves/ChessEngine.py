"""
This is responsible for storing all the information about the current state of the chess game.
It is responsible for determining any valid move in any given board_state.
It is responsible for keeping a move log.
"""


class BoardState():
    def __init__(self):
        # The board is 8x8. It is represented by a 2d list
        # Each element of the list is described by two characters in accordance to algebraic notation:
        # The first character represents the color of the piece:
        # "b" (black), "w" (white)
        # The second character represents the type of the piece:
        # "R" (Rook), "N" (Knight), "B" (Bishop), "Q" (Queen), "K" (King), "p" (pawn)
        # "--" represents an empty tile
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.possibleEnpassant = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.wQs,
                                             self.currentCastlingRights.bKs, self.currentCastlingRights.bQs)]
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        if self.board[move.startRow][move.startCol] != "--":
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow, move.endCol)

            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol] = "--"
            if move.pieceMoved[1] == "p" and abs(move.startRow-move.endRow) == 2:
                self.possibleEnpassant = ((move.startRow + move.endRow) // 2, move.startCol)
            else:
                self.possibleEnpassant = ()

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:    # Kingside Castle
                    self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]   # Rook move
                    self.board[move.endRow][move.endCol+1] = "--"   # Removes Rook from original tile
                else:   # Queenside Castle
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                    self.board[move.endRow][move.endCol-2] = "--"

            self.updateCastleRights(move)
            self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                                     self.currentCastlingRights.wQs, self.currentCastlingRights.bQs))

    def undoMove(self):
        if len(self.moveLog) != 0:      # finds out if there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove     # switches player's turn
            # Update the position of the King's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # Leave ending tile blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.possibleEnpassant = (move.endRow, move.endCol)
            # Undo a 2 tiles pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.possibleEnpassant = ()
            # Undo castling rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wKs, newRights.bKs, newRights.wQs, newRights.bQs)
            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:    # Kingside Castle
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:   # Queenside Castle
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wKs = False
            self.currentCastlingRights.wQs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bKs = False
            self.currentCastlingRights.bQs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wQs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wKs = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bQs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bKs = False
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wQs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wKs = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bQs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bKs = False

    def getValidMoves(self):
        temp_possibleEnpassant = self.possibleEnpassant
        temp_castlingRights = CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                            self.currentCastlingRights.wQs, self.currentCastlingRights.bQs)
        # All legal moves
        # generale all possible moves
        moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)


        # for each move make the move
        for i in range(len(moves)-1, -1, -1):  # When removing from a list go backwards through list to avoid skipping elements in list
            self.makeMove(moves[i])
        # for all opponent's moves, see if the king is under attack
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("Checkmate!")
            else:
                self.staleMate = True
                print("Stalemate")
        else:
            self.checkMate = False
            self.staleMate = False

        self.possibleEnpassant = temp_possibleEnpassant
        self.currentCastlingRights = temp_castlingRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.tileUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.tileUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def tileUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c:    # Tile under attack
                return True
        return False

    def getPossibleMoves(self):
        # All possible moves (this means that it does not consider exposing the king to checks)
        moves = []
        for r in range(len(self.board)):    # Number of rows
            for c in range(len(self.board[r])):     # Number of columns in a given row
                turn = self.board[r][c][0]
                if turn == "w" and self.whiteToMove or turn == "b" and not self.whiteToMove:
                    piece = self.board[r][c][1]
                    if piece == "p":
                        self.getPawnMoves(r, c, moves)
                    elif piece == "R":
                        self.getRookMoves(r, c, moves)
                    elif piece == "N":
                        self.getKnightMoves(r, c, moves)
                    elif piece == "B":
                        self.getBishopMoves(r, c, moves)
                    elif piece == "Q":
                        self.getQueenMoves(r, c, moves)
                    elif piece == "K":
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove and self.board[r][c][0] == "w":
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0 and self.board[r-1][c-1][0] == "b":  # checks if on the diagonal left tile there is a black piece to capture
                moves.append(Move((r, c), (r-1, c-1), self.board))
            elif c-1 >= 0 and (r-1, c-1) == self.possibleEnpassant:
                moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c+1 <= 7 and self.board[r-1][c+1][0] == "b":
                moves.append(Move((r, c), (r-1, c+1), self.board))
            elif c-1 >= 0 and (r-1, c+1) == self.possibleEnpassant:
                moves.append(Move((r, c), (r - 1, c+1), self.board, isEnpassantMove=True))

        elif not self.whiteToMove and self.board[r][c][0] == "b":
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0 and self.board[r+1][c-1][0] == "w":   # checks if on the diagonal left tile there is a black piece to capture
                moves.append(Move((r, c), (r+1, c-1), self.board))
            elif c-1 >= 0 and (r+1, c-1) == self.possibleEnpassant:
                moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7 and self.board[r+1][c+1][0] == "w":
                moves.append(Move((r, c), (r+1, c+1), self.board))
            elif c-1 >= 0 and (r+1, c+1) == self.possibleEnpassant:
                moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break   # Rook stops before friendly piece
                else:
                    break   # Rook reaches end of the board

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] == enemyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # Bishop stops before friendly piece
                else:
                    break  # Bishop reaches end of the board

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow <= 7 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] == enemyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getCastleMoves(self, r, c, moves):
        if self.tileUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wKs) or (not self.whiteToMove and self.currentCastlingRights.bKs):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wQs) or (not self.whiteToMove and self.currentCastlingRights.bQs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.tileUnderAttack(r, c+1) and not self.tileUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.tileUnderAttack(r, c-1) and not self.tileUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wKs, bKs, wQs, bQs):
        self.wKs = wKs
        self.bKs = bKs
        self.wQs = wQs
        self.bQs = bQs


class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToColumns = {"a": 0, "b": 1, "c": 2, "d": 3,
                      "e": 4, "f": 5, "g": 6, "h": 7}
    columnsToFiles = {v: k for k, v in filesToColumns.items()}

    def __init__(self, startTile, endTile, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startTile[0]
        self.startCol = startTile[1]
        self.endRow = endTile[0]
        self.endCol = endTile[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0 or self.pieceMoved == "bp" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.columnsToFiles[c] + self.rowsToRanks[r]
