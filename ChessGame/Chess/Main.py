import pygame as p
from Chess import Engine


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

#Makes a dictionary containing all the piece images.
def LoadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR", "bp", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


#Main function that will handle user input, updating board, etc.
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    LoadImages() #Images only loaded once
    running = True
    sqSelected = ()
    currentMove = [] #Keep track of starting and ending square coordinates
    gameOver = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Moving pieces
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): #Player clicked same square twice, reset move.
                        sqSelected = ()
                        currentMove = []
                    else:
                        sqSelected = (row, col)
                        currentMove.append(sqSelected)
                    #Checks to see if move is valid
                    if len(currentMove) == 2:
                        move = Engine.Move(currentMove[0], currentMove[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                currentMove = []
                        if not moveMade:
                            currentMove = [sqSelected]

            elif e.type == p.KEYDOWN:
                #Undo move using "z"
                if e.key == p.K_z:
                    gs.unndoMove()
                    moveMade = True
                    #Don't animate when undoing
                    animate = False
                #Reset board using "r"
                if e.key == p.K_r:
                    gs = Engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                moveAnimation(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteTurn:
                drawText(screen, 'Black Wins By Checkmate')
            else:
                drawText(screen, 'White Wns By Checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


#Highlights the possible moves for the current selected piece
def highlight(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        i, j = sqSelected
        if gs.board[i][j][0] == ('w' if gs.whiteTurn else 'b'): #Makes sure piece selected is valid piece
            #Highlight selected piece
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (j*SQ_SIZE, i*SQ_SIZE))
            #Highlight the possible moves for that piece
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == i and move.startCol == j:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i+j)%2)]
            p.draw.rect(screen, color, p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlight(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def moveAnimation(move, screen, board, clock):
    global colors
    deltaR = move.endRow - move.startRow
    deltaC = move.endCol - move.startCol
    framesPS = 7                                              #Speed of the animation
    frameCount = (abs(deltaR) + abs(deltaC)) * framesPS       #Makes the speed consistent based on move distance
    for frame in range(frameCount + 1):
        i, j = (move.startRow + deltaR*frame/frameCount, move.startCol + deltaC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #Remove piece from ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSq = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSq)
        #Put back piece taken
        if move.pieceTaken != '--':
            screen.blit(IMAGES[move.pieceTaken], endSq)
        #Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


#Text function for Checkmate/Stalemate
def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObj = font.render(text, 0, p.Color('Grey'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, 0, p.Color('Black'))
    screen.blit(textObj, textLocation.move(2,2))


if __name__ == "__main__":
    main()