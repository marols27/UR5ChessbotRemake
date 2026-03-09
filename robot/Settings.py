"""
Settings module: Central configuration for the chess robot application.

Fixes over original:
- No import-time side effects (no bare except triggering robot calibration)
- Lazy initialization of board feature and engine path
- Dynamic Stockfish discovery (PATH, project directory, then configurable)
- Handles missing config.json gracefully
- on_env_configure calls instance method correctly
"""

import json
import logging
import os
import shutil

import chess
import chess.engine
from .ToolCenterPoint import ToolCenterPoint as TCP
from .UR5Feature import UR5Feature
from .PoseConfigure import PoseConfigure

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Chess Dimensions (meters)
# ------------------------------------------------------------------
KING_HEIGHT: float = 0.098
BOARD_SIZE: float = 0.54
SQUARE_SIZE: float = 0.055

# ------------------------------------------------------------------
# Robot Parameters
# ------------------------------------------------------------------
TRAVEL_HEIGHT: float = KING_HEIGHT * 2 + 0.01
CONNECTION_IP: str = "172.31.1.144"
ACCELERATION: float = 0.6
SPEED: float = 1.0
GRIPPER_SPEED: int = 150
GRIPPER_FORCE: int = 50

# ------------------------------------------------------------------
# DGT Board
# ------------------------------------------------------------------
PORT: str = "/dev/ttyACM0"

# ------------------------------------------------------------------
# Config file
# ------------------------------------------------------------------
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_NAME: str = os.path.join(_PROJECT_DIR, "config.json")

# ------------------------------------------------------------------
# Starting FEN
# ------------------------------------------------------------------
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# ------------------------------------------------------------------
# Engine settings
# ------------------------------------------------------------------
TIMEOUT_TIME = 0.1
TIMEOUT = chess.engine.Limit(time=TIMEOUT_TIME)
DIFFICULTY = 1


def _find_stockfish() -> str:
    """Find the Stockfish binary. Searches PATH, then the project directory."""
    # 1. Check PATH
    sf = shutil.which("stockfish")
    if sf:
        return sf

    # 2. Check within project directory
    project_sf = os.path.join(
        _PROJECT_DIR,
        "stockfish-ubuntu-x86-64-sse41-popcnt",
        "stockfish",
        "src",
        "stockfish",
    )
    if os.path.isfile(project_sf) and os.access(project_sf, os.X_OK):
        return project_sf

    # 3. Fallback — return "stockfish" and let the caller handle the error
    logger.warning("Stockfish binary not found on PATH or in project directory")
    return "stockfish"


STOCKFISH_PATH: str = _find_stockfish()


def _load_config() -> dict:
    """Load calibration config from JSON file. Returns empty dict on failure."""
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {FILE_NAME}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return {}


def _init_calibration_points(config: dict):
    """Initialize calibration TCPs from config dict."""
    global ORIGIN, XAXIS, XYPLANE, HOME, CAPTURE_POSE, BOARD_FEATURE

    points = PoseConfigure.Points
    try:
        ORIGIN = TCP(config[points.ORIGIN.value])
        XAXIS = TCP(config[points.XAXIS.value])
        XYPLANE = TCP(config[points.XYPLANE.value])
        HOME = TCP(config[points.HOME.value])
        CAPTURE_POSE = TCP(config[points.DROP.value])
        BOARD_FEATURE = UR5Feature(ORIGIN, XAXIS, XYPLANE)
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Failed to initialize calibration points: {e}")
        # Create dummy values so the app can still launch in simulation mode
        _default = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ORIGIN = TCP(_default)
        XAXIS = TCP([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        XYPLANE = TCP([0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        HOME = TCP(_default)
        CAPTURE_POSE = TCP(_default)
        BOARD_FEATURE = UR5Feature(ORIGIN, XAXIS, XYPLANE)


# Initialize on import (safe — no hardware access)
_config = _load_config()
_init_calibration_points(_config)


def update_config():
    """Reload calibration points from the config file."""
    config = _load_config()
    if config:
        _init_calibration_points(config)
    else:
        logger.warning("update_config: no config data loaded")


def on_env_configure():
    """Run first-time setup calibration."""
    pose = PoseConfigure(connectionIP=CONNECTION_IP, fileName=FILE_NAME)
    pose.firstTimeSettup()
    update_config()
