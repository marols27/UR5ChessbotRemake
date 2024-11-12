import copy
import chess
import chess.engine


class Engine:
    # CLASS DOCUMENTATION:
    # This class is made to return the best move, specify the oponent dificulty and other chess engine properties.


    def __init__(self):
        engine = chess.engine.SimpleEngine.popen_uci(r"./stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/src/stockfish") 



class Engine01:
    def __init__(self, board, maxDepth, color):
        self.board = board
        self.maxDepth = maxDepth
        self.color = color
    
    def mateOpportunity(self):
        if (self.legal_moves.count() == 0):
            if (self.board.turn == self.color):
                return -999
            else:
                return 999
        else:
            return 0
    
    #def openning(self):

    def squareResidentPoints(self, square):
        pieceValue = 0
        if (self.board.piece_type_at(square) == chess.PAWN):
            pieceValue = 1
        elif (self.board.piece_type_at(square) == chess.ROOK):
            pieceValue = 5.1
        elif (self.board.piece_type_at(square) == chess.KNIGHT):
            pieceValue = 3.33
        elif (self.board.piece_type_at(square) == chess.BISHOP):
            pieceValue = 3.2
        elif (self.board.piece_type_at(square) == chess.QUEEN):
            pieceValue = 8.8
        return pieceValue 

    def engine(self, candidate, depth):
        listOfMoves = list(self.board.legal_moves)

        if (depth == self.maxDepth or listOfMoves.count() == 0):
            return self.evalBoard()
        else:
            newCandidate = None
            if (depth % 2 != 0):
                newCandidate = float("-inf")
            else:
                newCandidate = float("inf")

        for i in listOfMoves: 
            self.board.push(i)
            value = self.engine(newCandidate, depth+1)

            # Minmaxing:
            # maximizing algorythm:
            if (value > newCandidate and depth % 2 != 0):
                newCandidate = value
                if (depth == 1):
                    move = i
            # minimizing algorythm:
            elif (value < newCandidate and depth % 2 == 0):
                newCandidate = value

            # Alpha beta pruning:
            if (candidate != None and value < candidate and depth % 2 == 0):
                self.board.pop()
                break
            elif (candidate != None and value > candidate and depth % 2 != 0):
                self.board.pop()
                break
        
        if (depth > 1):
            return newCandidate
        if (depth == 1):
            return move
    