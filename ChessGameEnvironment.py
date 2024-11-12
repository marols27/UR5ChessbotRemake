import chess.pgn
from Board import Board
import chess
import chess.engine
from DGTBoard import DGTBoard
import json
from ToolCenterPoint import ToolCenterPoint as TCP
from UR5Robot import UR5Robot
import os.path

class ChessGameEnvironment():
    # # DOCUMENTATION:
    # This class consist of the underlying elements that we are using in our settup.
    # this might get changed in the future to be personalizable to the settups that others might have,
    # but for now it consists of the board, robot, captured pieces spot.
    # The plan is to make this class the overall object / class of the entire settup, and make this class
    # handle al the logic between the different elements in the chess playin environments, including the GUI interface
    # we plan to have on a touch screen, next to and included in our system settup.
    
    
    # # FIELDS: 
    # - engine:
    #       An engine using stockfish to return the best move for the current turn.
    # - dgtBoard:      
    #       An object keeping the physical boards conection.
    #
    # - board:
    #       An object that keeps track of the board related components of the environments, 
    #       like the position of the pieces and, legal moves.
    #
    # - robot:
    #       An object that keep track of all info acording the UR5 Robot, 
    #       and the movement functions for easier use in the environment.
    #  
    # - capturePos:
    #       Currently a TCP for dropping of captured pieces. 
    #       The plan is to create a table class to keep track of captured pieces and add pawn promotion functionality for the robot.
    #
    # - pieceNames:
    #       A simple dictionary for translating piece letters to piece names.
    # 
    # - files:
    #       A simple dictionary for translating file letters to numbers for indexing.
    
    # # CONSTRUCTOR:
    # __init__(str fenString):
    #       Normal constructor 
    

    # # EVENT HANDLERS:
    # - onConnected(port): 
    #       Feedback for the dgt board connection.
    # 
    # - onDisconnected(): 
    #       Feedback for the dgt board disconnection.
    #
    # - onBoardChange(): 
    #       Feed for uppdating the board state in the program based on updates from the board.
    #
    # - onConfirmMove():
    #       Updates the game state when the user confirmes his/her move.


    # # METHODS:
    # - strBoardToFenBoard(str board) -> "str":
    #       Expects a board string in the format: 
    #       r n b q k b n r
    #       p p p p p p p p
    #       . . . . . . . .
    #       . . . . . . . .
    #       . . . . . . . .
    #       . . . . . . . .
    #       P P P P P P P P
    #       R N B Q K B N R
    #       And returns the fen representation of the board:
    #       "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    #
    # - strBoardToMatrix(str board) -> "list[list[str]]":
    #       Expects a board string in the format: 
    #       r n b q k b n r
    #       p p p p p p p p
    #       . . . . . . . .
    #       . . . . . . . .
    #       . . . . . . . .
    #       . . . . . . . .
    #       P P P P P P P P
    #       R N B Q K B N R
    #       And returns either a 8 x 8 2 dimentional list in the style:
    #       [
    #           ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], 
    #           ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], 
    #           ['.', '.', '.', '.', '.', '.', '.', '.'], 
    #           ['.', '.', '.', '.', '.', '.', '.', '.'], 
    #           ['.', '.', '.', '.', '.', '.', '.', '.'], 
    #           ['.', '.', '.', '.', '.', '.', '.', '.'], 
    #           ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], 
    #           ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    #       ]
    #       or None if an error ocures or the string length is wrong.
    #
    # - playRobotMove() -> None:
    #       Makes the robot play it's turn.



    # Fields
    dgtBoard = None#DGTBoard()
    pieceNames = {
        "p": "Pawn",
        "r": "Rook",
        "k": "Knight",
        "b": "Bishop",
        "q": "Queen"
    }
    files = {
        "a":1,
        "b":2,
        "c":3,
        "d":4,
        "e":5,
        "f":6,
        "g":7,
        "h":8
        }
    turn = True
    waitingForPlayer = False



    # Constructor:
    def __init__(self, startingFen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        self.engine = chess.engine.SimpleEngine.popen_uci(r"./Rebuild/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/src/stockfish") 
        self.game = chess.pgn.Game()
        self.game.headers["Event"] = "Chess Game"
        self.robot = UR5Robot(Board.tallestPieceHeight)
        self.capturePos = TCP([0.6566121091692373, -0.36140058526616803, 0.30538657582554596, 2.0007589648399895, 2.3521374535970705, 0.005035329574496449])
        boardFeature = self.calibrate()
        self.dgtBoard = DGTBoard()
        self.startingFen = self.strBoardToFenBoard(self.dgtBoard.getCurentBoard()) + " w KQkq - 0 1"
        while self.startingFen != startingFen:
            input("Please place your peces in the corect starting setup and confirm setup...")
            self.startingFen = self.strBoardToFenBoard(self.dgtBoard.getCurentBoard()) + " w KQkq - 0 1" # NB! I could not figure out how to await the response, or variable change.
            self.startingFen = self.strBoardToFenBoard(self.dgtBoard.getCurentBoard()) + " w KQkq - 0 1" # So i did a double get instead, to avoid using sleep.
        print("Board settup has been verified")
        self.board = Board(self.startingFen, boardFeature[0], boardFeature[1], boardFeature[2])
        self.updatingDGTBoard = None
        self.updatingUCI = None
        self.liveBoard = self.strBoardToMatrix(str(self.board))
        self.color = False
        if self.color:
            self.waitingForPlayer = True
        self.turn = self.board.turn
        self.checkMate = self.board.checkMate
        self.staleMate = self.board.staleMate
        self.isInsuffichentMaterials = self.board.isInsuffichentMaterials

        #Event Handlers:
        @self.dgtBoard.dgtConnection.on("connected")
        def onConnection(port):
            print(f"Board connected at {port}")

        @self.dgtBoard.dgtConnection.on("disconnected")
        def onDisconnection():
            print("Board disconnected")

        @self.dgtBoard.dgtConnection.on("board")
        def onBoardChange(board):
            print(str(board))
            self.updatingDGTBoard = str(board)
            self.updatingUCI = self.board.getUCI(self.updatingDGTBoard)
            self.liveBoard = self.strBoardToMatrix(str(board))
            move = {
                "dgtBoardFEN": self.strBoardToFenBoard(str(board)),
                "isLegal": self.updatingUCI in self.board.legalMoves
            }
            print(json.dumps(move)) # send 
            if self.updatingUCI in self.board.legalMoves:
                cmd = input("Confirm move y or n?\n")
                if cmd == "y":
                    print("Confirmed")
                    onConfirmMove()
                else:
                    print("Denied")

        #@userFeedback.on("confirmMove")
        def onConfirmMove(confirmMove):
            if self.turn == self.color:
                self.dgtBoard = self.updatingDGTBoard
                uciMove = chess.Move.from_uci(self.updatingUCI)
                self.board.push(uciMove)
                self.game.add_variation(chess.Move.from_uci(uciMove))
                self.turn = self.board.turn
                legalMoves: "list[chess.Move]" = list(self.board.legal_moves)
                self.legalMoves = []
                for i in legalMoves:
                    x = str(i)
                    x.replace("Move.from_uci('", "")
                    x.replace("')", "")
                    self.legalMoves.append(x)
                pgn = {"PGN": str(self.game.game())}
                # socket.emit("pgn")
                self.checkMate = self.board.checkMate
                self.staleMate = self.board.staleMate
                self.isInsuffichentMaterials = self.board.isInsuffichentMaterials
                if self.checkMate:
                    print("Checkmate! You win!")
                elif self.staleMate:
                    print("Stalemate! It's a draw!")
                elif self.isInsuffichentMaterials:
                    print("Insuffichent materials! It's a draw!")
                else:
                    print("It is the robots turn now!")
            else:
                print("It is not your turn!")
            



    #Methods:
    def strBoardToFenBoard(self, strBoard: str) -> str:
        strBoard = strBoard.split("\n")
        for i in range(len(strBoard)):
            strBoard[i] = strBoard[i].split(" ")
        fen = ""
        emptySpacesCounter = 0
        for y in range(len(strBoard)):
            for x in range(len(strBoard[y])):
                if strBoard[y][x] != ".":
                    if emptySpacesCounter > 0:
                        fen += str(emptySpacesCounter)
                        emptySpacesCounter = 0
                    fen += strBoard[y][x]
                else:
                    emptySpacesCounter += 1
                    if x == 7:
                        fen += str(emptySpacesCounter)
                        emptySpacesCounter = 0
            if y < 7:
                fen += "/"
        return fen
            
    def strBoardToMatrix(self, board: str) -> "list[list[str]]":
        if len(board) == 127:
            try:
                board = board.split("\n")
                for i in range(len(board)):
                    board[i] = board[i].split(" ")
                return board
            except:
                return None
        else:
            return None
    
    def playRobotMove(self):
        previousBoard = str(self.board.board)
        result = self.engine.play(self.board.board, chess.engine.Limit(time=0.1))
        print(result.move)
        self.board.push(result.move)
        self.game.add_variation(chess.Move.from_uci(result.move))
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
            self.robot.promotion(move["fromPos"].TCP, self.capturePos.TCP)
            targetSquare = self.liveBoard[int(str(result.move)[4])][self.files[str(result.move)[3]] - 1]
            while targetSquare != move["promotionPiece"]:
                piece = self.pieceNames[move["promotionPiece"]]
                input(f"Please place a {'white' if self.turn else 'black'} {piece} at the {result.move[2:4]} square and press enter...")
        elif move["type"] == "capturePromotion":
            self.robot.capturePromotion(move["fromPos"].TCP, move["toPos"].TCP, self.capturePos.TCP)
            targetSquare = self.liveBoard[int(str(result.move)[4])][self.files[str(result.move)[3]] - 1]
            while targetSquare != move["promotionPiece"]:
                piece = self.pieceNames[move["promotionPiece"]]
                input(f"Please place a {'white' if self.turn else 'black'} {piece} at the {result.move[2:4]} square and press enter...")
        else:
            # Move not recognised
            pass
        board = self.dgtBoard.getCurentBoard()
        board = self.dgtBoard.getCurentBoard()
        print(str(self.game.game()))
        move = {
                "dgtBoardFEN": self.strBoardToFenBoard(str(board)),
                "PGN": str(self.game.game())
        }
        #socket.emit(move)
        print(json.dumps(move)) # send 
        self.checkMate = self.board.checkMate
        self.staleMate = self.board.staleMate
        self.isInsuffichentMaterials = self.board.isInsuffichentMaterials
        if self.checkMate:
            print("Checkmate! You loose!")
        elif self.staleMate:
            print("Stalemate! It's a draw!")
        elif self.isInsuffichentMaterials:
            print("Insuffichent materials! It's a draw!")
        else:
            print("Your turn!")

    def calibrate(self) -> "list[TCP]":
        calibrationFileName = "config.json"
        feature = None
        if os.path.exists(calibrationFileName):
            recalibrationCMD = None
            while recalibrationCMD != "y" and recalibrationCMD != "n":
                if recalibrationCMD != None:
                    print("Input not recognised, please try again...")
                recalibrationCMD = input("Do you wish to recalibrate the board feature? y/n\n")
            if recalibrationCMD == "y":
                with open(calibrationFileName, "w") as calibrationFile:
                    feature = self.robot.recalibrateFeature()
                    calibrationFile.write(json.dumps({"feature": [feature[0].TCP, feature[1].TCP, feature[2].TCP]}))

            else:
                print("Trying to use predeffined board feature...")
                try:
                    with open(calibrationFileName, "r") as calibrationFile:
                        feature = json.loads(calibrationFile.read())["feature"]
                        feature = [TCP(feature[0]), TCP(feature[1]), TCP(feature[2])]
                except:
                    print("There was an error using the predeffined board feature,")
                    print("Please redeffine the feature by following the instructions...")
                    with open(calibrationFileName, "w") as calibrationFile:
                        feature = self.robot.recalibrateFeature()
                        calibrationFile.write(json.dumps({"feature": [feature[0].TCP, feature[1].TCP, feature[2].TCP]}))
        else:
            print("There was no predeffined board feature, please define one by following the instructions...")
            with open(calibrationFileName, "w") as calibrationFile:
                feature = self.robot.recalibrateFeature()
                calibrationFile.write(json.dumps({"feature": [feature[0].TCP, feature[1].TCP, feature[2].TCP]}))
        return feature