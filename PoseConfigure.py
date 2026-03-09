"""
PoseConfigure: Robot calibration point management.

In simulation mode, calibration operations are no-ops.

Fixes over original:
- No import-time hardware initialization
- teach mode wrapped in try/finally
- start_teach_mode and end_teach_mode use the same connection
- Simulation mode support
"""

import json
import logging
from enum import Enum

from simulation import SIMULATION_MODE

logger = logging.getLogger(__name__)


class PoseConfigure:
    """Manages calibration points for the UR5 robot chess setup."""

    class Points(Enum):
        ORIGIN = "origin"
        XAXIS = "xAxis"
        XYPLANE = "xyPlane"
        HOME = "home"
        DROP = "drop"

    def __init__(
        self, connectionIP: str = "172.31.1.144", fileName: str = "config.json"
    ):
        self.connectionIP = connectionIP
        self.fileName = fileName
        self.simulation = SIMULATION_MODE
        self._control = None
        self._info = None

    def firstTimeSettup(
        self, connectionIP: str | None = None, fileName: str | None = None
    ):
        """
        Calibrate all 5 points interactively and save to config file.
        In simulation mode, creates a default config if none exists.
        """
        if connectionIP:
            self.connectionIP = connectionIP
        if fileName:
            self.fileName = fileName

        if self.simulation:
            logger.info("[SIM] firstTimeSettup: skipping (simulation mode)")
            return

        import rtde_control
        import rtde_receive
        from robotiq_gripper_control import RobotiqGripper

        control = rtde_control.RTDEControlInterface(self.connectionIP)
        info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        gripper = RobotiqGripper(control)
        gripper.activate()
        gripper.move(37)

        try:
            control.teachMode()
            config = {}

            input("Move the robot to the board origin and press enter...")
            config[self.Points.ORIGIN.value] = info.getActualTCPPose()

            input("Move the robot to the x axis and press enter...")
            config[self.Points.XAXIS.value] = info.getActualTCPPose()

            input("Move the robot to the xy plane and press enter...")
            config[self.Points.XYPLANE.value] = info.getActualTCPPose()

            input("Move the robot to the home position and press enter...")
            config[self.Points.HOME.value] = info.getActualTCPPose()

            input("Move the robot to the drop position and press enter...")
            config[self.Points.DROP.value] = info.getActualTCPPose()

            with open(self.fileName, "w") as f:
                json.dump(config, f)
            logger.info(f"Calibration saved to {self.fileName}")
        finally:
            control.endTeachMode()

    def recalibrate(
        self, point: str, connectionIP: str | None = None, fileName: str | None = None
    ):
        """Recalibrate a single point and update the config file."""
        if connectionIP:
            self.connectionIP = connectionIP
        if fileName:
            self.fileName = fileName

        if self.simulation:
            logger.info(f"[SIM] recalibrate({point}): skipping (simulation mode)")
            return

        import rtde_control
        import rtde_receive
        from robotiq_gripper_control import RobotiqGripper

        control = rtde_control.RTDEControlInterface(self.connectionIP)
        info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        gripper = RobotiqGripper(control)
        gripper.activate()
        gripper.move(37)

        try:
            with open(self.fileName, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Cannot read config file: {e}")
            return

        try:
            control.teachMode()
            input(f"Move the robot to the {point} point and press enter...")
            config[point] = info.getActualTCPPose()
            control.endTeachMode()

            with open(self.fileName, "w") as f:
                json.dump(config, f)
            logger.info(f"Recalibrated {point} and saved to {self.fileName}")
        except Exception as e:
            logger.error(f"Recalibration failed: {e}")
            control.endTeachMode()

    def start_teach_mode(self):
        """Enter teach mode (robot can be moved freely by hand)."""
        if self.simulation:
            logger.info("[SIM] start_teach_mode: skipping (simulation mode)")
            return

        import rtde_control
        import rtde_receive
        from robotiq_gripper_control import RobotiqGripper

        self._control = rtde_control.RTDEControlInterface(self.connectionIP)
        self._info = rtde_receive.RTDEReceiveInterface(self.connectionIP)
        gripper = RobotiqGripper(self._control)
        gripper.activate()
        gripper.move(37)
        self._control.teachMode()

    def end_teach_mode(self):
        """Exit teach mode. Uses the same connection as start_teach_mode."""
        if self.simulation:
            logger.info("[SIM] end_teach_mode: skipping (simulation mode)")
            return

        if self._control is not None:
            try:
                self._control.endTeachMode()
            except Exception as e:
                logger.error(f"Failed to end teach mode: {e}")
            finally:
                self._control = None
                self._info = None
        else:
            logger.warning("end_teach_mode called but no active teach mode session")

    def calibrate_point(self, point: str):
        """Calibrate a single point using the current teach mode session."""
        if self.simulation:
            logger.info(f"[SIM] calibrate_point({point}): skipping (simulation mode)")
            return

        if self._info is None:
            logger.error("calibrate_point called without active teach mode session")
            return

        try:
            with open(self.fileName, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        pose = self._info.getActualTCPPose()
        old_value = config.get(point)
        config[point] = pose
        logger.info(f"Calibrated {point}: {old_value} -> {pose}")

        with open(self.fileName, "w") as f:
            json.dump(config, f)
