import time
import tkinter as tk
from tkinter import ttk, messagebox
from components.chessboard import Chessboard  # Import the Chessboard component
from components.move_history import MoveHistory  # Import the MoveHistory component
from DGTBoard import DGTBoard
from UR5Robot import UR5Robot
from Board import Board
from Game import Game
import Settings
import chess
import chess.engine
import chess.pgn
from playsound import playsound

def show_game_screen(root, color, difficulty):
    '''Show the game screen with the selected color and difficulty.'''

    for widget in root.winfo_children():
        widget.destroy()

    # Create the game
    robot = UR5Robot(Settings.TRAVEL_HEIGHT, Settings.HOME, Settings.CONNECTION_IP, Settings.ACCELERATION, Settings.SPEED, Settings.GRIPPER_SPEED, Settings.GRIPPER_FORCE)
    dgt = DGTBoard(Settings.PORT)
    board = Board(Settings.START_FEN, Settings.BOARD_FEATURE, Settings.BOARD_SIZE, Settings.SQUARE_SIZE)
    engine = chess.engine.SimpleEngine.popen_uci(Settings.STOCKFISH_PATH)
    if difficulty == "easy":
        engine.configure({"Skill Level": 1})
    elif difficulty == "medium":
        engine.configure({"Skill Level": 5})
    elif difficulty == "hard":
        engine.configure({"Skill Level": 10})
    gameInfo = chess.pgn.Game()
    capturePos = Settings.CAPTURE_POSE
    timeout = Settings.TIMEOUT
    game = Game(robot, dgt, board, engine, gameInfo, capturePos, timeout, 10, color == "white")

    # Define the Ubuntu font
    ubuntu_font = ("Ubuntu", 24)
    ubuntu_font_bold = ("Ubuntu", 24, "bold")
    ubuntu_font_large = ("Ubuntu", 32, "bold")

    # Set up style configurations
    style = ttk.Style()
    style.theme_use("clam")

    # Define styles for buttons and labels
    style.configure("TFrame", background="#1a237e")
    style.configure("TLabel", font=ubuntu_font, background="#1a237e", foreground="white")
    style.configure("TButton", font=ubuntu_font_bold, padding=10)
    style.configure("Confirm.TButton", font = ubuntu_font_large, background="#28a745", foreground="white")
    style.map("Confirm.TButton",
              background=[("active", "#218838")],
              foreground=[("active", "white")])
    style.configure("Resign.TButton", background="#dc3545", font=ubuntu_font_large, foreground="white")
    style.map("Resign.TButton",
              background=[("active", "#c82333")],
              foreground=[("active", "white")])

    # Create the main game frame
    game_frame = ttk.Frame(root, style="TFrame")
    game_frame.pack(fill="both", expand=True)

    # Determine whether to flip the board based on the selected color
    flipped = (color == "black")

    # Chessboard frame
    board_frame = ttk.Frame(game_frame, style="TFrame")
    board_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n", rowspan=3)

    # Define desired square size
    square_size = 100

    # Create the Chessboard component with the specified square size
    board_canvas = Chessboard(board_frame, square_size=square_size, flipped=flipped)
    board_canvas.pack()

    # Update the Chessboard with the starting position
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board_canvas.update_board(starting_fen)

    # Move history frame
    history_frame = ttk.Frame(game_frame, style="TFrame")
    history_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")

    # Action buttons frame
    action_frame = ttk.Frame(game_frame, style="TFrame")
    action_frame.grid(row=1, column=1, padx=20, pady=10, sticky="e")

    # Confirm Move Button
    confirm_move_button = ttk.Button(
        action_frame,
        text="CONFIRM MOVE",
        style="Confirm.TButton",
        command=lambda: confirm_move()
    )
    confirm_move_button.pack(side="left", padx=10)

    # Resign Button
    resign_button = ttk.Button(
        action_frame,
        text="RESIGN",
        style="Resign.TButton",
        command=lambda: resign_game()
    )
    resign_button.pack()

    # Create the MoveHistory component
    move_history = MoveHistory(history_frame, board_canvas, game)
    move_history.grid(row=0, column=0, padx=20, pady=20, sticky="n")

    def return_to_home():
        game_frame.destroy()
        from home_screen import show_home_screen
        show_home_screen(root)

    def message_callback(header, text):
        print(header, text)
        if header == "You won" or header == "You lost" or header == "It's a draw":
            text = text + "\nDo you want to return to home menu?"
            mbox = None
            if header == "You won":
                mbox = messagebox.askyesno(header, text)
                if mbox:
                    return_to_home()
            elif header == "You lost":
                mbox = messagebox.askyesno(header, text)
                if mbox:
                    return_to_home()
            elif header == "It's a draw":
                mbox = messagebox.askyesno(header, text)
                if mbox:
                    return_to_home()
        else:
            messagebox.showinfo(header, text)
            move_history.reset_to_current() 

    def confirm_move():
        move_history.reset_to_current()
        if not move_history.is_current:
            board_canvas.update_board(game.dgtBoard.getCurentBoardFen())
            game.confirmMove(message_callback)
            board_canvas.update_board(game.board.board.fen())
        else:
            move_history.reset_to_current()
            confirm_move()

    # Example function to resign the game
    def resign_game():
        messagebox.showinfo("Resign", "You have resigned the game.")
        game_frame.destroy()

        # Import inside the function to avoid circular import
        from home_screen import show_home_screen
        show_home_screen(root)

    def play_first_move():
        correct_start_fen = game.board.board.fen().split(" ")[0]
        if color == "black":
            current_dgt_fen = game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                game.playRobotMove()
                board_canvas.update_board(game.board.board.fen())
            else:
                messagebox.showinfo("The board is set up wrong", "Please set up the board correctly and press the confirm move button.")
                play_first_move()
        else:
            if correct_start_fen == correct_start_fen:
                messagebox.showinfo("Get ready", "You are playing white. Please make your move.")
            else:
                messagebox.showinfo("The board is set up wrong", "Please set up the board correctly and press the confirm move button.")
                play_first_move()
        

    play_first_move()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess Game")
    root.geometry("1024x768")
    show_game_screen(root, tk.Frame(root), "black", "medium")
    root.mainloop()
