"""
MoveHistory component: Displays the game move history with navigation.

Fixes over original:
- Uses a cloned chess.Board (not the shared game board reference)
- reset_to_current() correctly sets is_current = True (was False)
- Navigation doesn't corrupt the game state
"""

import chess
import customtkinter as ctk


class MoveHistory(ctk.CTkFrame):
    def __init__(self, parent, board_canvas, game, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.board_canvas = board_canvas
        self.game = game
        self._display_board = chess.Board()  # Private board for display only
        self.current_move_index = -1
        self.is_current = True
        self.moves = []

        # Label
        move_history_label = ctk.CTkLabel(
            self,
            text="Move History",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        move_history_label.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

        # Textbox for moves
        self.move_history_text = ctk.CTkTextbox(
            self,
            height=300,
            width=400,
            font=ctk.CTkFont(size=24),
            fg_color="#666666",
            text_color="white",
            wrap="word",
            padx=10,
            pady=10,
        )
        self.move_history_text.grid(row=1, column=0, columnspan=4, pady=10)

        # Navigation buttons
        ARROW_SIZE = 30
        back_button = ctk.CTkButton(
            self,
            text="<<",
            command=self.first_move,
            width=60,
            font=ctk.CTkFont(size=ARROW_SIZE),
        )
        back_button.grid(row=2, column=0, pady=10, padx=5)

        prev_button = ctk.CTkButton(
            self,
            text="<",
            command=self.prev_move,
            width=60,
            font=ctk.CTkFont(size=ARROW_SIZE),
        )
        prev_button.grid(row=2, column=1, pady=10, padx=5)

        next_button = ctk.CTkButton(
            self,
            text=">",
            command=self.next_move,
            width=60,
            font=ctk.CTkFont(size=ARROW_SIZE),
        )
        next_button.grid(row=2, column=2, pady=10, padx=5)

        forward_button = ctk.CTkButton(
            self,
            text=">>",
            command=self.last_move,
            width=60,
            font=ctk.CTkFont(size=ARROW_SIZE),
        )
        forward_button.grid(row=2, column=3, pady=10, padx=5)

    def load_moves(self, board: chess.Board):
        """
        Load moves from a chess.Board. Makes a copy of the move stack
        to avoid corrupting the game state.
        """
        # FIX: Copy the move list instead of storing a reference
        self.moves = list(board.move_stack)
        self.current_move_index = len(self.moves) - 1
        self.is_current = True
        self.update_move_history()

    def update_move_history(self):
        """Update the displayed move history text."""
        self.move_history_text.delete("1.0", "end")

        # FIX: Use our private display board, not the game board
        self._display_board.reset()

        move_line = ""
        for i, move in enumerate(self.moves):
            san_move = self._display_board.san(move)
            self._display_board.push(move)

            if i % 2 == 0:  # White move
                move_line = f"{i // 2 + 1}. {san_move}".ljust(40)
            else:  # Black move
                move_line += f"{san_move}"
                self.move_history_text.insert("end", move_line + "\n")
                move_line = ""

            if i == self.current_move_index:
                self.highlight_current_move_squares(move)

        # Handle unpaired white move
        if move_line:
            self.move_history_text.insert("end", move_line + "\n")

    def highlight_current_move_squares(self, move):
        """Highlight the from/to squares of the current move."""
        start_file = chess.square_file(move.from_square)
        start_rank = chess.square_rank(move.from_square)
        end_file = chess.square_file(move.to_square)
        end_rank = chess.square_rank(move.to_square)

        self.board_canvas.update_board(self._display_board.fen())
        self.board_canvas.highlight_square(start_file, start_rank, color="#ffff00")
        self.board_canvas.highlight_square(end_file, end_rank, color="#ffff00")

    def first_move(self):
        """Navigate to the first move."""
        if not self.moves:
            return
        self.is_current = False
        self.current_move_index = 0
        self.render_current_position()

    def prev_move(self):
        """Navigate to the previous move."""
        if self.current_move_index > 0:
            self.is_current = False
            self.current_move_index -= 1
            self.render_current_position()

    def next_move(self):
        """Navigate to the next move."""
        if self.current_move_index < len(self.moves) - 1:
            self.is_current = False
            self.current_move_index += 1
            self.render_current_position()

    def last_move(self):
        """Navigate to the last move."""
        if not self.moves:
            return
        self.current_move_index = len(self.moves) - 1
        self.is_current = True
        self.render_current_position()

    def render_current_position(self):
        """Render the board at the current navigation position."""
        self._display_board.reset()
        for move in self.moves[: self.current_move_index + 1]:
            self._display_board.push(move)
        self.board_canvas.update_board(self._display_board.fen())
        self.update_move_history()

    def reset_to_current(self):
        """
        Reset the display to show the current game position.

        FIX: Sets is_current = True (original had False, which was the opposite
        of what the method name implies).
        """
        self.is_current = True
        if self.moves:
            self.current_move_index = len(self.moves) - 1
        else:
            self.current_move_index = -1

        # Rebuild display board to current state
        self._display_board.reset()
        for move in self.moves:
            self._display_board.push(move)
        self.board_canvas.update_board(self._display_board.fen())

    def get_current_fen(self):
        """Get the FEN for the currently displayed position."""
        return self._display_board.fen()
