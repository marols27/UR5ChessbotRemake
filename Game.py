from Board import Board
import chess
import chess.engine
import chess.pgn
from DGTBoard import DGTBoard
from flask_socketio import SocketIO
from ToolCenterPoint import ToolCenterPoint as TCP
from UR5Robot import UR5Robot
import json
from playsound import playsound

class Game:
    """
    ### A class for handling the game loop of a chess game, and to handle the turn cycle.

    ### FIELDS:

    """

    robot = None
    dgtBoard = None
    board = None
    engine = None
    gameInfo = None
    capturePos = None
    timeout = None

    difficulty = None
    color = None
    move = None
    

    def __init__(self, robot: UR5Robot, dgtBoard: DGTBoard, board: Board, engine: chess.engine.SimpleEngine, gameInfo: chess.pgn.Game, capturePos: TCP, timeout: chess.engine.Limit, difficulty: int, color: bool) -> None:
        self.robot = robot
        self.dgtBoard = dgtBoard
        self.board = board
        self.engine = engine
        self.gameInfo = gameInfo
        self.capturePos = capturePos
        self.timeout = timeout
        self.difficulty = difficulty
        self.color = color

        
    
    def getPGN(self):
        pgn = self.board.getPGN()
        return pgn

    def playRobotMove(self):
        self.robot.control.reconnect()
        pieceNames = {
            "q": "queen",
            "r": "rook",
            "b": "bishop",
            "n": "knight"
        }
        files = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5,
            "f": 6,
            "g": 7,
            "h": 8
        }
        liveBoard = self.dgtBoard.getCurentBoard()
        liveBoard = self.dgtBoard.getCurentBoard() # To make sure it updates
        previousBoard = str(self.board.board)
        result = self.engine.play(self.board.board, self.timeout)
        self.move = str(result.move)
        self.board.push(result.move)
        self.turn = self.board.turn
        move = self.board.getMoveTCPByUCI(str(result.move), previousBoard)
        # self.board.getMoveTCPByUCI() is a dictionary with the structure:
        # {
        #     "moveType": str,            # A move description
        #     "fromPos": TCP,             # The move from pos
        #     "toPos": TCP,               # The move to pos
        #     "enPassantTarget": TCP,     # The captured pawn during enPassant
        #     "castleFrom": TCP,          # The rooks from pos when castling
        #     "castleTo": TCP,            # The rooks to pos when castling
        #     "promotionPiece": str       # The piece to promote to when a pawn is promoted
        # }
        # And the different move types are:
        #  - "capturePromotion",
        #  - "promotion",
        #  - "enPassant",
        #  - "castle",
        #  - "capture",
        #  - "move"
        if move["type"] == "move":
            self.robot.movePiece(move["fromPos"].TCP, move["toPos"].TCP)
        elif move["type"] == "capture":
            self.robot.capturePiece(move["fromPos"].TCP, move["toPos"].TCP, self.capturePos.TCP)
        elif move["type"] == "enPassant":
            self.robot.enPassent(move["fromPos"].TCP, move["toPos"].TCP, move["enPassantTarget"].TCP, self.capturePos.TCP)
        elif move["type"] == "castle":
            self.robot.castle(move["fromPos"].TCP, move["toPos"].TCP, move["castleFrom"].TCP, move["castleTo"].TCP)
        elif move["type"] == "promotion":
            self.robot.promotion(move["fromPos"].TCP, move["toPos"].TCP)
            targetSquare = liveBoard[int(str(result.move)[4])][files[str(result.move)[3]] - 1]
            while targetSquare != move["promotionPiece"]:
                piece = pieceNames[move["promotionPiece"]]
                input(f"Please place a {'white' if self.turn else 'black'} {piece} at the {result.move[2:4]} square and press enter...")
        elif move["type"] == "capturePromotion":
            self.robot.capturePromotion(move["fromPos"].TCP, move["toPos"].TCP, self.capturePos.TCP)
            targetSquare = liveBoard[int(str(result.move)[4])][files[str(result.move)[3]] - 1]
            while targetSquare != move["promotionPiece"]:
                piece = pieceNames[move["promotionPiece"]]
                input(f"Please place a {'white' if self.turn else 'black'} {piece} at the {result.move[2:4]} square and press enter...")
        else:
            # Move not recognised
            pass
        move = {
            "dgtBoardFEN": self.board.board.board_fen()#,            "PGN": str(self.gameInfo.game())
        }
        self.robot.control.disconnect()
    
    def confirmMove(self, messageCallback):
        oldBoard = self.board
        print(oldBoard)
        updatedBoard = self.dgtBoard.getCurentBoard()
        updatedBoard = self.dgtBoard.getCurentBoard()
        print(updatedBoard)
        move = oldBoard.getUCI(str(updatedBoard))
        if move != None and move in [str(m) for m in oldBoard.board.legal_moves]:
                    print('setting move')
                    self.move = move
                    self.gameInfo.add_variation(chess.Move.from_uci(move))
                    self.board.push(move)
                    self.turn = self.board.turn
                    if self.board.checkMate:
                        messageCallback("You won","Checkmate! Congratulations, you have defeated the chessrobot!")
                    elif self.board.staleMate:
                        messageCallback("It's a draw","Stalemate! The game is a draw!")
                    self.playRobotMove()
                    if  self.board.checkMate:
                        messageCallback("You lost","Checkmate! You have lost to the mighty chessrobot!")
                    elif self.board.staleMate:
                        messageCallback("It's a draw","Stalemate! The game is a draw!")
        else:
            playsound("speechfiles/illegal_move.mp3")
            messageCallback("Illegal move! Please try again.")
        pass
        
    def playerMove(self):
        unTouchedBoard = self.board
        playerHasNotMoved = True
        while playerHasNotMoved:
            updatedBoard = self.dgtBoard.getCurentBoard()
            move = unTouchedBoard.getUCI(str(updatedBoard))
            if move != None and move in [str(m) for m in unTouchedBoard.board.legal_moves]:
                confirmCommand = input(f"Confirm move {move} y/n?")
                if confirmCommand == "y":
                    print('setting move')
                    self.move = move
                    self.gameInfo.add_variation(chess.Move.from_uci(move))
                    self.board.push(move)
                    self.turn = self.board.turn
                    print(self.board.turn)
                    playerHasNotMoved = False
                else:
                    print("Move not confirmed!")

    def runGameLoop(self):
        gameIsRunning = True
        while gameIsRunning:
            if self.board.turn == self.color:
                print("Your turn!")
                self.playerMove()
            else:
                print("Robots turn!")
                self.playRobotMove()

            if self.board.checkMate or self.board.staleMate or self.board.isInsuffichentMaterials:
                gameIsRunning = False
        
        if self.board.checkMate:
            print(f"Checkmate! {'You loose!' if self.board.turn == self.color else 'You win!'}")
        if self.board.staleMate:
            print("Stalemate! It's a draw!")
        if self.board.isInsuffichentMaterials:
            print("Insuffichent materials! It's a draw!")