import chess.pgn
from UR5Feature import UR5Feature
from ToolCenterPoint import ToolCenterPoint as TCP
import chess

class Board():
    # # CLASS DOCCUMENTATION:
    # This class contains information of the physical DGT boards dimentions, the game state (pieces position), the

    # # FIELDS:
    # - boardSize: The board length and with measured in meter.
    # - squareSize: The boards squares with and length measured in meter.
    # - kingHeight: The height of the tallest piece on the board measured in meter.
    # - loop: (Not quite sure) Some kind of asyncronus task processing variable.
    # - dgtBoard: The asyncronus connection task to the physical board.
    # - feature: A feature object for keeping track of the boards pose relative to the robot.
    #            "this is used to in a more easy way calculate the pieces' positions on the board during playtime."
    # - board: A viritual clone of the board, keeping track of the physical state of the board. (Might not be nessecary).
    # - history: A list keeping track of every leegal move don since the start of the program. (need to be resett whith each new game)
    # - previousState: Keeps track of the previous legal move done on the board.
    
    # # CONSTRUCTOR:
    # __init__(startFen, featureOriginTCP, featureXAxisTCP, featureXYPlaneTCP, boardSize, squareSize, tallestPieceHeight): 
    #       Creates a new Board object, and populates the history, and previousState with the startFen, 
    #       and initializes the feature using the 3 TCP objects passed in the constructor.
    
    # # METHODS:
    # - getSquareTCP(pos): 
    #       Expects a string of 2 caracters (file letters and rank numbers) in the format "[a-h][1-8]" 
    #       and returns the position coordinates for the square for the robot to move to.
    #
    #  - getUCI(board): 
    #       Returns a Universal Chess Interface (UCI) move string, by comparing a new board layout with the current.
    # 
    # - getMoveTCPByUCI(uciMove) -> dict: 
    #       Returns a dictionary containing the move type (str) and an x number of different 
    #       ToolCenterPoints (TCP) for the robot. 
    #       The dictionary is structured in the following way:
    #       {
    #           "type": str,                # A move description
    #           "fromPos": TCP,             # The move from pos
    #           "toPos": TCP,               # The move to pos
    #           "enPassantTarget": TCP,     # The captured pawn during enPassant
    #           "castleFrom": TCP,          # The rooks from pos when castling
    #           "castleTo": TCP,            # The rooks to pos when castling
    #           "promotionPiece": str       # The piece to promote to when a pawn is promoted
    #       }
    #       And the different move types are:
    #        - "capturePromotion",
    #        - "promotion",
    #        - "enPassant", 
    #        - "castle", 
    #        - "capture", 
    #        - "move"
    #              
    #  - push(UCI) -> None: Updates the board with the new move.
    #       Expect a Universal Chess Interface (UCI) move as a string, and updates the virtual clone of the game.
    #       Does not return anything.
    #
    # - getPGN() -> "list[str]":
    #       Portable Game Notation (PGN) is a history of chess moves in a game.
    #       Returns the current PGN as a list of uci moves.
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

    # Fields:
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
    boardSize: float = 0.54
    squareSize: float = 0.055


    # Constructor:
    def __init__(
            self, 
            startFen: str,
            feature: UR5Feature,
            boardSize: float = 0.54,
            squareSize: float = 0.055
        ):
        self.boardSize = boardSize      # m
        self.squareSize = squareSize    # m
        self.feature = feature
        self.board = chess.Board(fen=startFen)
        self.turn = self.board.turn
        self.checkMate = self.board.is_checkmate()
        self.staleMate = self.board.is_stalemate()
        self.isInsuffichentMaterials = self.board.is_insufficient_material()
        
        legalMoves: "list[chess.Move]" = list(self.board.legal_moves)
        self.legalMoves: "list[str]" = []
        for i in legalMoves:
            x = str(i)
            x.replace("Move.from_uci('", "")
            x.replace("')", "")
            self.legalMoves.append(x)

    # Methods
    def getSquareTCP(self, boardPos: str) -> TCP:
        file = self.files[boardPos[0].lower()]
        rank = int(boardPos[1])
        return self.feature.getFeatureRelativeTCP(self.squareSize * (file - 1), self.squareSize * (rank - 1), 0)
    
    # Not finished, to do list:
    # - Implement the casteling case.
    def getUCI(self, toBoard: str) -> str:
        def fileNumberToLetter(number):
            return list(self.files.keys())[list(self.files.values()).index(number)]
        fromBoard = str(self.board).split("\n")
        for i in range(len(fromBoard)):
            fromBoard[i] = fromBoard[i].split(" ")
        
        toBoard = toBoard.split("\n")
        for i in range(len(toBoard)):
            toBoard[i] = toBoard[i].split(" ")
        
        # List of dictionaries in the form {file, rank, before, after}
        changedSquares: "list[dict]" = []
        for x in range(1, 9):
            for y in range(1, 9):
                if fromBoard[8-y][x-1] != toBoard[8-y][x-1]:
                    changedSquares.append({"file":x, "fileLetter":fileNumberToLetter(x),"rank":y, "before":fromBoard[8-y][x-1], "after":toBoard[8-y][x-1]})

        uci = ""
        # Picked upp piece case
        if len(changedSquares) == 1:
            return None

        # Normal move case (with promotion handling)
        elif len(changedSquares) == 2:
            # Checking spechial non complete move cases
            movingPawn = changedSquares[0]["before"].lower() == "p" or changedSquares[1]["before"].lower() == "p"
            changingFiles = changedSquares[0]["file"] != changedSquares[1]["file"]
            enPassentMove = changedSquares[0]["before"] == changedSquares[1]["after"] and changedSquares[0]["after"] == changedSquares[1]["before"]
            kingIsCasteling = (changedSquares[0]["before"].lower() == "k" or changedSquares[1]["before"].lower() == "k") and abs(changedSquares[0]["file"] - changedSquares[1]["file"]) == 2

            notCompletedMoveCases = [
                changedSquares[0]["after"] == changedSquares[1]["after"], # "During a capture, both squares has to be emptied during piece moving"
                movingPawn and changingFiles and enPassentMove,
                kingIsCasteling
            ]
            if True in notCompletedMoveCases:
                return None

            if changedSquares[0]["after"] == ".":
                uci += changedSquares[0]["fileLetter"]
                uci += str(changedSquares[0]["rank"])
                uci += changedSquares[1]["fileLetter"]
                uci += str(changedSquares[1]["rank"])
                movedPieceIsPawn = changedSquares[0]["before"].lower() == "p"
                movedPieceWasPromoted = changedSquares[1]["after"].lower() != "p"
                if movedPieceIsPawn and movedPieceWasPromoted:
                    uci += changedSquares[1]["after"].lower()
            else:
                uci += changedSquares[1]["fileLetter"]
                uci += str(changedSquares[1]["rank"])
                uci += changedSquares[0]["fileLetter"]
                uci += str(changedSquares[0]["rank"])
                movedPieceIsPawn = changedSquares[1]["before"].lower() == "p"
                movedPieceWasPromoted = changedSquares[0]["after"].lower() != "p"
                if movedPieceIsPawn and movedPieceWasPromoted:
                    uci += changedSquares[0]["after"].lower()
            return uci
        
        # En passent move case
        elif len(changedSquares) == 3:
            fromRank = []
            moveToSquare = None
            assaultingSquare = None
            for i in changedSquares:
                if i["before"].lower() == "p":
                    fromRank.append(i)
                else:
                    moveToSquare = i
            
            if len(fromRank) != 2:
                return None
            
            fromRankACheck = fromRank[0]["before"].lower() == "p" and fromRank[0]["after"] == "."
            fromRankBCheck = fromRank[1]["before"].lower() == "p" and fromRank[1]["after"] == "."
            moveToSquareCheck = moveToSquare["before"] == "." and moveToSquare["after"].lower() == "p"
            enPassentMove = fromRankACheck and fromRankBCheck and moveToSquareCheck
            if not enPassentMove:
                return None # "ERROR: 3 Changes on the board was made, but no en passent move detected!"
            else:
                assaultingSquare = fromRank[0] if fromRank[0]["file"] != moveToSquare["file"] else fromRank[1]
                uci += assaultingSquare["fileLetter"]
                uci += str(assaultingSquare["rank"])
                uci += moveToSquare["fileLetter"]
                uci += str(moveToSquare["rank"])
                return uci
        
        # Castle move case
        elif len(changedSquares) == 4:
            rooksMove = [None, None]
            kingsMove = [None, None]
            for i in changedSquares:
                if i["before"].lower() == "k":
                    kingsMove[0] = i
                elif i["before"].lower() == "r":
                    rooksMove[0] = i
                elif i["after"].lower() == "k":
                    kingsMove[1] = i
                elif i["after"].lower() == "r":
                    rooksMove[1] = i
                else:
                    return None
            kingHasMoved2Files = abs(kingsMove[0]["file"] - kingsMove[1]["file"]) == 2
            kingHasMoved0Ranks = kingsMove[0]["rank"] == kingsMove[1]["rank"]
            if kingHasMoved2Files and kingHasMoved0Ranks:
                return kingsMove[0]["fileLetter"] + str(kingsMove[0]["rank"]) + kingsMove[1]["fileLetter"] + str(kingsMove[1]["rank"])
            else:
                return None
        else:
            return None
    
    def getMoveTCPByUCI(self, uciMove: str, previousBoard: str) -> "dict[str, TCP, TCP, TCP]":
        fromSquare = [uciMove[:2][0], int(uciMove[:2][1])]
        toSquare = [uciMove[2:4][0], int(uciMove[2:4][1])]
        fromBoard = self.strBoardToMatrix(previousBoard)
        toBoard = self.strBoardToMatrix(str(self.board))

        isMoveToSquareEmpty = fromBoard[8 - toSquare[1]][self.files[toSquare[0]] - 1] == "."
        isMoveFromSquarePawn = toBoard[8 - toSquare[1]][self.files[toSquare[0]] - 1].lower() == "p"
        isFileChangingMove = fromSquare[0] != toSquare[0]
        isMoveFromSquareKing = fromBoard[8 - fromSquare[1]][self.files[fromSquare[0]] - 1].lower() == "k"
        isMoving2Files = abs(self.files[fromSquare[0]] - self.files[toSquare[0]]) == 2
        isToSpotOccupied = fromBoard[8 - toSquare[1]][self.files[toSquare[0]] - 1] != "."

        if len(uciMove) == 5:
            move = {
                "type": "promotion" if not isToSpotOccupied else "capturePromotion",
                "fromPos": self.getSquareTCP(fromSquare),
                "toPos": self.getSquareTCP(toSquare),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": uciMove[4]
            }
        elif isMoveFromSquarePawn and isMoveToSquareEmpty and isFileChangingMove:
            move = {
                "type": "enPassant",
                "fromPos": self.getSquareTCP(fromSquare),
                "toPos": self.getSquareTCP(toSquare),
                "enPassantTarget": self.getSquareTCP(toSquare[0] + int(fromSquare[1])),
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None
            }
        # CASTLING MOVES SOFT CODED VERSION FOR NORMAL CHESS ONLY:
        elif isMoveFromSquareKing and isMoving2Files:
            rookFromSquareOnCastelingSide = "a" + str(fromSquare[1]) if (toSquare[0] == "c") else "h" + str(fromSquare[1])
            rookToSquareOnCastelingSide = "d" + str(fromSquare[1]) if (toSquare[0] == "c") else "f" + str(fromSquare[1])
            move = {
                "type": "castle",
                "fromPos": self.getSquareTCP(fromSquare),
                "toPos": self.getSquareTCP(toSquare),
                "enPassantTarget": None,
                "castleFrom": self.getSquareTCP(rookFromSquareOnCastelingSide),
                "castleTo": self.getSquareTCP(rookToSquareOnCastelingSide),
                "promotionPiece": None
            }
        # CASTLING MOVES HARD CODED VERSION FOR NORMAL CHESS ONLY:
            """
            if isMoveFromSquareKing:
                if uciMove == "e1c1":
                    move = {
                        "type": "castle",
                        "fromPos": self.getSquareTCP(fromSquare),
                        "toPos": self.getSquareTCP(toSquare),
                        "enPassantTarget": None,
                        "castleFrom": self.getSquareTCP("a1"),
                        "castleTo": self.getSquareTCP("d1"),
                        "promotionPiece": None
                    }
                elif uciMove == "e1g1":
                    move = {
                        "type": "castle",
                        "fromPos": self.getSquareTCP(fromSquare),
                        "toPos": self.getSquareTCP(toSquare),
                        "enPassantTarget": None,
                        "castleFrom": self.getSquareTCP("h1"),
                        "castleTo": self.getSquareTCP("f1"),
                        "promotionPiece": None
                    }
                elif uciMove == "e8c8":
                    move = {
                        "type": "castle",
                        "fromPos": self.getSquareTCP(fromSquare),
                        "toPos": self.getSquareTCP(toSquare),
                        "enPassantTarget": None,
                        "castleFrom": self.getSquareTCP("a8"),
                        "castleTo": self.getSquareTCP("d8"),
                        "promotionPiece": None
                    }
                elif uciMove == "e8g8":
                    move = {
                        "type": "castle",
                        "fromPos": self.getSquareTCP(fromSquare),
                        "toPos": self.getSquareTCP(toSquare),
                        "enPassantTarget": None,
                        "castleFrom": self.getSquareTCP("h8"),
                        "castleTo": self.getSquareTCP("f8"),
                        "promotionPiece": None
                    }
                else:
                    isMoveToSquareEmpty = self.fromBoard[int(toSquare[1])][self.files[toSquare[0]]] == "."
                    if isMoveToSquareEmpty:
                        move = {
                            "type": "move",
                            "fromPos": self.getSquareTCP(fromSquare),
                            "toPos": self.getSquareTCP(toSquare),
                            "enPassantTarget": None,
                            "castleFrom": None,
                            "castleTo": None,
                            "promotionPiece": None
                        }
                    else:
                        move = {
                            "type": "capture",
                            "fromPos": self.getSquareTCP(fromSquare),
                            "toPos": self.getSquareTCP(toSquare),
                            "enPassantTarget": None,
                            "castleFrom": None,
                            "castleTo": None,
                            "promotionPiece": None
                        }
            """
        elif isToSpotOccupied:
            move = {
                "type": "capture",
                "fromPos": self.getSquareTCP(fromSquare),
                "toPos": self.getSquareTCP(toSquare),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None
            }
        else:
            move = {
                "type": "move",
                "fromPos": self.getSquareTCP(fromSquare),
                "toPos": self.getSquareTCP(toSquare),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None
            }
        return move

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
    
    def push(self, uci):
        if type(uci) != str:
            uci = str(uci)
            uci.replace("Move.from_uci('", "")
            uci.replace("')", "")
        self.board.push_uci(uci)
        self.turn = self.board.turn
        self.checkMate = self.board.is_checkmate()
        self.staleMate = self.board.is_stalemate()
        self.isInsuffichentMaterials = self.board.is_insufficient_material()
        legalMoves: "list[chess.Move]" = list(self.board.legal_moves)
        self.legalMoves: "list[str]" = []
        for i in legalMoves:
            x = str(i)
            x.replace("Move.from_uci('", "")
            x.replace("')", "")
            self.legalMoves.append(x)

    def getPGN(self):
        return self.board.move_stack