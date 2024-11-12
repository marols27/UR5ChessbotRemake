import Settings
from UR5Robot import UR5Robot
from Board import Board

robot = UR5Robot(travelHeight=Settings.TRAVEL_HEIGHT, homePose=Settings.HOME, connectionIP=Settings.CONNECTION_IP, acceleration=Settings.ACCELERATION, speed=Settings.SPEED, gripperSpeed=Settings.GRIPPER_SPEED, gripperForce=Settings.GRIPPER_FORCE)
board = Board(startFen=Settings.START_FEN, feature=Settings.BOARD_FEATURE, boardSize=Settings.BOARD_SIZE, squareSize=Settings.SQUARE_SIZE)
robot.movePiece(board.getSquareTCP("e2").TCP, board.getSquareTCP("e4").TCP)
robot.movePiece(board.getSquareTCP("e4").TCP, board.getSquareTCP("e2").TCP)