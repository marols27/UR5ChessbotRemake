import rtde_control #import RTDEControlInterface as RTDEControl
import rtde_receive #import RTDEReceiveInterface as RTDEReceive
from robotiq_gripper_control import RobotiqGripper
import copy
from ToolCenterPoint import ToolCenterPoint as TCP


#import Getuci
#import SafeVariableClass

class UR5Robot:
    """
    ## UR5Robot class for some simpler work with a UR5Robot playing chess.
    This class is just ment to store the settings of a robot, as well as the different interfaces in a single object.
    By doing this we get to create robotic moves by deffining the basic movements Goto, Grab, and Dropp,
    and then combinding theese basic movements to create movements of our chess needs.

    #### Fields:
        - travelHeight: The height the robot needs to move to avoid piece collition while moving pieces.
        - homePose:     A predeffined position for the robot to go to and stop in while not doing anything.
        - connectionIP: The UR5Robots IP adress, for conection of the different interfaces.
        - acceleration: The UR5Robots movement acceleration.
        - speed:        The UR5Robots movement speed.
        - gripperSpeed: The UR5Robots gripper speed.
        - gripperForce: The UR5Robots gripper force.

        - control:  Interface for driving the robot.
        - info:     Interface for getting current information about the robot.
        - gripper:  Interface for driving the robots gripper.
    
    #### Constructor:
        - __init__(
            self,
            travelHeight: float,
            conectionIP: str,
            gripperForce: float,
            gripperSpeed: float,
            speed: float,
            acceleration: float
        )
    
    #### Methodes:
        - `getPos(self):` Lets you move the robot arm to a desiered location, and returns the pose of that location when confirmed.
        - freeDrive(self): Lets you move the robot freely until you confirm the position. (To move the robot away).
    ##### Basic movement:
        - goto(self, pos: "list[float]"): Moves the robot to the specified position.
        - grab(self): Makes the robot gripper close.
        - drop(self): Makes the robot gripper open.
    ##### Combined movement:
        - home(self): Moves the robot to the predeffined home pose.
        - movePiece(self, fromPos: "list[float]", toPos: "list[float]", home = True): Moves a chess piece form a specified location to another specified location, and returns the robot to the home stance if home = True.
        - capturePiece(self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"): Captures a piece to the capture pos, and move the piece from and to the specified positions.
        - enPassent(self, fromPos: "list[float]", toPos: "list[float]", targetPos: "list[float]", capturePos: "list[float]"): Performes an en passent move, by from and to poses, a target pose and a capture pose.'
        - castle(self, fromPosKing: "list[float]", toPosKing: "list[float]", fromPosRook: "list[float]", toPosRook: "list[float]"): Performs a casteling move by two sets of from and to poses.
        - promotion(self, fromPos: "list[float]", capturePos: "list[float]"): Captures a pawn for promotion, and requests the user to place down the requiered piece.
        - capturePromotion(self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"): Captures a pawn and an opponet piece and requests the user to place down the requiered piece.
    """

    # Fields:
    travelHeight = None
    homePose = None
    connectionIP = None
    acceleration = None
    speed = None
    gripperSpeed = None
    gripperForce = None

    # Interfaces:
    control = None
    info = None
    gripper = None


    # Constructor:
    def __init__(self, travelHeight: float, homePose: TCP, connectionIP: str, acceleration: float, speed: float, gripperSpeed: float, gripperForce: float):
        self.travelHeight = travelHeight
        self.homePose = homePose
        self.connectionIP = connectionIP
        self.acceleration = acceleration
        self.speed = speed
        self.gripperSpeed = gripperSpeed
        self.gripperForce = gripperForce

        # Connection and setup:
        self.control = rtde_control.RTDEControlInterface(connectionIP)
        self.info = rtde_receive.RTDEReceiveInterface(connectionIP)
        self.gripper = RobotiqGripper(self.control)
        self.gripper.activate()
        self.gripper.set_force(gripperForce)  # from 0 to 100 %
        self.gripper.set_speed(gripperSpeed)  # from 0 to 100 %
        self.drop()
        self.control.disconnect()


    # Methodes:
    def getPos(self):
        self.control.teachMode()
        input("Move the robot to the point and press enter to get the pose...")
        self.control.endTeachMode()
        pose = self.info.getActualTCPPose()
        return pose

    def freeDrive(self):
        self.control.teachMode()
        input("Move the robot away to a desiered location and press enter to continiue...")
        self.control.endTeachMode()
        
    def goto(self, pos: "list[float]"):
        try:
            self.control.moveL(pos, self.speed, self.acceleration)
        except:
            if self.control.isConnected():
                self.control.disconnect()
            self.control.reconnect()
            if self.info.isConnected():
                self.info.disconnect()
            self.info.reconnect()
            self.control.moveL(pos, self.speed, self.acceleration)


    def grab(self):
        try:
            self.gripper.move(6)
        except:
            if self.control.isConnected():
                self.control.disconnect()
            self.control.reconnect()
            if self.info.isConnected():
                self.info.disconnect()
            self.info.reconnect()
            self.gripper.activate()
            self.gripper.set_force(self.gripperForce)  # from 0 to 100 %
            self.gripper.set_speed(self.gripperSpeed)  # from 0 to 100 %
            self.gripper.move(37)
            self.gripper.move(6)


    def drop(self):
        try:
            self.gripper.move(37)
        except:
            if self.control.isConnected():
                self.control.disconnect()
            self.control.reconnect()
            if self.info.isConnected():
                self.info.disconnect()
            self.info.reconnect()
            self.gripper.activate()
            self.gripper.set_force(self.gripperForce)  # from 0 to 100 %
            self.gripper.set_speed(self.gripperSpeed)  # from 0 to 100 %
            self.gripper.move(37)

    def home(self):
        self.goto(self.homePose.TCP)

    def movePiece(self, fromPos: "list[float]", toPos: "list[float]", home = True):
        aboveFromPos = copy.deepcopy(fromPos)
        aboveFromPos[2] += self.travelHeight
        aboveToPos = copy.deepcopy(toPos)
        aboveToPos[2] += self.travelHeight
        self.goto(aboveFromPos)
        self.goto(fromPos)
        self.grab()
        self.goto(aboveFromPos)
        self.goto(aboveToPos)
        self.goto(toPos)
        self.drop()
        self.goto(aboveToPos)
        if home:
            self.home()

    def capturePiece(self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"):
        aboveToPos = copy.deepcopy(toPos)
        aboveToPos[2] += self.travelHeight
        self.goto(aboveToPos)
        self.goto(toPos)
        self.grab()
        self.goto(aboveToPos)
        self.goto(capturePos)
        self.drop()
        self.movePiece(fromPos, toPos)
    
    def enPassent(self, fromPos: "list[float]", toPos: "list[float]", targetPos: "list[float]", capturePos: "list[float]"):
        self.movePiece(fromPos, toPos, False)
        self.movePiece(targetPos, capturePos)

    def castle(self, fromPosKing: "list[float]", toPosKing: "list[float]", fromPosRook: "list[float]", toPosRook: "list[float]"):
        self.movePiece(fromPosKing, toPosKing, False)
        self.movePiece(fromPosRook, toPosRook)
    
    def promotion(self, fromPos: "list[float]", capturePos: "list[float]"):
        self.movePiece(fromPos, capturePos)
        # Request piece promotion.
    
    def capturePromotion(self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"):
        self.movePiece(fromPos, capturePos, False)
        self.movePiece(toPos, capturePos)
        # Request piece promotion.

    if __name__ == '__main__':
        pass