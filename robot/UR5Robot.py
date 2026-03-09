"""
UR5Robot: High-level interface for a UR5 robot playing chess.

Provides basic movements (goto, grab, drop) and combined chess movements
(movePiece, capturePiece, enPassant, castle, promotion).

In simulation mode, all physical movements are logged but not executed.

Fixes over original:
- No bare except: clauses (catches specific exceptions)
- Constructor does not disconnect immediately after setup
- Simulation mode for testing without hardware
- Proper resource cleanup via close()
"""

import copy
import logging

from .ToolCenterPoint import ToolCenterPoint as TCP
from .simulation import SIMULATION_MODE

logger = logging.getLogger(__name__)


class UR5Robot:
    """UR5 robot controller for chess piece manipulation."""

    def __init__(
        self,
        travelHeight: float,
        homePose: TCP,
        connectionIP: str,
        acceleration: float,
        speed: float,
        gripperSpeed: float,
        gripperForce: float,
    ):
        self.travelHeight = travelHeight
        self.homePose = homePose
        self.connectionIP = connectionIP
        self.acceleration = acceleration
        self.speed = speed
        self.gripperSpeed = gripperSpeed
        self.gripperForce = gripperForce
        self.simulation = SIMULATION_MODE

        self.control = None
        self.info = None
        self.gripper = None

        if not self.simulation:
            self._connect()
        else:
            logger.info("UR5Robot running in SIMULATION mode")

    def _connect(self):
        """Establish connections to the robot hardware."""
        import rtde_control
        import rtde_receive
        from .robotiq_gripper_control import RobotiqGripper

        self.control = rtde_control.RTDEControlInterface(self.connectionIP)
        self.info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        self.gripper = RobotiqGripper(self.control)
        self.gripper.activate()
        self.gripper.set_force(self.gripperForce)
        self.gripper.set_speed(self.gripperSpeed)
        self.drop()  # Open gripper to start
        logger.info(f"UR5Robot connected to {self.connectionIP}")

    def _reconnect(self):
        """Reconnect to the robot if the connection was lost."""
        if self.simulation:
            return
        try:
            if self.control and self.control.isConnected():
                self.control.disconnect()
            self.control.reconnect()
            if self.info and self.info.isConnected():
                self.info.disconnect()
            self.info.reconnect()
        except Exception as e:
            logger.error(f"Failed to reconnect: {e}")
            raise

    def close(self):
        """Clean up robot connections."""
        if self.simulation:
            return
        try:
            if self.control and self.control.isConnected():
                self.control.disconnect()
            if self.info and self.info.isConnected():
                self.info.disconnect()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Basic movements
    # ------------------------------------------------------------------

    def goto(self, pos: "list[float]"):
        """Move the robot to the specified TCP position."""
        if self.simulation:
            logger.debug(f"[SIM] goto({pos[:3]}...)")
            return
        try:
            self.control.moveL(pos, self.speed, self.acceleration)
        except RuntimeError:
            logger.warning("moveL failed, attempting reconnect...")
            self._reconnect()
            self.control.moveL(pos, self.speed, self.acceleration)

    def grab(self):
        """Close the gripper to grab a piece."""
        if self.simulation:
            logger.debug("[SIM] grab()")
            return
        try:
            self.gripper.move(6)
        except RuntimeError:
            logger.warning("grab failed, attempting reconnect...")
            self._reconnect()
            self.gripper.activate()
            self.gripper.set_force(self.gripperForce)
            self.gripper.set_speed(self.gripperSpeed)
            self.gripper.move(37)
            self.gripper.move(6)

    def drop(self):
        """Open the gripper to drop a piece."""
        if self.simulation:
            logger.debug("[SIM] drop()")
            return
        try:
            self.gripper.move(37)
        except RuntimeError:
            logger.warning("drop failed, attempting reconnect...")
            self._reconnect()
            self.gripper.activate()
            self.gripper.set_force(self.gripperForce)
            self.gripper.set_speed(self.gripperSpeed)
            self.gripper.move(37)

    # ------------------------------------------------------------------
    # Combined movements
    # ------------------------------------------------------------------

    def home(self):
        """Move the robot to the predefined home position."""
        self.goto(self.homePose.TCP)

    def movePiece(
        self, fromPos: "list[float]", toPos: "list[float]", home: bool = True
    ):
        """Move a chess piece from one position to another."""
        aboveFrom = copy.deepcopy(fromPos)
        aboveFrom[2] += self.travelHeight
        aboveTo = copy.deepcopy(toPos)
        aboveTo[2] += self.travelHeight

        self.goto(aboveFrom)
        self.goto(fromPos)
        self.grab()
        self.goto(aboveFrom)
        self.goto(aboveTo)
        self.goto(toPos)
        self.drop()
        self.goto(aboveTo)
        if home:
            self.home()

    def capturePiece(
        self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"
    ):
        """Capture a piece: move captured piece to capturePos, then move attacking piece."""
        aboveTo = copy.deepcopy(toPos)
        aboveTo[2] += self.travelHeight
        self.goto(aboveTo)
        self.goto(toPos)
        self.grab()
        self.goto(aboveTo)
        self.goto(capturePos)
        self.drop()
        self.movePiece(fromPos, toPos)

    def enPassent(
        self,
        fromPos: "list[float]",
        toPos: "list[float]",
        targetPos: "list[float]",
        capturePos: "list[float]",
    ):
        """Perform an en passant capture."""
        self.movePiece(fromPos, toPos, home=False)
        self.movePiece(targetPos, capturePos)

    def castle(
        self,
        fromPosKing: "list[float]",
        toPosKing: "list[float]",
        fromPosRook: "list[float]",
        toPosRook: "list[float]",
    ):
        """Perform a castling move (king + rook)."""
        self.movePiece(fromPosKing, toPosKing, home=False)
        self.movePiece(fromPosRook, toPosRook)

    def promotion(self, fromPos: "list[float]", capturePos: "list[float]"):
        """Remove the pawn for promotion (user must place the new piece)."""
        self.movePiece(fromPos, capturePos)

    def capturePromotion(
        self, fromPos: "list[float]", toPos: "list[float]", capturePos: "list[float]"
    ):
        """Capture promotion: remove both pawn and captured piece."""
        self.movePiece(toPos, capturePos, home=False)
        self.movePiece(fromPos, capturePos)
