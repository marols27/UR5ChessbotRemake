import rtde_control #import RTDEControlInterface as RTDEControl
import rtde_receive #import RTDEReceiveInterface as RTDEReceive
from robotiq_gripper_control import RobotiqGripper
import json
from enum import Enum

class PoseConfigure:
    """
    ## Class for calibrating the robot to a specific settup.

    #### ATTRIBUTES:
    - conectionIP: 
        The IP of the robot.
    - fileName: 
        The name of the file to save the calibration to.
    
    #### METHODES:
    - firstTimeSettupe(): 
        Calibrates the robot for the first time.
    - recalibrate(point: Points): 
        Recalibrates a specific point.
    
    
    """

    class Points(Enum):
        """
        ### Enumerator for the calibration points.

        Values:
        - ORIGIN: Origin point
        - XAXIS: X axis point
        - XYPLANE: XY plane point
        - HOME: Home point
        - DROP: Drop point
        """

        ORIGIN = "origin"
        XAXIS = "xAxis"
        XYPLANE = "xyPlane"
        HOME = "home"
        DROP = "drop"
    
    connectionIP = None
    fileName = None

    def __init__(self, connectionIP: str = '172.31.1.144', fileName: str = "config.json"):
        self.connectionIP = connectionIP
        self.fileName = fileName

    def firstTimeSettup(self, connectionIP: str = '172.31.1.144', fileName: str = 'config.json'):
        """
        ### Calibrates the robot for the first time, initializing 5 points and saves them to a file.
        """
        if self.connectionIP == None:
            self.connectionIP = connectionIP
        if self.fileName == None:
            self.fileName = fileName
        control = rtde_control.RTDEControlInterface(self.connectionIP)
        info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        gripper = RobotiqGripper(control)
        gripper.activate()
        gripper.move(37)
        control.teachMode()
        config = {}
        input("Move the robot to the board origin and press enter...")
        config[self.Points.ORIGIN.value] = info.getActualTCPPose()
        print(info.getActualTCPPose())
        print(config[self.Points.ORIGIN.value])
        input("Move the robot to the x axis and press enter...")
        config[self.Points.XAXIS.value] = info.getActualTCPPose()
        #print(config[self.Points.XAXIS.value])
        input("Move the robot to the xy plane and press enter...")
        config[self.Points.XYPLANE.value] = info.getActualTCPPose()
        #print(config[self.Points.XYPLANE.value])
        input("Move the robot to the home position and press enter...")
        config[self.Points.HOME.value] = info.getActualTCPPose()
        #print(config[self.Points.HOME.value])
        input("Move the robot to the drop position and press enter...")
        config[self.Points.DROP.value] = info.getActualTCPPose()
        #print(config[self.Points.DROP.value])
        with open(self.fileName, 'w') as file:
            json.dump(config, file)
        control.endTeachMode()
    
    def recalibrate(self, point: Points, connectionIP: str = '172.31.1.144', fileName: str = 'config.json'):
        """
        ### Calibrates a single point of the 5 existing calibrated points, and updates the existing file.
        """
        if self.connectionIP == None:
            self.connectionIP = connectionIP
        if self.fileName == None:
            self.fileName = fileName
        control = rtde_control.RTDEControlInterface(self.connectionIP)
        info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        gripper = RobotiqGripper(control)
        gripper.activate()
        gripper.move(37)
        try:
            with open(self.fileName, 'r') as file:
                config = json.load(file)
            file.close()
            control.teachMode()
            input(f"Move the robot to the {point} point and press enter to get the pose...")
            config[point] = info.getActualTCPPose()
            control.endTeachMode()
            with open(self.fileName, 'w') as file:
                json.dump(config, file)
        except:
            print("No previous calibration found, or there was an error reading the file!")
            return
    
    def freeMove(self):
        control = rtde_control.RTDEControlInterface(self.connectionIP)
        control.teachMode()
        input("Move the robot to the point and press enter to get the pose...")
        control.endTeachMode()
    
    def start_teach_mode(self):
        control = rtde_control.RTDEControlInterface(self.connectionIP)
        control.teachMode()
    
    def end_teach_mode(self):   
        control = rtde_control.RTDEControlInterface(self.connectionIP)
        control.endTeachMode()
    
    def calibrate_point(self, point):
        info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        config = None
        with open(self.fileName, 'r') as file:
                config = json.load(file)
        file.close()
        if point == "origin":
            print("Current Origin:",config[self.Points.ORIGIN.value])                       
            config[self.Points.ORIGIN.value] = info.getActualTCPPose()
            print("New Origin:",config[self.Points.ORIGIN.value])
        elif point == "xAxis":
            config[self.Points.XAXIS.value] = info.getActualTCPPose()
            print("New X Axis:",config[self.Points.XAXIS.value])
        elif point == "xyPlane":
            config[self.Points.XYPLANE.value] = info.getActualTCPPose()
            print("New XY Plane:",config[self.Points.XYPLANE.value])
        elif point == "home":
            print("Current Home:",config[self.Points.HOME.value])
            config[self.Points.HOME.value] = info.getActualTCPPose()
            print("New Home:",config[self.Points.HOME.value])
        elif point == "drop":
            config[self.Points.DROP.value] = info.getActualTCPPose()
            print("New Drop:",config[self.Points.DROP.value])
        else:
            print("Invalid point!")

        with open(self.fileName, 'w') as file:
                json.dump(config, file)

