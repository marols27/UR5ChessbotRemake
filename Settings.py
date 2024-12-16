import chess
import chess.engine
from ToolCenterPoint import ToolCenterPoint as TCP
from UR5Feature import UR5Feature
from PoseConfigure import PoseConfigure
import json


# Chess Dimensions in meters
KING_HEIGHT: float = 0.098
BOARD_SIZE: float = 0.54
SQUARE_SIZE: float = 0.055


# Robot Parameters
TRAVEL_HEIGHT: float = KING_HEIGHT * 2 + 0.01 # To king heights and a tiny margin tall to avoid collision
CONNECTION_IP: str = '172.31.1.144'  # UR5 Robot IP (modify to actual IP)
ACCELERATION: float = 0.6
SPEED: float = 1.0
GRIPPER_SPEED: int = 150
GRIPPER_FORCE: int = 50


# DGTBoard
PORT: str = "/dev/ttyACM*"  # DGT Board port (modify to actual port)


# Configurations
FILE_NAME: str = "config.json" # File name to save and load the calibration points
try:
    with open(FILE_NAME, 'r') as file:
        config = json.loads(file.read())
    ORIGIN = TCP(config[PoseConfigure.Points.ORIGIN.value])
    XAXIS = TCP(config[PoseConfigure.Points.XAXIS.value])
    XYPLANE = TCP(config[PoseConfigure.Points.XYPLANE.value])
    HOME = TCP(config[PoseConfigure.Points.HOME.value])
    CAPTURE_POSE = TCP(config[PoseConfigure.Points.DROP.value])
except:
    PoseConfigure().firstTimeSettup(connectionIP=CONNECTION_IP, fileName=FILE_NAME)
    with open(FILE_NAME, 'r') as file:
        config = json.loads(file.read())
    ORIGIN = TCP(config[PoseConfigure.Points.ORIGIN.value])
    print(ORIGIN)
    XAXIS = TCP(config[PoseConfigure.Points.XAXIS.value])
    XYPLANE = TCP(config[PoseConfigure.Points.XYPLANE.value])
    HOME = TCP(config[PoseConfigure.Points.HOME.value])
    CAPTURE_POSE = TCP(config[PoseConfigure.Points.DROP.value])

def update_config():
    with open(FILE_NAME, 'r') as file:
        config = json.loads(file.read())
    global ORIGIN, XAXIS, XYPLANE, HOME, CAPTURE_POSE
    ORIGIN = TCP(config[PoseConfigure.Points.ORIGIN.value])
    XAXIS = TCP(config[PoseConfigure.Points.XAXIS.value])
    XYPLANE = TCP(config[PoseConfigure.Points.XYPLANE.value])
    HOME = TCP(config[PoseConfigure.Points.HOME.value])
    CAPTURE_POSE = TCP(config[PoseConfigure.Points.DROP.value])

# Board Params
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  
BOARD_FEATURE = UR5Feature(ORIGIN, XAXIS, XYPLANE)  


# Engine
STOCKFISH_PATH = r"/home/rocotics/Desktop/MrCheckMate/Ur5ChessBot/Rebuild/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/src/stockfish" # Path to stockfish engine file, replace with actual path.
TIMEOUT_TIME = 0.1  # Time limit for the engine
TIMEOUT = chess.engine.Limit(time=TIMEOUT_TIME)  # Time limit for the engine
DIFFICULTY = 1  # Example difficulty, replace with actual


def on_condition():
    # conditions
    pass

def on_start_game():
    # First game condition
    pass

def on_env_configure():
    # Environment configuration
    PoseConfigure.firstTimeSettup(connectionIP=CONNECTION_IP, fileName=FILE_NAME)

#SOCKET.on('condition', on_condition)
#SOCKET.on('start_game', on_start_game)
#SOCKET.on('env_configure', on_env_configure)