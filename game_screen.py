import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
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
from tkinter import messagebox
import navigation


def show_game_screen(root, color, difficulty):
    """Show the game screen with the selected color and difficulty."""

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

    # Define fonts
    ubuntu_font = ctk.CTkFont(size=24, weight="normal")
    ubuntu_font_bold = ctk.CTkFont(size=24, weight="bold")
    ubuntu_font_large = ctk.CTkFont(size=48, weight="bold")

    #Buttonconfigurations
    BUTTON_HEIGHT = 150
    BUTTON_CORNER_RADIUS = 40
    BORDER_COLOR = "white"
    BORDER_WIDTH = 10

    # Create the main game frame
    game_frame = ctk.CTkFrame(root)
    game_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Determine whether to flip the board based on the selected color
    flipped = (color == "black")

    # Chessboard frame
    board_frame = ctk.CTkFrame(game_frame)
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
    history_frame = ctk.CTkFrame(game_frame)
    history_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")

    # Action buttons frame
    action_frame = ctk.CTkFrame(game_frame)
    action_frame.grid(row=1, column=1, padx=20, pady=10, sticky="e")

    # Confirm Move Button
    confirm_move_button = ctk.CTkButton(
        action_frame,
        text="CONFIRM MOVE",
        font=ubuntu_font_large,
        fg_color="#28a745",
        hover=False,
        text_color="white",
        border_color=BORDER_COLOR,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT,
        corner_radius=BUTTON_CORNER_RADIUS,
        command=lambda: confirm_move()
    )
    confirm_move_button.pack(side="left", padx=10)

    # Resign Button
    resign_button = ctk.CTkButton(
        action_frame,
        text="RESIGN",
        font=ubuntu_font_large,
        fg_color="#dc3545",
        hover=False,
        border_color=BORDER_COLOR,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT,
        corner_radius=BUTTON_CORNER_RADIUS,
        text_color="white",
        command=lambda: resign_game()
    )
    resign_button.pack()

    # Create the MoveHistory component
    move_history = MoveHistory(history_frame, board_canvas, game)
    move_history.grid(row=0, column=0, padx=20, pady=20, sticky="n")

    def return_to_home():
        engine.quit()
        navigation.navigate_to_home(root)

    def message_callback(header, text):
        print(header, text)
        if header in ["You won", "You lost", "It's a draw"]:
            text += "\nDo you want to return to the home menu?"
            msg_box = CTkMessagebox(title=header, message=text, icon="question", option_1="Yes", option_2="No")
            response = msg_box.get()
            if response == "Yes":
                return_to_home()
        else:
            CTkMessagebox(title=header, message=text, icon="info", option_1="OK")
            move_history.reset_to_current()

    def confirm_move():
        move_history.reset_to_current()
        if not move_history.is_current:
            board_canvas.update_board(game.dgtBoard.getCurentBoardFen())
            game.confirmMove(message_callback)
            move_history.load_moves(game.board.board)
            print(game.gameInfo.mainline_moves)
        else:
            move_history.reset_to_current()
            confirm_move()

    def resign_game():
        resign_message = messagebox.askquestion("You have asked to resign", "Are you sure you want to resign the game?")
        if resign_message == "yes":
            return_to_home()

    def play_first_move():
        correct_start_fen = game.board.board.fen().split(" ")[0]
        if color == "black":
            current_dgt_fen = game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                messagebox.showinfo("Get Ready", "You are playing black so the robot wil start the game, press OK when ready")
                game.playRobotMove()
                board_canvas.update_board(game.board.board.fen())
                move_history.load_moves(game.board.board)
            else:
                messagebox.showinfo("Board is set up wrong", "Please set the pieces in their starting positions and press OK")
                play_first_move()
        else:
            if correct_start_fen == correct_start_fen:
                messagebox.showinfo("Get Ready", "You are playing white. Please make your move.")
            else:
                messagebox.showinfo("The board is set up wrong", "Please set up the board correctly and press the confirm move button.")
                play_first_move()

    play_first_move()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Dark mode
    ctk.set_default_color_theme("blue")  # Default theme
    root = ctk.CTk()
    root.title("Chess Game")
    root.geometry("1024x768")
    show_game_screen(root, "black", "medium")
    root.mainloop()
