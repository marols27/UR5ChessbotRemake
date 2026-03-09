"""
Design system & component factories for the UR5 Chessbot UI.

Centralizes all design tokens (colors, fonts, spacing) and provides factory
functions for common UI components to eliminate copy-pasted styling constants.
"""

import customtkinter as ctk

# ------------------------------------------------------------------
# Colors
# ------------------------------------------------------------------
BG_PRIMARY = "#1a1a2e"       # Deepest background (root window)
BG_SECONDARY = "#16213e"     # Cards, panels
BG_TERTIARY = "#0f3460"      # Elevated surfaces, active cards
BG_INPUT = "#1e2d4d"         # Input fields, text boxes

ACCENT = "#00cdac"           # Primary teal accent
ACCENT_HOVER = "#00b89c"     # Teal hover state

BORDER_SUBTLE = "#2a3a5e"    # Subtle borders (replaces 10px white)
BORDER_ACTIVE = ACCENT       # Active/selected border

TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#94a3b8"   # Muted text
TEXT_ON_ACCENT = "#000000"   # Text on teal buttons

STATUS_GREEN = "#22c55e"     # Connected / success
STATUS_RED = "#ef4444"       # Disconnected / error / danger
STATUS_AMBER = "#f59e0b"     # Simulated / warning
STATUS_RED_HOVER = "#dc2626"

# Chessboard
BOARD_LIGHT = "#f0d9b5"
BOARD_DARK = "#b58863"
BOARD_HIGHLIGHT = "#aaf0aa"
BOARD_SELECT = "#7fc97f"
BOARD_NAV_HIGHLIGHT = "#ffff00"

# Difficulty accent colors
DIFF_EASY = STATUS_GREEN
DIFF_MEDIUM = STATUS_AMBER
DIFF_HARD = STATUS_RED

# ------------------------------------------------------------------
# Typography
# ------------------------------------------------------------------
def font_h1():
    return ctk.CTkFont(size=42, weight="bold")

def font_h2():
    return ctk.CTkFont(size=32, weight="bold")

def font_h3():
    return ctk.CTkFont(size=24, weight="bold")

def font_body():
    return ctk.CTkFont(size=18)

def font_button():
    return ctk.CTkFont(size=24, weight="bold")

def font_small():
    return ctk.CTkFont(size=14)

def font_mono():
    return ctk.CTkFont(family="monospace", size=18)

# ------------------------------------------------------------------
# Touch targets & spacing
# ------------------------------------------------------------------
BUTTON_HEIGHT = 70
BUTTON_HEIGHT_LARGE = 90
TOUCH_MIN = 60
CORNER_RADIUS = 16
BORDER_WIDTH = 2

# ------------------------------------------------------------------
# Component factories
# ------------------------------------------------------------------

def primary_button(parent, text, command, **kwargs):
    """Teal accent button for primary actions (Play, Confirm, Start)."""
    defaults = dict(
        text=text,
        command=command,
        font=font_button(),
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        text_color=TEXT_ON_ACCENT,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_SUBTLE,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT_LARGE,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def secondary_button(parent, text, command, **kwargs):
    """Outlined button for secondary actions (Configure, Back)."""
    defaults = dict(
        text=text,
        command=command,
        font=font_button(),
        fg_color="transparent",
        hover_color=BG_TERTIARY,
        text_color=TEXT_PRIMARY,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_SUBTLE,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT_LARGE,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def danger_button(parent, text, command, **kwargs):
    """Red button for destructive actions (Exit, Resign)."""
    defaults = dict(
        text=text,
        command=command,
        font=font_button(),
        fg_color=STATUS_RED,
        hover_color=STATUS_RED_HOVER,
        text_color=TEXT_PRIMARY,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_SUBTLE,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT_LARGE,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def card_frame(parent, **kwargs):
    """Styled card frame with subtle border."""
    defaults = dict(
        fg_color=BG_SECONDARY,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_SUBTLE,
        border_width=BORDER_WIDTH,
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def heading(parent, text, level=1, **kwargs):
    """Create a heading label at the specified level (1-3)."""
    fonts = {1: font_h1, 2: font_h2, 3: font_h3}
    font_fn = fonts.get(level, font_h1)
    defaults = dict(
        text=text,
        font=font_fn(),
        text_color=TEXT_PRIMARY,
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)
