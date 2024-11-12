from ToolCenterPoint import ToolCenterPoint as TCP
import numpy as NP
import copy

class UR5Feature(): # NB the constructor should be reconstructed to calculate rotation angles during 3 pts config instead of just using the origon orientation!
    
    # Quick info about a UR5feature:
    # A feature for the UR5 robot (defined by it's creators) is a userdefined coordinate system relative to
    # the UR5 base coordinates.
    # It is defined by 3 points, the origin, the X-Axis point and the Y-Axis point.
    # The origin, wil be the point from which every point will work from,
    # The X-Axis point will define in which direction the X-Axis in the coordinate system should increase.
    # And the Y-Axis point will define in what direction the Y-Axis increases in the coordinate system.
    # The Z-Axis is automaticaly sett as you already sett the X, and y -Axis. 
    # The Z-Axis should then be a line or vector pointing 90 degrees of both the X and Y Axis, 
    # in the direction determined by the "Right Hand Rule".

    # CLASS DOCUMENTATION:
    # This class represents a UR5 feature as coordinate system, using an origo point as it's center
    # and 3 vectors determining the orientation of the x, y and z axis.
    
    # Fields:
    #  - Origin: The xyz coordinate the feature will be centered to.
    #  - XAxis: The xyz vector that defines the X axis orientation from the origo.
    #  - YAxis: The xyz vector that defines the Y axis orientation from the origo.
    #  - ZAxis: The xyz vector that defines the Z axis orientation from the origo.

    # Constructor:
    #  - __init__(self, origin, xAxis, xyPlane): Uses the first point to set the origin and robot orientation, and the remaining to find the XYZ axis orientation.
    
    # Functions:
    # - getNewTCPByXYZMove(self, currentTCP, x, y, z): 
    #       Returns the new TCP, moved by x, y, and z in their x, y and z directions relative to the current TCP
    #
    # - getNewTCPByFeatureXYZ(self, x, y, z): 
    #       Returns the new TCP at the coordinates x, y, and z relative to the local origin



    # Fields
    Origin: "TCP" = None
    XAxis: "TCP" = None
    XYPlane: "TCP" = None
    XAxis: "list[float]" = None
    YAxis: "list[float]" = None
    ZAxis: "list[float]" = None


    # Constructrs:
    def __init__(self, origin: TCP, xAxis: TCP, xyPlane: TCP):
        self.Origin = origin
        self.XAxis = xAxis
        self.XYPlane = xyPlane
        origin = origin.position()
        xAxis = xAxis.position()
        xyPlane = xyPlane.position()

        xVector = [xAxis[0] - origin[0], xAxis[1] - origin[1], xAxis[2] - origin[2]]
        self.XAxis = xVector / NP.linalg.norm(xVector)

        pVector = [xyPlane[0] - origin[0], xyPlane[1] - origin[1], xyPlane[2] - origin[2]]
        zVector = NP.cross(xVector, pVector)
        self.ZAxis = zVector / NP.linalg.norm(zVector)

        yVector = NP.cross(self.ZAxis, self.XAxis)
        self.YAxis = yVector / NP.linalg.norm(yVector)
    

    # Methodes:
    def getNewTCPByXYZMove(self, currentTCP: TCP, x: float, y: float, z: float) -> TCP:
        newTCP = copy.deepcopy(currentTCP)
        newTCP.TCP[3:] = self.Origin[3:]
        newTCP.TCP[0] += (x * self.XAxis[0] + y * self.YAxis[0] + z * self.ZAxis[0])
        newTCP.TCP[1] += (x * self.XAxis[1] + y * self.YAxis[1] + z * self.ZAxis[1])
        newTCP.TCP[2] += (x * self.XAxis[2] + y * self.YAxis[2] + z * self.ZAxis[2])
        return newTCP
    
    def getFeatureRelativeTCP(self, x: float, y: float, z: float) -> TCP:
        newTCP = copy.deepcopy(self.Origin)
        newTCP.TCP[0] += (x * self.XAxis[0] + y * self.YAxis[0] + z * self.ZAxis[0])
        newTCP.TCP[1] += (x * self.XAxis[1] + y * self.YAxis[1] + z * self.ZAxis[1])
        newTCP.TCP[2] += (x * self.XAxis[2] + y * self.YAxis[2] + z * self.ZAxis[2])
        return newTCP
        



    """def angleBetweenVectors(self, v1: "list[float]", v2: "list[float]") -> float:
        if len(v1) != len(v2):
            return None
        else:
            v1Length = NP.linalg.norm()
            v2Length = NP.linalg.norm()
            scalar = NP.dot(v1, v2)
            angleBetweenVectors = math.acos(scalar / (v1Length * v2Length))
        return angleBetweenVectors"""