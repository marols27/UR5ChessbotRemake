import tkinter as tk
from tkinter import ttk, font as tkfont
import chess

class MoveHistory(ttk.Frame):
    def __init__(self, parent, board_canvas, game, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.board_canvas = board_canvas
        self.game = game  # Reference to the Game instance
        self.board = chess.Board()
        self.current_move_index = -1  # Start before the first move
        self.is_current = False  # Flag to indicate if showing the current board
        self.moves = []

        # Initialize styles
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Ubuntu', 20, 'bold'), foreground='white', background='#333333')
        self.style.configure('Nav.TButton', font=('Ubuntu', 14), foreground='white', background='#444444')
        self.style.map('Nav.TButton', background=[('active', '#555555')])

        # Label
        move_history_label = ttk.Label(self, text="Move History", style='Title.TLabel', padding=(10, 5))
        move_history_label.grid(row=0, column=0, columnspan=4, sticky="ew")

        # Text widget for displaying moves
        text_font = tkfont.Font(family='Ubuntu', size=16)
        self.move_history_text = tk.Text(self, height=15, width=40, bg="#666666", fg="white",
                                         font=text_font, borderwidth=0, padx=10, pady=10)
        self.move_history_text.grid(row=1, column=0, columnspan=4)
        self.move_history_text.tag_configure("current_move", foreground="red")

        # Navigation buttons
        back_button = ttk.Button(self, text="<<", style='Nav.TButton', command=self.first_move)
        back_button.grid(row=2, column=0, pady=10, padx=5)

        prev_button = ttk.Button(self, text="<", style='Nav.TButton', command=self.prev_move)
        prev_button.grid(row=2, column=1, pady=10, padx=5)

        next_button = ttk.Button(self, text=">", style='Nav.TButton', command=self.next_move)
        next_button.grid(row=2, column=2, pady=10, padx=5)

        forward_button = ttk.Button(self, text=">>", style='Nav.TButton', command=self.last_move)
        forward_button.grid(row=2, column=3, pady=10, padx=5)

    def load_moves(self):
        """Load moves from the gameInfo object in the Game class."""
        game_info = self.game.get_game_info()  # Get the current gameInfo from the Game instance
        self.board = game_info.board()  # Get the current board position from the gameInfo
        self.moves = list(game_info.mainline_moves())  # Extract all moves made in the game

        self.current_move_index = len(self.moves) - 1  # Start at the last move
        self.is_current = True  # Set the flag to indicate the current board state is being shown

        self.update_move_history()  # Display the moves

    def update_move_history(self):
        """Update the displayed move history text."""
        self.move_history_text.delete('1.0', tk.END)
        self.board.reset()  # Ensure the board starts from the initial position

        for i, move in enumerate(self.moves):
            san_move = self.board.san(move)
            self.board.push(move)
            prefix = f"{i//2 + 1}. " if i % 2 == 0 else " "
            move_text = prefix + san_move + " "

            if i == self.current_move_index:
                if i % 2 == 0:
                    self.move_history_text.insert(tk.END, move_text.split('.')[0] + ".")
                    self.move_history_text.insert(tk.END, move_text.split('.')[1], "current_move")
                else:
                    self.move_history_text.insert(tk.END, move_text, "current_move")

                self.highlight_current_move_squares(move)
            else:
                self.move_history_text.insert(tk.END, move_text)

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
        return self
