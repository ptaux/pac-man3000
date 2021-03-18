import chess
import chess.polyglot
import time
from operator import itemgetter  

class Engine:
    def __init__(self, board):
        self.board = board
        self.pawnValue = 100
        self.knightValue = 280
        self.bishopValue = 320
        self.rookValue = 479
        self.queenValue = 929 
        self.kingValue = 60000

        self.mobilityValue = 10
        self.bishop_pair_value = 50
        self.pawn_penalty = 50

        self.kingsideCastleBonus = 250
        self.queensideCastleBonus = 200

        self.pawntable = [
        0,   0,   0,   0,   0,   0,   0,   0,
            78,  83,  86,  73, 102,  82,  85,  90,
             7,  29,  21,  44,  40,  31,  44,   7,
           -17,  16,  -2,  15,  14,   0,  15, -13,
           -26,   3,  10,   9,   6,   1,   0, -23,
           -22,   9,   5, -11, -10,  -2,   3, -19,
           -31,   8,  -7, -37, -36, -14,   3, -31,
             0,   0,   0,   0,   0,   0,   0,   0]

        self.knightstable = [
        -66, -53, -75, -75, -10, -55, -58, -70,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
            10,  67,   1,  74,  73,  27,  62,  -2,
            24,  24,  45,  37,  33,  41,  25,  17,
            -1,   5,  31,  21,  22,  35,   2,   0,
           -18,  10,  13,  22,  18,  15,  11, -14,
           -23, -15,   2,   0,   2,   0, -23, -20,
           -74, -23, -26, -24, -19, -35, -22, -69]

        self.bishopstable = [
        -59, -78, -82, -76, -23,-107, -37, -50,
           -11,  20,  35, -42, -39,  31,   2, -22,
            -9,  39, -32,  41,  52, -10,  28, -14,
            25,  17,  20,  34,  26,  25,  15,  10,
            13,  10,  17,  23,  17,  16,   0,   7,
            14,  25,  24,  15,   8,  25,  20,  15,
            19,  20,  11,   6,   7,   6,  20,  16,
            -7,   2, -15, -12, -14, -15, -10, -10]

        self.rookstable = [
        35,  29,  33,   4,  37,  33,  56,  50,
            55,  29,  56,  67,  55,  62,  34,  60,
            19,  35,  28,  33,  45,  27,  25,  15,
             0,   5,  16,  13,  18,  -4,  -9,  -6,
           -28, -35, -16, -21, -13, -29, -46, -30,
           -42, -28, -42, -25, -25, -35, -26, -46,
           -53, -38, -31, -26, -29, -43, -44, -53,
           -30, -24, -18,   5,  -2, -18, -31, -32]

        self.queenstable = [
        6,   1,  -8,-104,  69,  24,  88,  26,
            14,  32,  60, -10,  20,  76,  57,  24,
            -2,  43,  32,  60,  72,  63,  43,   2,
             1, -16,  22,  17,  25,  20, -13,  -6,
           -14, -15,  -2,  -5,  -1, -10, -20, -22,
           -30,  -6, -13, -11, -16, -11, -16, -27,
           -36, -18,   0, -19, -15, -15, -21, -38,
           -39, -30, -31, -13, -31, -36, -34, -42]

        self.kingstable = [
         4,  54,  47, -99, -99,  60,  83, -62,
           -32,  10,  55,  56,  56,  55,  10,   3,
           -62,  12, -57,  44, -67,  28,  37, -31,
           -55,  50,  11,  -4, -19,  13,   0, -49,
           -55, -43, -52, -28, -51, -47,  -8, -50,
           -47, -42, -43, -79, -64, -32, -29, -32,
            -4,   3, -14, -50, -57, -18,  13,   4,
            17,  30,  -3, -14,   6,  -1,  40,  18]

        self.transposition = {}

        self.pieceValues = {
            1: self.pawnValue,
            2: self.knightValue,
            3: self.bishopValue,
            4: self.rookValue,
            5: self.queenValue,
            6: self.kingValue
        }

        self.tables = {
            1: self.pawntable,
            2: self.knightstable,
            3: self.bishopstable,
            4: self.rookstable,
            5: self.queenstable,
            6: self.kingstable
        }

    def Evaluate(self):
        hash = chess.polyglot.zobrist_hash(self.board)
        if hash in self.transposition:
            eval = self.transposition.get(hash)[0]
            return eval
        else:
            if self.board.is_game_over():
                return self.getGameOver()

            material = self.CountMaterial(chess.WHITE) - self.CountMaterial(chess.BLACK)
            mobility = self.CountMobility(chess.WHITE) - self.CountMobility(chess.BLACK)
            pieceSquares = self.CountPieceSquares(chess.WHITE) - self.CountPieceSquares(chess.BLACK)
            bishop_pair = self.CountBishopPair(chess.WHITE) - self.CountBishopPair(chess.BLACK)
            pawn_structure = self.CountPawnStructure(chess.WHITE) - self.CountPawnStructure(chess.BLACK)

            toPlay = 1 if self.board.turn == chess.WHITE else -1

            eval = ( material + mobility + pieceSquares + bishop_pair + pawn_structure) * toPlay

            self.transposition.update({hash : [eval, self.board.ply()]})

            return eval

    def QuickEvaluate(self):

        hash = chess.polyglot.zobrist_hash(self.board)

        if hash in self.transposition:
            eval = self.transposition.get(hash)[0]
            return eval
        else:
            if self.board.is_game_over():
                return self.getGameOver()

            whiteMaterial = self.CountMaterial(chess.WHITE)
            blackMaterial = self.CountMaterial(chess.BLACK)

            material = whiteMaterial - blackMaterial

            toPlay = 1 if self.board.turn == chess.WHITE else -1

            eval = material * toPlay

            self.transposition.update({hash : [eval, self.board.ply()]})

            return eval

    def getGameOver(self):
        if self.board.is_checkmate():
            if self.board.turn:
                return -9999 #LOSS
            else:
                return 9999 #WIN
        if self.board.is_stalemate():
            return 0 #DRAW
        if self.board.is_insufficient_material():
            return 0 #DRAW
        if self.board.can_claim_draw():
            return 0 #DRAW

    def CountMaterial(self, colour):
        p = len(self.board.pieces(chess.PAWN, colour)) #NUMBER OF PAWNS
        n = len(self.board.pieces(chess.KNIGHT, colour)) #NUMBER OF KNIGHTS
        b = len(self.board.pieces(chess.BISHOP, colour)) #NUMBER OF BISHOPS
        r = len(self.board.pieces(chess.ROOK, colour)) #NUMBER OF ROOKS
        q = len(self.board.pieces(chess.QUEEN, colour)) #NUMBER OF QUEENS

        material = p*self.pawnValue + n*self.knightValue + b*self.bishopValue + r*self.rookValue + q*self.queenValue

        return material

    def CountMobility(self, colour):

        if self.board.turn == colour:
            m = self.board.legal_moves.count()
        else:
            self.board.push(chess.Move.null())
            m = self.board.legal_moves.count()
            self.board.pop()
        
        mobility = m * self.mobilityValue

        return mobility

    def CountPieceSquares(self, colour):

        if colour == chess.WHITE:
            pawnsq = sum([self.pawntable[i] for i in self.board.pieces(chess.PAWN, chess.WHITE)])
            knightsq = sum([self.knightstable[i] for i in self.board.pieces(chess.KNIGHT, chess.WHITE)])
            bishopsq= sum([self.bishopstable[i] for i in self.board.pieces(chess.BISHOP, chess.WHITE)])
            rooksq = sum([self.rookstable[i] for i in self.board.pieces(chess.ROOK, chess.WHITE)]) 
            queensq = sum([self.queenstable[i] for i in self.board.pieces(chess.QUEEN, chess.WHITE)]) 
            kingsq = sum([self.kingstable[i] for i in self.board.pieces(chess.KING, chess.WHITE)]) 

            piece_squares = pawnsq + knightsq + bishopsq+ rooksq+ queensq + kingsq
            return piece_squares
        else:
            pawnsq = sum([self.pawntable[chess.square_mirror(i)] for i in self.board.pieces(chess.PAWN, chess.BLACK)])
            knightsq = sum([self.knightstable[chess.square_mirror(i)] for i in self.board.pieces(chess.KNIGHT, chess.BLACK)])
            bishopsq= sum([self.bishopstable[chess.square_mirror(i)] for i in self.board.pieces(chess.BISHOP, chess.BLACK)])
            rooksq = sum([self.rookstable[chess.square_mirror(i)] for i in self.board.pieces(chess.ROOK, chess.BLACK)])
            queensq = sum([self.queenstable[chess.square_mirror(i)] for i in self.board.pieces(chess.QUEEN, chess.BLACK)])
            kingsq = sum([self.kingstable[chess.square_mirror(i)] for i in self.board.pieces(chess.KING, chess.BLACK)])

            piece_squares = pawnsq + knightsq + bishopsq+ rooksq+ queensq + kingsq
            return piece_squares

    def CountBishopPair(self, colour):
        if len(self.board.pieces(chess.BISHOP, colour)) == 2:
            return self.bishop_pair_value
        else:
             return 0

    def CountPawnStructure(self, colour):
        p = len(self.board.pieces(chess.PAWN, colour))

        #Pawn structure: doubled pawns are given a penalty. Adds up all pawns on unique files, subtracts that from total pawns to get number of doubled pawns
        pawns = list(self.board.pieces(chess.PAWN, colour))
        files = []
        for i in pawns:
            i = chess.square_file(i)
            files.append(i)
        f = set(files)
        n = len(f)
        bad_pawns = (p-n) ** 2 #Raised to power of 2 so that each subsequent doubled pawn adds extra penalty

        pawn_structure = bad_pawns * self.pawn_penalty

        return pawn_structure

    def Search(self, depth, alpha, beta, last_best):

        if depth == 0:
            return self.SearchAllCaptures(alpha, beta, last_best)

        moves = self.OrderMoves(last_best)

        moveCount = len(moves)

        if moveCount == 0:
            if self.board.is_checkmate:
                return -9999
            else:
                return 0

        for move in moves:
            self.board.push(move)
            eval = -self.Search(depth-1, -beta, -alpha, last_best)
            self.board.pop()
            if eval >= beta:
                return beta
            else:
                alpha = max(alpha, eval)
        
        return alpha

    def SearchAllCaptures(self, alpha, beta, last_best):

        eval = self.Evaluate()

        if eval >= beta:
            return beta
        else:
            alpha = max(alpha, eval)

        moves = self.OrderMoves(last_best)

        for move in moves:
            if self.board.is_capture(move):
                self.board.push(move)
                eval = -self.SearchAllCaptures(-beta, -alpha, last_best)
                self.board.pop()
                if eval >= beta:
                    return beta
                else:
                    alpha = max(alpha, eval)
        return alpha

    def iterative_search(self, depth):
        d = 1
        last_best = chess.Move.null()
        while d <= depth:
            if self.board.is_game_over():
                return last_best
                break
            else:
                last_best = self.SelectMove(d, last_best)
                d += 1
        print(len(self.transposition))
        delete = []
        for key, value in self.transposition.items():
            if value[1] < self.board.ply() - depth:
                delete.append(key)
        for i in delete:
            del self.transposition[i]
        print(len(self.transposition))
        return last_best

    def OrderMoves(self, last_best):

        ordering = {}

        moves = self.board.legal_moves

        for move in moves:

            moveScoreEstimate = 0

            if move == last_best:
                moveScoreEstimate += 9999
            else:
                toSquare = move.to_square
                fromSquare = move.from_square
                movePieceType = self.board.piece_type_at(fromSquare)
                if self.board.is_capture(move):
                    if self.board.is_en_passant(move):
                        moveScoreEstimate += 100
                    else:
                        capturePieceType = self.board.piece_type_at(toSquare)
                        moveScoreEstimate += self.pieceValues.get(capturePieceType) - (self.pieceValues.get(movePieceType)/100)
                if move.promotion != None:
                    moveScoreEstimate += 1000
            ordering.update({move: moveScoreEstimate})

        ordered_list = []

        for key, value in sorted(ordering.items(), key = itemgetter(1), reverse = True):
            ordered_list.append(key)

        return ordered_list

    def SelectMove(self, depth, last_best):

        tic = time.perf_counter()

        try:
            bestMove = chess.polyglot.MemoryMappedReader("Perfect2017.bin").weighted_choice(self.board).move

            toc = time.perf_counter()

            t = toc-tic

            print(f"Selected move in {t:0.4f} seconds")

            return bestMove
        except:

            bestMove = chess.Move.null()
            bestValue = -99999
            alpha = -100000
            beta = 100000

            print("Selecting move... Depth = " + str(depth))

            moves = self.OrderMoves(chess.Move.null())

            for move in moves:
                self.board.push(move)
                boardValue = -self.Search(depth-1, -beta, -alpha, last_best)
                if boardValue > bestValue:
                    bestValue = boardValue
                    bestMove = move
                if( boardValue > alpha ):
                    alpha = boardValue
                self.board.pop()

            toc = time.perf_counter()

            t = toc-tic

            print(f"Selected move in {t:0.4f} seconds")

            return bestMove

def engineMove(playerIsWhite):
    if board.is_game_over():
        if playerIsWhite:
            print("Checkmate. White wins the game.")
            return
        else:
            print("Checkmate. Black wins the game.")
            return
    else:
        mov = bot.new_iterative_search(3)

        board.pop()

        x = board.san(mov)

        board.push(mov)

        if playerIsWhite:
            print("..." + str(x))
        else:
            print(str(board.fullmove_number) + ". " + str(x)) 

def getValidMoveInput():
    while True:
        try:
            move = input("Enter your move: ")
            if board.parse_san(move) not in board.legal_moves:
                print(move + " is not a legal move.")
                continue
            else:
                break
        except ValueError:
            print(move + " is not a legal move.")
            continue
    return board.parse_san(move)

def playerMove(playerIsWhite):
    if board.is_game_over():
        if playerIsWhite:
            print("Checkmate. Black wins the game.")
            return
        else:
            print("Checkmate. White wins the game.")
            return
    else:
        move = getValidMoveInput()

        if playerIsWhite:
            print(str(board.fullmove_number) + ". " + str(board.san(move)))
        else:
            print("..." + str(board.san(move)))

        board.push(move)

def playGame():

    board.reset_board()

    while True:
        try:
            playerColour = input("Please choose your colour (w/b): ")
            print()
            if playerColour != "w" and playerColour != "b":
                print("Please choose your colour (w/b): ")
                print()
                continue
            else:
                if playerColour == "w":
                    playerIsWhite = True
                    print("WHITE")
                else:
                    playerIsWhite = False
                    print("BLACK")
            break
        except ValueError:
            print("Please choose your colour (w/b): ")
            print()
            continue

    while (board.is_game_over() == False):
        if playerIsWhite:
            playerMove(playerIsWhite)
            engineMove(playerIsWhite)
        else:
            engineMove(playerIsWhite)
            playerMove(playerIsWhite)

"""

board = chess.Board()
bot = Engine(board)
playGame()

"""

board = chess.Board("r1r5/1p6/p3RPp1/1kn3Q1/1q1pp3/P7/1PPn1PP1/R2N2K1 b - - 0 29")

bot = Engine(board)

#print(bot.iterative_search(4))


tic = time.perf_counter()

bot.OrderMoves(chess.Move.null())

toc = time.perf_counter()

t = toc-tic

print(f"Completed function in {t:0.5f} seconds")
