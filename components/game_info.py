"""
Game info panel: Turn indicator, inline status messages, and last move display.

Replaces most CTkMessagebox popups on the game screen with inline feedback.
"""

import customtkinter as ctk
from theme import (
    BG_SECONDARY, BG_TERTIARY, BORDER_SUBTLE, BORDER_WIDTH,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT,
    STATUS_GREEN, STATUS_RED, STATUS_AMBER,
    font_h2, font_h3, font_body, font_small, CORNER_RADIUS,
    card_frame,
)


class GameInfoPanel(ctk.CTkFrame):
    """Right-side panel showing turn indicator, status, and last move."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        # Turn indicator card
        turn_card = card_frame(self)
        turn_card.pack(fill="x", pady=(0, 10))

        self._turn_label = ctk.CTkLabel(
            turn_card,
            text="Setting up...",
            font=font_h3(),
            text_color=TEXT_SECONDARY,
        )
        self._turn_label.pack(padx=16, pady=14)

        # Status message card
        status_card = card_frame(self)
        status_card.pack(fill="x", pady=(0, 10))

        status_header = ctk.CTkLabel(
            status_card,
            text="Status",
            font=font_small(),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        status_header.pack(padx=16, pady=(10, 0), anchor="w")

        self._status_label = ctk.CTkLabel(
            status_card,
            text="Waiting to start...",
            font=font_body(),
            text_color=TEXT_PRIMARY,
            wraplength=280,
            anchor="w",
            justify="left",
        )
        self._status_label.pack(padx=16, pady=(4, 12), anchor="w")

        # Last move card
        move_card = card_frame(self)
        move_card.pack(fill="x", pady=(0, 10))

        move_header = ctk.CTkLabel(
            move_card,
            text="Last Move",
            font=font_small(),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        move_header.pack(padx=16, pady=(10, 0), anchor="w")

        self._move_label = ctk.CTkLabel(
            move_card,
            text="\u2014",
            font=font_h2(),
            text_color=ACCENT,
        )
        self._move_label.pack(padx=16, pady=(4, 12))

        # Animation state
        self._anim_id = None
        self._anim_dots = 0

    def set_turn(self, is_human: bool):
        """Update the turn indicator."""
        self._stop_animation()
        if is_human:
            self._turn_label.configure(
                text="Your Turn",
                text_color=STATUS_GREEN,
            )
        else:
            self._anim_dots = 0
            self._animate_thinking()

    def _animate_thinking(self):
        """Animate 'Robot Thinking...' with cycling dots."""
        dots = "." * (self._anim_dots % 4)
        self._turn_label.configure(
            text=f"Robot Thinking{dots}",
            text_color=STATUS_AMBER,
        )
        self._anim_dots += 1
        self._anim_id = self._turn_label.after(500, self._animate_thinking)

    def _stop_animation(self):
        if self._anim_id is not None:
            self._turn_label.after_cancel(self._anim_id)
            self._anim_id = None

    def set_status(self, text: str, level: str = "info"):
        """Show an inline status message.

        Args:
            text: Message to display
            level: 'info', 'error', or 'success'
        """
        colors = {
            "info": TEXT_PRIMARY,
            "error": STATUS_RED,
            "success": STATUS_GREEN,
        }
        self._status_label.configure(
            text=text,
            text_color=colors.get(level, TEXT_PRIMARY),
        )

    def set_last_move(self, move_san: str):
        """Update the last move display."""
        self._move_label.configure(text=move_san)

    def destroy(self):
        self._stop_animation()
        super().destroy()
