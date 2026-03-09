from .ToolCenterPoint import ToolCenterPoint as TCP
import numpy as NP
import copy


class UR5Feature:
    """
    A user-defined coordinate system (feature) for the UR5 robot,
    defined by 3 calibration points: origin, x-axis, and xy-plane.

    The origin sets the coordinate center, the x-axis point defines
    the X direction, and the xy-plane point defines the XY plane.
    The Z axis is computed via the right-hand rule.
    """

    def __init__(self, origin: TCP, xAxis: TCP, xyPlane: TCP):
        self.Origin = origin
        self.XYPlane = xyPlane

        origin_pos = origin.position()
        xAxis_pos = xAxis.position()
        xyPlane_pos = xyPlane.position()

        xVector = NP.array(
            [
                xAxis_pos[0] - origin_pos[0],
                xAxis_pos[1] - origin_pos[1],
                xAxis_pos[2] - origin_pos[2],
            ]
        )

        x_norm = NP.linalg.norm(xVector)
        if x_norm < 1e-9:
            raise ValueError(
                "Origin and X-axis points are coincident or too close "
                f"(distance={x_norm:.2e}). Cannot define X axis."
            )
        self.XAxis = xVector / x_norm

        pVector = NP.array(
            [
                xyPlane_pos[0] - origin_pos[0],
                xyPlane_pos[1] - origin_pos[1],
                xyPlane_pos[2] - origin_pos[2],
            ]
        )

        zVector = NP.cross(xVector, pVector)
        z_norm = NP.linalg.norm(zVector)
        if z_norm < 1e-9:
            raise ValueError(
                "Calibration points are collinear — cannot define a plane. "
                "The XY-plane point must not be on the same line as origin and X-axis."
            )
        self.ZAxis = zVector / z_norm

        yVector = NP.cross(self.ZAxis, self.XAxis)
        self.YAxis = yVector / NP.linalg.norm(yVector)

    def getNewTCPByXYZMove(self, currentTCP: TCP, x: float, y: float, z: float) -> TCP:
        """Returns a new TCP moved by (x, y, z) in the feature's coordinate system."""
        newTCP = copy.deepcopy(currentTCP)
        # Copy orientation from origin
        newTCP.TCP[3:] = self.Origin.TCP[3:]
        newTCP.TCP[0] += x * self.XAxis[0] + y * self.YAxis[0] + z * self.ZAxis[0]
        newTCP.TCP[1] += x * self.XAxis[1] + y * self.YAxis[1] + z * self.ZAxis[1]
        newTCP.TCP[2] += x * self.XAxis[2] + y * self.YAxis[2] + z * self.ZAxis[2]
        return newTCP

    def getFeatureRelativeTCP(self, x: float, y: float, z: float) -> TCP:
        """Returns a new TCP at (x, y, z) relative to the feature origin."""
        newTCP = copy.deepcopy(self.Origin)
        newTCP.TCP[0] += x * self.XAxis[0] + y * self.YAxis[0] + z * self.ZAxis[0]
        newTCP.TCP[1] += x * self.XAxis[1] + y * self.YAxis[1] + z * self.ZAxis[1]
        newTCP.TCP[2] += x * self.XAxis[2] + y * self.YAxis[2] + z * self.ZAxis[2]
        return newTCP
