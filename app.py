"""
Main application entry point.

Fixes:
- Uses customtkinter for consistent theming
- Proper window close handler
- Logging configuration
"""

import logging
import customtkinter as ctk
from navigation import navigate_to_home

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class App:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("HVL Chess Robot")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        navigate_to_home(self.root)
        self.root.mainloop()

    def _on_close(self):
        """Clean up and close the application."""
        self.root.destroy()


def main():
    App()


if __name__ == "__main__":
    main()
