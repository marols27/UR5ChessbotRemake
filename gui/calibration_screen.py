"""
Calibration screen: UI for robot calibration point management.

Redesigned with:
- StatusBar with back navigation
- Step indicator bar (5 labeled circles: green=done, teal=current, gray=todo)
- Only current step description shown
- Persistent status label for feedback
- Visual tracking of completed calibration points
"""

import logging

import customtkinter as ctk

from robot.PoseConfigure import PoseConfigure
from .navigation import navigate_to_home
from robot.simulation import SIMULATION_MODE
from .components.status_bar import StatusBar
from .theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BORDER_SUBTLE,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
    STATUS_GREEN, STATUS_AMBER,
    font_h2, font_h3, font_body, font_small,
    primary_button, secondary_button, danger_button, card_frame, heading,
    CORNER_RADIUS, BORDER_WIDTH,
)

logger = logging.getLogger(__name__)

# Calibration steps definition
_STEPS = [
    ("origin", "#1 Origin (a1)", "Move the robot to the a1 corner of the chessboard and press the button."),
    ("xAxis", "#2 X Axis (h1)", "Move the robot to the h1 corner of the chessboard and press the button."),
    ("xyPlane", "#3 XY Plane (a8)", "Move the robot to the a8 corner of the chessboard and press the button."),
    ("home", "#4 Home", "Move the robot to the desired home/rest position and press the button."),
    ("drop", "#5 Drop", "Move the robot to the position where captured pieces should be placed."),
]


def show_calibration_screen(root):
    pose = None
    _calibration_started = False
    _after_ids = []
    _completed_steps = set()
    _current_step = [0]  # mutable for closures

    for widget in root.winfo_children():
        widget.destroy()

    import robot.Settings as Settings

    # Main container
    container = ctk.CTkFrame(root, fg_color=BG_PRIMARY, corner_radius=0)
    container.pack(fill="both", expand=True)

    def nav_home():
        for after_id in _after_ids:
            try:
                root.after_cancel(after_id)
            except Exception:
                pass
        if pose is not None and not SIMULATION_MODE:
            pose.end_teach_mode()
        navigate_to_home(root)

    # Status bar
    status_bar = StatusBar(container, back_command=nav_home, show_connections=True)
    status_bar.pack(fill="x")

    # Content
    content = ctk.CTkFrame(container, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=40, pady=20)
    content.grid_columnconfigure(0, weight=1)

    # Title
    heading(content, "Calibration", level=1).grid(row=0, column=0, pady=(0, 20))

    # Step indicator frame
    step_frame = ctk.CTkFrame(content, fg_color="transparent")
    step_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
    for i in range(len(_STEPS)):
        step_frame.grid_columnconfigure(i * 2, weight=0)
        if i < len(_STEPS) - 1:
            step_frame.grid_columnconfigure(i * 2 + 1, weight=1)

    _step_dots = []
    _step_labels = []

    for i, (key, label, desc) in enumerate(_STEPS):
        col = i * 2

        # Dot
        dot = ctk.CTkLabel(
            step_frame,
            text="*",
            font=ctk.CTkFont(size=28),
            text_color=TEXT_SECONDARY,
            width=36,
        )
        dot.grid(row=0, column=col, padx=4)
        _step_dots.append(dot)

        # Label below dot
        step_lbl = ctk.CTkLabel(
            step_frame,
            text=label,
            font=font_small(),
            text_color=TEXT_SECONDARY,
        )
        step_lbl.grid(row=1, column=col, padx=4)
        _step_labels.append(step_lbl)

        # Connector line between dots
        if i < len(_STEPS) - 1:
            line = ctk.CTkFrame(
                step_frame,
                fg_color=BORDER_SUBTLE,
                height=2,
            )
            line.grid(row=0, column=col + 1, sticky="ew", padx=4, pady=14)

    def _update_step_indicators():
        for i, (key, label, desc) in enumerate(_STEPS):
            if key in _completed_steps:
                _step_dots[i].configure(text_color=STATUS_GREEN)
                _step_labels[i].configure(text_color=STATUS_GREEN)
            elif i == _current_step[0] and _calibration_started:
                _step_dots[i].configure(text_color=ACCENT)
                _step_labels[i].configure(text_color=ACCENT)
            else:
                _step_dots[i].configure(text_color=TEXT_SECONDARY)
                _step_labels[i].configure(text_color=TEXT_SECONDARY)

    # Description card for current step
    desc_card = card_frame(content)
    desc_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))

    _desc_label = ctk.CTkLabel(
        desc_card,
        text='Press "Start Calibration" to begin.' if not SIMULATION_MODE
        else "[SIMULATION MODE] Calibration buttons will be simulated.",
        font=font_body(),
        text_color=TEXT_PRIMARY,
        wraplength=700,
    )
    _desc_label.pack(padx=20, pady=16)

    # Persistent status label
    _status_label = ctk.CTkLabel(
        content,
        text="",
        font=font_body(),
        text_color=STATUS_GREEN,
    )
    _status_label.grid(row=3, column=0, pady=(0, 10))

    def _show_current_step_desc():
        idx = _current_step[0]
        if 0 <= idx < len(_STEPS):
            _, label, desc = _STEPS[idx]
            _desc_label.configure(text=desc)
        _update_step_indicators()

    def calibrate_point(point):
        if SIMULATION_MODE:
            msg = f"[SIM] Calibration of '{point}' skipped in simulation mode."
            logger.info(msg)
        elif pose is not None:
            pose.calibrate_point(point)
            Settings.update_config()
        else:
            logger.error("PoseConfigure object not initialized!")
            return

        _completed_steps.add(point)
        suffix = " (simulated)" if SIMULATION_MODE else ""
        _status_label.configure(
            text=f"Calibrated: {point}{suffix}",
            text_color=STATUS_GREEN,
        )

        # Advance to next uncompleted step
        for i, (key, _, _) in enumerate(_STEPS):
            if key not in _completed_steps:
                _current_step[0] = i
                break
        else:
            _current_step[0] = len(_STEPS)
            _desc_label.configure(text="All points calibrated! Press Done to save.")

        _show_current_step_desc()

    # Calibration point buttons frame (hidden until started)
    cal_button_frame = ctk.CTkFrame(content, fg_color="transparent")
    cal_button_frame.grid(row=4, column=0, pady=(0, 16))
    cal_button_frame.grid_remove()  # Hidden initially

    button_font = font_h3()
    for i, (key, label, desc) in enumerate(_STEPS):
        btn = secondary_button(
            cal_button_frame,
            label,
            lambda k=key: calibrate_point(k),
            font=button_font,
            height=60,
        )
        btn.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

    def start_calibration():
        nonlocal pose, _calibration_started

        if _calibration_started:
            return
        _calibration_started = True

        pose = PoseConfigure()
        if not SIMULATION_MODE:
            pose.start_teach_mode()

        # Show calibration buttons
        cal_button_frame.grid()

        # Update step indicator
        _current_step[0] = 0
        _show_current_step_desc()

        # Disable start button
        start_btn.configure(state="disabled", fg_color=TEXT_SECONDARY)

    # Action buttons
    btn_frame = ctk.CTkFrame(content, fg_color="transparent")
    btn_frame.grid(row=5, column=0, pady=(10, 0), sticky="ew")
    btn_frame.grid_columnconfigure(1, weight=1)

    start_btn = primary_button(
        btn_frame, "Start Calibration", start_calibration
    )
    start_btn.grid(row=0, column=0, padx=(0, 10))

    done_btn = secondary_button(btn_frame, "Done", nav_home)
    done_btn.grid(row=0, column=2, padx=(10, 0))
