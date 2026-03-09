"""
Persistent status bar shown at the top of every screen.

Displays:
- Optional back arrow (left)
- App title "HVL Chess Robot" (left)
- Connection indicators (right): Robot / DGT Board / Engine
- "SIM" badge when in simulation mode
- Optional game context text (e.g., "Your turn", "Robot thinking...")
"""

import customtkinter as ctk
from simulation import SIMULATION_MODE
from theme import (
    BG_SECONDARY, BG_TERTIARY, BORDER_SUBTLE, BORDER_WIDTH,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
    STATUS_GREEN, STATUS_RED, STATUS_AMBER,
    font_body, font_small, CORNER_RADIUS,
)


class StatusBar(ctk.CTkFrame):
    """Top status bar with connection indicators and navigation."""

    def __init__(self, parent, back_command=None, show_connections=True, **kwargs):
        super().__init__(
            parent,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            border_color=BORDER_SUBTLE,
            border_width=1,
            height=50,
            **kwargs,
        )
        self.pack_propagate(False)

        # Left section
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=10, fill="y")

        if back_command:
            back_btn = ctk.CTkButton(
                left,
                text="<",
                width=40,
                height=36,
                fg_color="transparent",
                hover_color=BG_TERTIARY,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=22),
                corner_radius=8,
                command=back_command,
            )
            back_btn.pack(side="left", padx=(0, 6))

        title = ctk.CTkLabel(
            left,
            text="HVL Chess Robot",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        title.pack(side="left")

        # Context text (optional, updated dynamically)
        self._context_label = ctk.CTkLabel(
            left,
            text="",
            font=font_body(),
            text_color=TEXT_SECONDARY,
        )
        self._context_label.pack(side="left", padx=(16, 0))

        # Right section
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=10, fill="y")

        # SIM badge
        if SIMULATION_MODE:
            sim_badge = ctk.CTkLabel(
                right,
                text=" SIM ",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=STATUS_AMBER,
                text_color="#000000",
                corner_radius=6,
                width=44,
                height=24,
            )
            sim_badge.pack(side="right", padx=(8, 0), pady=12)

        # Connection indicators
        if show_connections:
            self._indicators = {}
            for name in ["Engine", "DGT", "Robot"]:
                indicator = _ConnectionDot(right, label=name)
                indicator.pack(side="right", padx=(8, 0))
                self._indicators[name.lower()] = indicator

            # Set initial states based on simulation
            if SIMULATION_MODE:
                self.set_connection("robot", "simulated")
                self.set_connection("dgt", "simulated")
                self.set_connection("engine", "connected")
        else:
            self._indicators = {}

    def set_connection(self, name: str, state: str):
        """Update a connection indicator.

        Args:
            name: 'robot', 'dgt', or 'engine'
            state: 'connected', 'disconnected', or 'simulated'
        """
        indicator = self._indicators.get(name)
        if indicator:
            indicator.set_state(state)

    def set_context(self, text: str):
        """Update the context text (e.g., 'Your turn', 'Robot thinking...')."""
        self._context_label.configure(text=text)


class _ConnectionDot(ctk.CTkFrame):
    """Small labeled connection indicator dot."""

    _STATE_COLORS = {
        "connected": STATUS_GREEN,
        "disconnected": STATUS_RED,
        "simulated": STATUS_AMBER,
    }

    def __init__(self, parent, label: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._dot = ctk.CTkLabel(
            self,
            text="*",
            font=ctk.CTkFont(size=14),
            text_color=STATUS_RED,
            width=16,
        )
        self._dot.pack(side="left")

        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=font_small(),
            text_color=TEXT_SECONDARY,
        )
        self._label.pack(side="left", padx=(2, 0))

    def set_state(self, state: str):
        color = self._STATE_COLORS.get(state, STATUS_RED)
        self._dot.configure(text_color=color)
