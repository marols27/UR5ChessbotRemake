"""
Home screen: Main menu with Play Game, Configure Robot, and Exit buttons.

Modernized with dark theme, StatusBar, compact layout, and theme factories.
"""

import os
import customtkinter as ctk
from PIL import Image

from .navigation import navigate_to_selection, navigate_to_calibration
from .components.status_bar import StatusBar
from .theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY,
    font_h1, font_body, primary_button, secondary_button, danger_button,
    card_frame, heading, CORNER_RADIUS,
)


def show_home_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    # Main container
    container = ctk.CTkFrame(root, fg_color=BG_PRIMARY, corner_radius=0)
    container.pack(fill="both", expand=True)

    # Status bar
    status_bar = StatusBar(container, show_connections=True)
    status_bar.pack(fill="x")

    # Content area
    content = ctk.CTkFrame(container, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=40, pady=20)
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(1, weight=1)

    # Top section: logo + title + subtitle
    top = ctk.CTkFrame(content, fg_color="transparent")
    top.grid(row=0, column=0, sticky="ew", pady=(20, 0))
    top.grid_columnconfigure(1, weight=1)

    # Logo
    image_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "images", "robotics_logo.jpg"
    )
    if os.path.exists(image_path):
        logo_img = ctk.CTkImage(Image.open(image_path), size=(180, 180))
        logo_label = ctk.CTkLabel(top, image=logo_img, text="")
        logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 30))
    else:
        placeholder = ctk.CTkLabel(
            top, text="[Logo]", font=font_body(), text_color=TEXT_SECONDARY
        )
        placeholder.grid(row=0, column=0, rowspan=2, padx=(0, 30))

    # Title
    title = heading(top, "The HVL Robotics Chess Robot", level=1)
    title.grid(row=0, column=1, sticky="sw", pady=(0, 4))

    # Compact instructions
    instructions_text = (
        "Challenge the chess robot! Choose difficulty and color, "
        "then confirm each move. Let the robot finish before playing your next move."
    )
    instructions = ctk.CTkLabel(
        top,
        text=instructions_text,
        font=font_body(),
        text_color=TEXT_SECONDARY,
        wraplength=700,
        anchor="w",
        justify="left",
    )
    instructions.grid(row=1, column=1, sticky="nw")

    # Buttons section (centered at bottom)
    btn_area = ctk.CTkFrame(content, fg_color="transparent")
    btn_area.grid(row=1, column=0, sticky="s", pady=(0, 40))
    btn_area.grid_columnconfigure((0, 1, 2), weight=1, uniform="btns")

    play_btn = primary_button(
        btn_area, "Play Game", lambda: navigate_to_selection(root)
    )
    play_btn.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

    config_btn = secondary_button(
        btn_area, "Configure Robot", lambda: navigate_to_calibration(root)
    )
    config_btn.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

    exit_btn = danger_button(btn_area, "Exit", root.destroy)
    exit_btn.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
