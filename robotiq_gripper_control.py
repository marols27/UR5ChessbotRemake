"""
Robotiq gripper control via UR RTDE interface.

In simulation mode, all methods are no-ops that log their actions.
"""

import logging
import time

from simulation import SIMULATION_MODE

logger = logging.getLogger(__name__)


class RobotiqGripper:
    """
    Controls a Robotiq gripper through the UR RTDE control interface.

    In simulation mode, all calls are no-ops and log the requested action.
    """

    def __init__(self, rtde_c=None):
        self.simulation = SIMULATION_MODE
        self.rtde_c = rtde_c

        if not self.simulation:
            from robotiq_preamble import ROBOTIQ_PREAMBLE

            self._preamble = ROBOTIQ_PREAMBLE
            if rtde_c is None:
                raise ValueError("rtde_c is required when not in simulation mode")
        else:
            self._preamble = ""
            logger.info("RobotiqGripper running in SIMULATION mode")

    def call(self, script_name: str, script_function: str) -> bool:
        if self.simulation:
            logger.debug(f"[SIM] Gripper script call: {script_name}")
            return True
        return self.rtde_c.sendCustomScriptFunction(
            "ROBOTIQ_" + script_name,
            self._preamble + script_function,
        )

    def activate(self) -> bool:
        """Activate the gripper. Takes ~5 seconds on real hardware."""
        ret = self.call("ACTIVATE", "rq_activate()")
        if not self.simulation:
            time.sleep(5)
        return ret

    def set_speed(self, speed: int) -> bool:
        """Set gripper speed (0-100%)."""
        return self.call("SET_SPEED", f"rq_set_speed_norm({speed})")

    def set_force(self, force: int) -> bool:
        """Set gripper force (0-100%)."""
        return self.call("SET_FORCE", f"rq_set_force_norm({force})")

    def move(self, pos_in_mm: int) -> bool:
        """Move the gripper to a position in mm."""
        return self.call("MOVE", f"rq_move_and_wait_mm({pos_in_mm})")

    def open(self) -> bool:
        """Open the gripper."""
        return self.call("OPEN", "rq_open_and_wait()")

    def close(self) -> bool:
        """Close the gripper."""
        return self.call("CLOSE", "rq_close_and_wait()")
