import customtkinter as ctk
import chess


class MoveHistory(ctk.CTkFrame):
    def __init__(self, parent, board_canvas, game, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.board_canvas = board_canvas
        self.game = game  # Reference to the Game instance
        self.board = chess.Board()
        self.current_move_index = 0  # Start before the first move
        self.is_current = False  # Flag to indicate if showing the current board
        self.moves = []

        # Label
        move_history_label = ctk.CTkLabel(
            self, text="Move History",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        move_history_label.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

        # Textbox for displaying moves
        self.move_history_text = ctk.CTkTextbox(
            self, height=300, width=400, font=ctk.CTkFont(size=16),
            fg_color="#666666", text_color="white", wrap="word", padx=10, pady=10
        )
        self.move_history_text.grid(row=1, column=0, columnspan=4, pady=10)
        #self.move_history_text.tag_configure("current_move", foreground="red")

        # Navigation buttons
        back_button = ctk.CTkButton(self, text="<<", command=self.first_move, width=60)
        back_button.grid(row=2, column=0, pady=10, padx=5)

        prev_button = ctk.CTkButton(self, text="<", command=self.prev_move, width=60)
        prev_button.grid(row=2, column=1, pady=10, padx=5)

        next_button = ctk.CTkButton(self, text=">", command=self.next_move, width=60)
        next_button.grid(row=2, column=2, pady=10, padx=5)

        forward_button = ctk.CTkButton(self, text=">>", command=self.last_move, width=60)
        forward_button.grid(row=2, column=3, pady=10, padx=5)

    def load_moves(self, board):
        """
        Load moves from the game's board object and update the move history.

        :param board: The current chess.Board instance with moves played so far.
        """
        self.board = board  # Store the board reference
        self.moves = list(board.move_stack)  # Get all moves from the board's move stack
        self.current_move_index = len(self.moves) - 1  # Set to the last move
        self.is_current = True  # Indicate the move history matches the current state

        # Update the move history display
        self.update_move_history()

    def update_move_history(self):
        """Update the displayed move history text."""
        self.move_history_text.delete('1.0', "end")
        self.board.reset()  # Ensure the board starts from the initial position

        for i, move in enumerate(self.moves):
            print(move)
            san_move = self.board.san(move)
            self.board.push(move)
            prefix = f"{i // 2 + 1}. " if i % 2 == 0 else " "
            move_text = prefix + san_move + " "

            if i == self.current_move_index:
                self.move_history_text.insert("end", move_text, "current_move")
                self.highlight_current_move_squares(move)
            else:
                self.move_history_text.insert("end", move_text)

    def highlight_current_move_squares(self, move):
        """Highlight the squares involved in the current move."""
        start_square = move.from_square
        end_square = move.to_square
        start_file, start_rank = chess.square_file(start_square), chess.square_rank(start_square)
        end_file, end_rank = chess.square_file(end_square), chess.square_rank(end_square)

        # Redraw the board before highlighting
        self.board_canvas.update_board(self.board.fen())
        self.board_canvas.highlight_square(start_file, start_rank, color="#ffff00")
        self.board_canvas.highlight_square(end_file, end_rank, color="#ffff00")

    def first_move(self):
        """Go to the first move."""
        self.is_current = False
        self.current_move_index = 0
        self.render_current_position()

    def prev_move(self):
        """Go to the previous move."""
        self.is_current = False
        if self.current_move_index > 0:
            self.current_move_index -= 1
        self.render_current_position()

    def next_move(self):
        """Go to the next move."""
        if self.current_move_index < len(self.moves) - 1:
            self.is_current = False
            self.current_move_index += 1
            self.render_current_position()

    def last_move(self):
        """Go to the last move."""
        self.is_current = False
        self.current_move_index = len(self.moves) - 1
        self.render_current_position()

    def render_current_position(self):
        """Render the board position for the current move."""
        self.board.reset()  # Reset to initial position
        for move in self.moves[:self.current_move_index + 1]:
            self.board.push(move)
        fen = self.board.fen()
        self.board_canvas.update_board(fen)
        self.update_move_history()

    def reset_to_current(self):
        """Reset the board to the current game position."""
        self.is_current = False
        self.current_move_index = -1
        self.board.reset()
        self.board_canvas.update_board(self.board.fen())
        self.update_move_history()

    def get_current_fen(self):
        """Get the FEN for the current game state."""
        return self.board.fen()
