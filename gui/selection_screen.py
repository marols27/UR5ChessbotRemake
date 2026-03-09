"""
Selection screen: Card-based difficulty and color selection.

Modernized with dark theme, StatusBar, colored card borders, pre-selected defaults.
"""

import os
import customtkinter as ctk
from PIL import Image

from . import navigation
from .components.status_bar import StatusBar
from .theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BORDER_SUBTLE,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
    DIFF_EASY, DIFF_MEDIUM, DIFF_HARD,
    font_h2, font_h3, font_body, font_button,
    primary_button, secondary_button, card_frame, heading,
    CORNER_RADIUS, BORDER_WIDTH,
)


def show_selection_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    # Main container
    container = ctk.CTkFrame(root, fg_color=BG_PRIMARY, corner_radius=0)
    container.pack(fill="both", expand=True)

    # Status bar with back navigation
    status_bar = StatusBar(
        container,
        back_command=lambda: navigation.navigate_to_home(root),
        show_connections=True,
    )
    status_bar.pack(fill="x")

    # Content area
    content = ctk.CTkFrame(container, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=40, pady=20)
    content.grid_columnconfigure(0, weight=1)

    # State variables
    difficulty_var = ctk.StringVar(value="easy")
    color_var = ctk.StringVar(value="white")

    # Difficulty card colors
    diff_colors = {"easy": DIFF_EASY, "medium": DIFF_MEDIUM, "hard": DIFF_HARD}
    diff_labels = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}

    # ------------------------------------------------------------------
    # Difficulty section
    # ------------------------------------------------------------------
    heading(content, "Choose Difficulty", level=2).grid(
        row=0, column=0, pady=(10, 16), sticky="w"
    )

    diff_frame = ctk.CTkFrame(content, fg_color="transparent")
    diff_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
    diff_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="diff")

    diff_cards = {}

    def select_difficulty(value):
        difficulty_var.set(value)
        _update_diff_styles()

    for col, key in enumerate(["easy", "medium", "hard"]):
        card = ctk.CTkFrame(
            diff_frame,
            fg_color=BG_SECONDARY,
            corner_radius=CORNER_RADIUS,
            border_color=BORDER_SUBTLE,
            border_width=BORDER_WIDTH,
            cursor="hand2",
        )
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        diff_cards[key] = card

        label = ctk.CTkLabel(
            card,
            text=diff_labels[key],
            font=font_h3(),
            text_color=TEXT_PRIMARY,
        )
        label.pack(pady=24, padx=20)

        # Make entire card clickable
        for widget in [card, label]:
            widget.bind("<Button-1>", lambda e, k=key: select_difficulty(k))

    def _update_diff_styles():
        sel = difficulty_var.get()
        for key, card in diff_cards.items():
            if key == sel:
                card.configure(
                    border_color=diff_colors[key],
                    fg_color=BG_TERTIARY,
                )
            else:
                card.configure(
                    border_color=BORDER_SUBTLE,
                    fg_color=BG_SECONDARY,
                )

    # Pre-select default
    _update_diff_styles()

    # ------------------------------------------------------------------
    # Color section
    # ------------------------------------------------------------------
    heading(content, "Choose Color", level=2).grid(
        row=2, column=0, pady=(10, 16), sticky="w"
    )

    color_frame = ctk.CTkFrame(content, fg_color="transparent")
    color_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
    color_frame.grid_columnconfigure((0, 1), weight=1, uniform="color")

    color_cards = {}
    # Piece images for color cards
    base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
    king_images = {
        "white": os.path.join(base_path, "Chess_klt60.png"),
        "black": os.path.join(base_path, "Chess_kdt60.png"),
    }

    def select_color(value):
        color_var.set(value)
        _update_color_styles()

    for col, key in enumerate(["white", "black"]):
        card = ctk.CTkFrame(
            color_frame,
            fg_color=BG_SECONDARY,
            corner_radius=CORNER_RADIUS,
            border_color=BORDER_SUBTLE,
            border_width=BORDER_WIDTH,
            cursor="hand2",
        )
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        color_cards[key] = card

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(pady=20, padx=20)

        # King piece image
        img_path = king_images.get(key, "")
        if os.path.exists(img_path):
            king_img = ctk.CTkImage(Image.open(img_path), size=(48, 48))
            img_label = ctk.CTkLabel(inner, image=king_img, text="")
            img_label.pack(pady=(0, 8))
            img_label.bind("<Button-1>", lambda e, k=key: select_color(k))

        label = ctk.CTkLabel(
            inner,
            text=key.capitalize(),
            font=font_h3(),
            text_color=TEXT_PRIMARY,
        )
        label.pack()

        for widget in [card, inner, label]:
            widget.bind("<Button-1>", lambda e, k=key: select_color(k))

    def _update_color_styles():
        sel = color_var.get()
        for key, card in color_cards.items():
            if key == sel:
                card.configure(border_color=ACCENT, fg_color=BG_TERTIARY)
            else:
                card.configure(border_color=BORDER_SUBTLE, fg_color=BG_SECONDARY)

    # Pre-select default
    _update_color_styles()

    # ------------------------------------------------------------------
    # Action buttons
    # ------------------------------------------------------------------
    btn_frame = ctk.CTkFrame(content, fg_color="transparent")
    btn_frame.grid(row=4, column=0, pady=(20, 0), sticky="ew")
    btn_frame.grid_columnconfigure(1, weight=1)

    def handle_start():
        selected_difficulty = difficulty_var.get()
        selected_color = color_var.get()
        navigation.navigate_to_game(root, selected_color, selected_difficulty)

    back_btn = secondary_button(
        btn_frame, "Back", lambda: navigation.navigate_to_home(root)
    )
    back_btn.grid(row=0, column=0, padx=(0, 10), sticky="w")

    start_btn = primary_button(btn_frame, "Start Game", handle_start)
    start_btn.grid(row=0, column=2, padx=(10, 0), sticky="e")
