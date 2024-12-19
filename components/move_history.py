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
            font=ctk.CTkFont(size=32, weight="bold")
        )
        move_history_label.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

        # Textbox for displaying moves
        self.move_history_text = ctk.CTkTextbox(
            self, height=300, width=400, font=ctk.CTkFont(size=24),
            fg_color="#666666", text_color="white", wrap="word", padx=10, pady=10
        )
        self.move_history_text.grid(row=1, column=0, columnspan=4, pady=10)
        
        # Navigation buttons
        ARROW_SIZE = 30

        back_button = ctk.CTkButton(self, text="↢↢", command=self.first_move, width=60, font=ctk.CTkFont(size=ARROW_SIZE))
        back_button.grid(row=2, column=0, pady=10, padx=5)

        prev_button = ctk.CTkButton(self, text="↢", command=self.prev_move, width=60, font=ctk.CTkFont(size=ARROW_SIZE))
        prev_button.grid(row=2, column=1, pady=10, padx=5)

        next_button = ctk.CTkButton(self, text="↣", command=self.next_move, width=60, font=ctk.CTkFont(size=ARROW_SIZE))
        next_button.grid(row=2, column=2, pady=10, padx=5)

        forward_button = ctk.CTkButton(self, text="↣↣", command=self.last_move, width=60, font=ctk.CTkFont(size=ARROW_SIZE))
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
        """Update the displayed move history text with moves aligned in pairs."""
        self.move_history_text.delete('1.0', "end")
        self.board.reset()  # Ensure the board starts from the initial position

        move_line = ""  # Temporary storage for each line of moves
        for i, move in enumerate(self.moves):
            san_move = self.board.san(move)
            self.board.push(move)
            
            # Formatting the move pair with spacing
            if i % 2 == 0:  # White move
                move_line = f"{i // 2 + 1}. {san_move}".ljust(40)  # Left-align the white move
            else:  # Black move
                move_line += f"{san_move}"  # Append the black move to the line
                self.move_history_text.insert("end", move_line + "\n")  # Insert line and line-shift
                move_line = ""  # Reset for the next line
            
            # Highlight current move if applicable
            if i == self.current_move_index:
                self.highlight_current_move_squares(move)

        # If the last move was a single white move (no black move yet)
        if move_line:
            self.move_history_text.insert("end", move_line + "\n")


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
