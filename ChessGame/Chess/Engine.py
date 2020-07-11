class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves
                              , 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteTurn = True
        self.moveLog = [] #Log to make undo's possible
        self.wKingLocation = (7, 4)
        self.bKingLocation = (0, 4)
        self.inCheck = False
        self.checkMate = False
        self.staleMate = False
        self.pins = [] #Keeps track of pieces that are pinned and cannot be moved or else result in checkmate
        self.checks = []
        self.enPassantSq = ()
        self.currCastlingRights = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currCastlingRights.wKS, self.currCastlingRights.wQS, self.currCastlingRights.bKS, self.currCastlingRights.bQS,)]


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteTurn = not self.whiteTurn #Switch turns every move
        #Keep track of both kings position for checkmate purposes
        if move.pieceMoved == "wK":
            self.wKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.bKingLocation = (move.endRow, move.endCol)
        #Enpassant move
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantSq = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enPassantSq = ()
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        #PawnPromotion move
        if move.pawnPromotion:
            promotionChoice = input("Promote to Q, R, B, or N:")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotionChoice.upper()

        #Castling
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(self.currCastlingRights.wKS, self.currCastlingRights.wQS, self.currCastlingRights.bKS, self.currCastlingRights.bQS,))

        if move.castleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'


    def unndoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceTaken
            self.whiteTurn = not self.whiteTurn

            if move.pieceMoved == "wK":
                self.wKingLocation = (move.endRow, move.endCol)
            if move.pieceMoved == "bK":
                self.bKingLocation = (move.endRow, move.endCol)

            if move.enPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceTaken
                self.enPassantSq = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantSq = ()



            self.castleRightsLog.pop()
            nRights = self.castleRightsLog[-1]
            self.currCastlingRights.wKS = nRights.wKS
            self.currCastlingRights.wQS = nRights.wQS
            self.currCastlingRights.bKS = nRights.bKS
            self.currCastlingRights.bQS = nRights.bQS
            if move.castleMove:
                if move.endCol - move.startCol == 2:    #King side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:                                   #Queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'


    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currCastlingRights.wKS = False
            self.currCastlingRights.wQS = False
        elif move.pieceMoved == 'bK':
            self.currCastlingRights.bKS = False
            self.currCastlingRights.bQS = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #Left rook
                    self.currCastlingRights.wQS = False
                elif move.startCol == 7: #Right rook
                    self.currCastlingRights.wKS = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currCastlingRights.bQS = False
                elif move.startCol == 7:
                    self.currCastlingRights.bKS = False



    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteTurn:
            kingRow = self.wKingLocation[0]
            kingCol = self.wKingLocation[1]
        else:
            kingRow = self.bKingLocation[0]
            kingCol = self.bKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #Block the only check or move the king
                moves = self.getPossibleMoves()
                #To block the check, move a piece into the squares between the king and attacker
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #Attacking piece
                validSquares = []
                if pieceChecking[1] == "N": #If Knight, must capture knight or  move king no pins
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                #Remove moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1): #Go backwards through iterating list when removing
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: #In double check king must move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves



    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteTurn:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.wKingLocation[0]
            startCol = self.wKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.bKingLocation[0]
            startCol = self.bKingLocation[1]
        #Start from king position, checking for possible attacks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #Second ally piece meaning no threat is possible
                            break
                    elif endPiece[0] == enemyColor:
                        enemyAttacking = endPiece[1]
                        #Account for all possible attackers
                        if (0 <= j <= 3 and enemyAttacking == "R") or \
                                (4 <= j <= 7 and enemyAttacking == "B") or \
                                (i == 1 and enemyAttacking == "p" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4<= j <= 5))) or \
                                (enemyAttacking == "Q") or (i == 1 and enemyAttacking == "K"):
                            if possiblePin == (): #No pins, therefore in check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #Pinned piece
                                pins.append(possiblePin)
                                break
                        else: #No check applied
                            break
                else: #Off board
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0<= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks


    def sqUnderAttack(self, startRow, startCol, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        enemyAttacking = endPiece[1]
                        if (0 <= j <= 3 and enemyAttacking == "R") or \
                                (4 <= j <= 7 and enemyAttacking == "B") or \
                                (i == 1 and enemyAttacking == "p" and (
                                        (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (enemyAttacking == "Q") or (i == 1 and enemyAttacking == "K"):
                            return True
                        else:
                             break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    return True

        return False


    def getPossibleMoves(self):
        moves =[]
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                turn = self.board[i][j][0]
                if (turn == "w" and self.whiteTurn) or (turn == "b" and not self.whiteTurn):
                    piece = self.board[i][j][1]
                    self.moveFunctions[piece](i, j, moves)
        return moves


    def getPawnMoves(self, i, j, moves):
        pinned = False
        pinDirection = ()
        for k in range(len(self.pins)-1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                pinned = True
                pinDirection = (self.pins[k][2], self.pins[k][3])
                self.pins.remove(self.pins[k])
                break
        pawnPromotion = False
        if self.whiteTurn:
            if self.board[i-1][j] == "--":
                if not pinned or pinDirection == (-1, 0):
                    if i-1 == 0:
                        pawnPromotion = True
                    moves.append(Move((i, j), (i-1, j), self.board, pawnPromotion=pawnPromotion))
                    if i == 6 and self.board[i-2][j] == "--":
                        moves.append(Move((i, j), (i-2, j), self.board))
            if j-1 >= 0:
                if not pinned or pinDirection == (-1, -1):
                    if self.board[i -1][j-1][0] == 'b':
                        if i -1 == 0:
                            pawnPromotion = True
                        moves.append(Move((i, j), (i -1, j-1), self.board, pawnPromotion=pawnPromotion))
                    if (i -1, j - 1) == self.enPassantSq:
                        moves.append(Move((i, j), (i -1, j - 1), self.board, enPassant=True))
            if j+1 <= 7:
                if not pinned or pinDirection == (-1, 1):
                    if self.board[i -1][j + 1][0] == 'b':
                        if i -1 == 0:
                            pawnPromotion = True
                        moves.append(Move((i, j), (i -1, j+1), self.board, pawnPromotion=pawnPromotion))
                    if (i -1, j + 1) == self.enPassantSq:
                        moves.append(Move((i, j), (i -1, j + 1), self.board, enPassant=True))

        if not self.whiteTurn:
            if self.board[i+1][j] == "--":
                if not pinned or pinDirection == (1, 0):
                    if i+1 == 7:
                        pawnPromotion = True
                    moves.append(Move((i, j), (i+1, j), self.board, pawnPromotion=pawnPromotion))
                    if i == 1 and self.board[i+2][j] == "--":
                        moves.append(Move((i, j), (i+2, j), self.board))
            if j-1 >= 0:
                if not pinned or pinDirection == (1, -1):
                    if self.board[i +1][j-1][0] == 'w':
                        if i +1 == 7:
                            pawnPromotion = True
                        moves.append(Move((i, j), (i +1, j-1), self.board, pawnPromotion=pawnPromotion))
                    if (i +1, j - 1) == self.enPassantSq:
                        moves.append(Move((i, j), (i +1, j - 1), self.board, enPassant=True))
            if j+1 <= 7:
                if not pinned or pinDirection == (1, 1):
                    if self.board[i +1][j + 1][0] == 'w':
                        if i +1 == 7:
                            pawnPromotion = True
                        moves.append(Move((i, j), (i +1, j+1), self.board, pawnPromotion=pawnPromotion))
                    if (i +1, j + 1) == self.enPassantSq:
                        moves.append(Move((i, j), (i +1, j + 1), self.board, enPassant=True))


    def getRookMoves(self, i, j, moves):
        pinned = False
        pinDirection = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                pinned = True
                pinDirection = (self.pins[k][2], self.pins[k][3])
                if self.board[i][j][1] != 'Q':
                    self.pins.remove(self.pins[k])
                break

        if self.whiteTurn:
            enemy = "b"
        if not self.whiteTurn:
            enemy = "w"
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1)) #up, down, left, right
        for d in directions:
            for k in range(1,8):
                endRow = i + (d[0] * k)
                endCol = j + (d[1] * k)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not pinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((i, j), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy:
                            moves.append(Move((i, j), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break


    def getKnightMoves(self, i, j, moves):
        pinned = False
        pinDirection = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                pinned = True
                self.pins.remove(self.pins[k])
                break

        possibleMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (2, -1), (2, 1))
        if self.whiteTurn:
            ally = "w"
        if not self.whiteTurn:
            ally = "b"
        for mov in possibleMoves:
            endRow = i + mov[0]
            endCol = j + mov[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not pinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ally:
                        moves.append(Move((i, j), (endRow, endCol), self.board))


    def getBishopMoves(self, i, j, moves):
        pinned = False
        pinDirection = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                pinned = True
                pinDirection = (self.pins[k][2], self.pins[k][3])
                self.pins.remove(self.pins[k])
                break
        if self.whiteTurn:
            enemy = "b"
        if not self.whiteTurn:
            enemy = "w"
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #diag topleft, diag topright, diag botleft, diag botright
        for d in directions:
            for k in range(1,8):
                endRow = i + (d[0] * k)
                endCol = j + (d[1] * k)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not pinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((i, j), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy:
                            moves.append(Move((i, j), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break


    def getQueenMoves(self, i, j, moves):
        self.getRookMoves(i, j, moves)
        self.getBishopMoves(i, j, moves)


    def getKingMoves(self, i, j, moves):
        possibleMoves = ((0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1))
        if self.whiteTurn:
            ally = "w"
        if not self.whiteTurn:
            ally = "b"
        for k in range(8):
            endRow = i + possibleMoves[k][0]
            endCol = j + possibleMoves[k][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally:
                    if ally == "w":
                        self.wKingLocation = (endRow, endCol)
                    else:
                        self.bKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((i, j), (endRow, endCol), self.board))
                    if ally == 'w':
                        self.wKingLocation = (i, j)
                    else:
                        self.bKingLocation = (i, j)
        self.getCastleMoves(i, j, moves, ally)


    def getCastleMoves(self, i, j, moves, ally):
        if self.sqUnderAttack(i, j, ally):
            return
        if (self.whiteTurn and self.currCastlingRights.wKS) or (not self.whiteTurn and self.currCastlingRights.bKS):
            self.getKSCastleMoves(i, j, moves, ally)
        if (self.whiteTurn and self.currCastlingRights.wQS) or (not self.whiteTurn and self.currCastlingRights.bQS):
            self.getQSCastleMoves(i, j, moves, ally)


    def getKSCastleMoves(self, i, j, moves, ally):
        if self.board[i][j+1] == '--' and self.board[i][j+2] == '--' and not self.sqUnderAttack(i, j+1, ally) and not self.sqUnderAttack(i, j+2, ally):
            moves.append(Move((i, j), (i, j+2), self.board, castleMove=True))

    def getQSCastleMoves(self, i, j, moves, ally):
        if self.board[i][j-1] == '--' and self.board[i][j-2] == '--' and self.board[i][j-3] == '--' and not self.sqUnderAttack(i, j-1, ally) and not self.sqUnderAttack(i, j-2, ally):
            moves.append(Move((i, j), (i, j-2), self.board, castleMove=True))



class castleRights():
    def __init__(self, wKS, bKS, wQS, bQS):
        self.wKS = wKS
        self.bKS = bKS
        self.wQS = wQS
        self.bQS = bQS

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant=False, pawnPromotion=False, castleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceTaken = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        self.castleMove = castleMove
        if enPassant:
            self.pieceTaken = 'bp' if self.pieceMoved == 'wp' else 'wp'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow *10 + self.endCol


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]