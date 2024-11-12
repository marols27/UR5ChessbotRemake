from Board import Board
import chess
import chess.engine
import chess.pgn
from DGTBoard import DGTBoard
from flask_socketio import SocketIO
from ToolCenterPoint import ToolCenterPoint as TCP
from UR5Robot import UR5Robot

class ChessGameEnvironment:
    socket = None
    robot = None
    dgtBoard = None
    board = None
    engine = None
    gameInfo = None
    capturePos = None

    def __init__(self, socket: SocketIO, robot: UR5Robot, dgtBoard: DGTBoard, board: Board, engine: chess.engine.SimpleEngine, gameInfo: chess.pgn.Game, capturePos: TCP) -> None:
        self.socket = socket
        self.robot = robot
        self.dgtBoard = dgtBoard
        self.board = board
        self.engine = engine
        self.gameInfo = gameInfo
        self.capturePos = capturePos

        print(self.board.board.fen().split(" ")[0])
        print(self.dgtBoard.getCurentBoard())