"""
Simulation mode support for running the chess robot without physical hardware.

When SIMULATION_MODE is True, mock implementations are used for:
- UR5Robot (logs moves instead of commanding the robot)
- DGTBoard (uses the internal chess.Board state)
- PoseConfigure (no-ops for calibration)
- RobotiqGripper (no-ops)

This allows the full UI to run for development and testing.
"""

import os

SIMULATION_MODE = os.environ.get("CHESSBOT_SIMULATE", "1") == "1"

# If hardware libraries are not available, force simulation mode
try:
    import rtde_control
    import rtde_receive
    import asyncdgt

    _HARDWARE_AVAILABLE = True
except ImportError:
    _HARDWARE_AVAILABLE = False
    SIMULATION_MODE = True
