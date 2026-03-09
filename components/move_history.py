"""
MoveHistory component: Displays the game move history with navigation.

Fixes over original:
- Uses a cloned chess.Board (not the shared game board reference)
- reset_to_current() correctly sets is_current = True (was False)
- Navigation doesn't corrupt the game state
- Colors imported from theme, touch-friendly nav buttons
"""

import chess
import customtkinter as ctk
from theme import (
    BG_SECONDARY, BG_INPUT, BORDER_SUBTLE, BORDER_WIDTH, CORNER_RADIUS,
    TEXT_PRIMARY, TEXT_SECONDARY, BOARD_NAV_HIGHLIGHT,
    font_h3, font_body, font_mono, TOUCH_MIN,
    heading as make_heading,
)


class MoveHistory(ctk.CTkFrame):
    def __init__(self, parent, board_canvas, game, *args, **kwargs):
        super().__init__(parent, fg_color="transparent", *args, **kwargs)
        self.board_canvas = board_canvas
        self.game = game
        self._display_board = chess.Board()
        self.current_move_index = -1
        self.is_current = True
        self.moves = []

        # Header
        header = make_heading(self, "Moves", level=3)
        header.grid(row=0, column=0, columnspan=4, pady=(0, 8), sticky="ew")

        # Textbox for moves (monospace)
        self.move_history_text = ctk.CTkTextbox(
            self,
            height=300,
            width=400,
            font=font_mono(),
            fg_color=BG_INPUT,
            text_color=TEXT_PRIMARY,
            wrap="word",
            padx=10,
            pady=10,
            corner_radius=CORNER_RADIUS,
            border_color=BORDER_SUBTLE,
            border_width=1,
        )
        self.move_history_text.grid(row=1, column=0, columnspan=4, pady=(0, 8))

        # Navigation buttons (60px+ height for touch)
        ARROW_SIZE = 24
        nav_style = dict(
            width=60,
            height=TOUCH_MIN,
            font=ctk.CTkFont(size=ARROW_SIZE),
            fg_color=BG_SECONDARY,
            hover_color=BG_INPUT,
            text_color=TEXT_PRIMARY,
            border_color=BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
        )

        ctk.CTkButton(
            self, text="\u00ab", command=self.first_move, **nav_style
        ).grid(row=2, column=0, pady=4, padx=3)

        ctk.CTkButton(
            self, text="\u2039", command=self.prev_move, **nav_style
        ).grid(row=2, column=1, pady=4, padx=3)

        ctk.CTkButton(
            self, text="\u203a", command=self.next_move, **nav_style
        ).grid(row=2, column=2, pady=4, padx=3)

        ctk.CTkButton(
            self, text="\u00bb", command=self.last_move, **nav_style
        ).grid(row=2, column=3, pady=4, padx=3)

    def load_moves(self, board: chess.Board):
        self.moves = list(board.move_stack)
        self.current_move_index = len(self.moves) - 1
        self.is_current = True
        self.update_move_history()

    def update_move_history(self):
        self.move_history_text.delete("1.0", "end")
        self._display_board.reset()

        move_line = ""
        for i, move in enumerate(self.moves):
            san_move = self._display_board.san(move)
            self._display_board.push(move)

            if i % 2 == 0:
                move_line = f"{i // 2 + 1}. {san_move}".ljust(40)
            else:
                move_line += f"{san_move}"
                self.move_history_text.insert("end", move_line + "\n")
                move_line = ""

            if i == self.current_move_index:
                self.highlight_current_move_squares(move)

        if move_line:
            self.move_history_text.insert("end", move_line + "\n")

    def highlight_current_move_squares(self, move):
        start_file = chess.square_file(move.from_square)
        start_rank = chess.square_rank(move.from_square)
        end_file = chess.square_file(move.to_square)
        end_rank = chess.square_rank(move.to_square)

        self.board_canvas.update_board(self._display_board.fen())
        self.board_canvas.highlight_square(
            start_file, start_rank, color=BOARD_NAV_HIGHLIGHT
        )
        self.board_canvas.highlight_square(
            end_file, end_rank, color=BOARD_NAV_HIGHLIGHT
        )

    def first_move(self):
        if not self.moves:
            return
        self.is_current = False
        self.current_move_index = 0
        self.render_current_position()

    def prev_move(self):
        if self.current_move_index > 0:
            self.is_current = False
            self.current_move_index -= 1
            self.render_current_position()

    def next_move(self):
        if self.current_move_index < len(self.moves) - 1:
            self.is_current = False
            self.current_move_index += 1
            self.render_current_position()

    def last_move(self):
        if not self.moves:
            return
        self.current_move_index = len(self.moves) - 1
        self.is_current = True
        self.render_current_position()

    def render_current_position(self):
        self._display_board.reset()
        for move in self.moves[: self.current_move_index + 1]:
            self._display_board.push(move)
        self.board_canvas.update_board(self._display_board.fen())
        self.update_move_history()

    def reset_to_current(self):
        self.is_current = True
        if self.moves:
            self.current_move_index = len(self.moves) - 1
        else:
            self.current_move_index = -1

        self._display_board.reset()
        for move in self.moves:
            self._display_board.push(move)
        self.board_canvas.update_board(self._display_board.fen())

    def get_current_fen(self):
        return self._display_board.fen()
