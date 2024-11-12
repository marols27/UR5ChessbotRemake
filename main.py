import chess.engine
import chess.pgn
from ChessGameEnvironment import ChessGameEnvironment
from flask_socketio import SocketIO, send, emit
from UR5Robot import UR5Robot
from DGTBoard import DGTBoard
from Board import Board
import chess
import Settings
from Game import Game
import threading

# If you wish to change any of the settings, it is recommended to change them in the Settings.py file.
chessGame = None
robot = UR5Robot(
    travelHeight=Settings.TRAVEL_HEIGHT, 
    homePose=Settings.HOME, 
    connectionIP=Settings.CONNECTION_IP, 
    acceleration=Settings.ACCELERATION, 
    speed=Settings.SPEED, 
    gripperSpeed=Settings.GRIPPER_SPEED, 
    gripperForce=Settings.GRIPPER_FORCE
)
robot.goto([0.7091606786033604, -0.0541754831329132, 0.29518362120390085, 2.1329911700278688, 2.2857584007660523, 0.0035996202591358053])
robot.home()
socket = Settings.SOCKET
dgtBoard = DGTBoard(port=Settings.PORT)
board = Board(
    startFen=Settings.START_FEN, 
    feature=Settings.BOARD_FEATURE, 
    boardSize=Settings.BOARD_SIZE, 
    squareSize=Settings.SQUARE_SIZE
)
engine = chess.engine.SimpleEngine.popen_uci(Settings.STOCKFISH_PATH)
gameInfo = chess.pgn.Game()
capturePos = Settings.CAPTURE_POSE
timeout = Settings.TIMEOUT

conditions = None
dgtThread = threading.Thread(None, dgtBoard.run)
dgtThread.daemon = True
dgtThread.start()

@dgtBoard.dgtConnection.on('board')
def on_board(board):
    print(board)
    #emit('board', board)

def start_game():
    #try:
        global chessGame
        if chessGame == None:
            chessGame = Game(
                socket=socket, 
                robot=robot, 
                dgtBoard=dgtBoard, 
                board=board, 
                engine=engine, 
                gameInfo=gameInfo, 
                capturePos=capturePos, 
                timeout=timeout
            )
            robot.home()
            global conditions
            chessGame.on_conditions(conditions)
            chessGame.runGameLoop()
    #except Exception as e:
    #    print(f"Error during game initialization: {e}")

socket.start()
# Event handlers (commented out unless needed for your specific logic):
"""
@robot.control.on("connect")
def on_robot_connection():
    socket.emit("robot_connected")

@robot.control.on("disconnect")
def on_robot_disconnection():
    socket.emit("robot_disconnected")

@robot.info.on("connect")
def on_robot_info_connection():
    socket.emit("robot_info_connected")

@robot.info.on("disconnect")
def on_robot_info_disconnection():
    socket.emit("robot_info_disconnected")

@robot.gripper.on("connect")
def on_robot_gripper_connection():
    socket.emit("robot_gripper_connected")

@robot.gripper.on("disconnect")
def on_robot_gripper_disconnection():
    socket.emit("robot_gripper_disconnected")

@dgtBoard.dgtConnection.on("connect")
def on_dgt_connection():
    socket.emit("dgt_connected")

@dgtBoard.dgtConnection.on("disconnect")
def on_dgt_disconnection():
    socket.emit("dgt_disconnected")
"""
