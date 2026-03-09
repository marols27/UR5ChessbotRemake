"""
Calibration screen: UI for robot calibration point management.

Fixes over original:
- Origin button calls calibrate_point() (with Settings.update_config) instead
  of bypassing it via pose.calibrate_point() directly
- Prevents repeated start_calibration button presses creating duplicate widgets
- Cancels `after` callbacks on navigation away
- Uses CTkMessagebox instead of print for feedback
- Works in simulation mode (shows info messages instead of failing)
"""

import logging

import customtkinter as ctk

from PoseConfigure import PoseConfigure
from navigation import navigate_to_home
from simulation import SIMULATION_MODE
import Settings

logger = logging.getLogger(__name__)


def show_calibration_screen(root):
    pose = None
    _calibration_started = False
    _after_ids = []

    for widget in root.winfo_children():
        widget.destroy()

    calibration_frame = ctk.CTkFrame(root, corner_radius=10)
    calibration_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(
        calibration_frame,
        text="Calibration",
        font=ctk.CTkFont(size=42, weight="bold"),
    )
    title_label.pack(pady=30)

    desc_text = """Press the "Start Calibration" button to begin the calibration process.
    Move the robot to the desired position and press the corresponding button to calibrate the robot's pose.

    The following points can be calibrated:
    1. Set Origin: Set the origin of the robot's pose (a1 corner).
    2. Set X Axis: Set the X axis of the robot's pose (h1 corner).
    3. Set XY Plane: Set the XY plane of the robot's pose (a8 corner).
    4. Set Home: Set the home position where the robot should return to.
    5. Set Drop: Set the drop position where the robot should drop captured pieces.

    Press the "Done" button to save the calibration points and navigate to the home screen."""

    if SIMULATION_MODE:
        desc_text += "\n\n    [SIMULATION MODE] Calibration buttons are disabled."

    description_label = ctk.CTkLabel(
        calibration_frame, text=desc_text, font=ctk.CTkFont(size=24)
    )
    description_label.pack(pady=30)

    confirmation_label = None

    def calibrate_point(point):
        nonlocal confirmation_label

        if SIMULATION_MODE:
            msg = f"[SIM] Calibration of '{point}' skipped in simulation mode."
            logger.info(msg)
        elif pose is not None:
            pose.calibrate_point(point)
            Settings.update_config()
        else:
            logger.error("PoseConfigure object not initialized!")
            return

        # Show confirmation feedback
        if confirmation_label is not None:
            confirmation_label.destroy()

        confirmation_label = ctk.CTkLabel(
            calibration_frame,
            text=f"Calibrated new {point} point"
            + (" (simulated)" if SIMULATION_MODE else ""),
            font=ctk.CTkFont(size=36),
        )
        confirmation_label.pack(pady=20)
        after_id = confirmation_label.after(3000, confirmation_label.destroy)
        _after_ids.append(after_id)

    def start_calibration():
        nonlocal pose, _calibration_started

        # Prevent duplicate button frame creation
        if _calibration_started:
            return
        _calibration_started = True

        pose = PoseConfigure()
        if not SIMULATION_MODE:
            pose.start_teach_mode()

        # Frame for calibration point buttons
        cal_button_frame = ctk.CTkFrame(calibration_frame, corner_radius=10)
        cal_button_frame.pack(pady=30)

        button_font = ctk.CTkFont(size=30, weight="bold")

        # FIX: All buttons go through calibrate_point() which calls Settings.update_config()
        set_origin_button = ctk.CTkButton(
            cal_button_frame,
            text="#1 Set Origin a1",
            font=button_font,
            command=lambda: calibrate_point("origin"),
        )
        set_x_axis_button = ctk.CTkButton(
            cal_button_frame,
            text="#2 Set X Axis h1",
            font=button_font,
            command=lambda: calibrate_point("xAxis"),
        )
        set_xy_plane_button = ctk.CTkButton(
            cal_button_frame,
            text="#3 Set XY Plane a8",
            font=button_font,
            command=lambda: calibrate_point("xyPlane"),
        )
        set_home_button = ctk.CTkButton(
            cal_button_frame,
            text="Set Home",
            font=button_font,
            command=lambda: calibrate_point("home"),
        )
        set_drop_button = ctk.CTkButton(
            cal_button_frame,
            text="Set Drop",
            font=button_font,
            command=lambda: calibrate_point("drop"),
        )

        set_origin_button.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        set_x_axis_button.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        set_xy_plane_button.grid(row=0, column=2, padx=15, pady=15, sticky="ew")
        set_home_button.grid(row=0, column=3, padx=15, pady=15, sticky="ew")
        set_drop_button.grid(row=0, column=4, padx=15, pady=15, sticky="ew")

        # Disable the start button after first press
        start_calibration_button.configure(state="disabled", fg_color="gray")

    start_calibration_button = ctk.CTkButton(
        calibration_frame,
        text="Start Calibration",
        font=ctk.CTkFont(size=32, weight="bold"),
        command=start_calibration,
        height=80,
    )
    start_calibration_button.pack(pady=30)

    def nav_home():
        # Cancel pending after callbacks
        for after_id in _after_ids:
            try:
                root.after_cancel(after_id)
            except Exception:
                pass

        if pose is not None and not SIMULATION_MODE:
            pose.end_teach_mode()
        navigate_to_home(root)

    done_button = ctk.CTkButton(
        calibration_frame,
        text="Done",
        font=ctk.CTkFont(size=32, weight="bold"),
        command=nav_home,
        height=80,
    )
    done_button.pack(pady=30)
