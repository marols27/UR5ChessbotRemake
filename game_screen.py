"""
Game screen: Main chess game UI.

Fixes over original:
- Hardware initialization wrapped in try/except with error handling
- Robot/engine operations run in background thread to avoid UI freeze
- Fixed confirm_move() infinite recursion
- Fixed tautological FEN comparison for white player (was always True)
- Proper engine cleanup on navigation away
- Simulation mode support throughout
"""

import logging
import threading

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from components.chessboard import Chessboard
from components.move_history import MoveHistory
from DGTBoard import DGTBoard
from UR5Robot import UR5Robot
from Board import Board
from Game import Game
from simulation import SIMULATION_MODE
import Settings
import chess
import chess.engine
import chess.pgn
import navigation

logger = logging.getLogger(__name__)


def show_game_screen(root, color, difficulty):
    """Show the game screen with the selected color and difficulty."""

    for widget in root.winfo_children():
        widget.destroy()

    # ------------------------------------------------------------------
    # Initialize hardware / engine with error handling
    # ------------------------------------------------------------------
    try:
        robot = UR5Robot(
            Settings.TRAVEL_HEIGHT,
            Settings.HOME,
            Settings.CONNECTION_IP,
            Settings.ACCELERATION,
            Settings.SPEED,
            Settings.GRIPPER_SPEED,
            Settings.GRIPPER_FORCE,
        )
    except Exception as e:
        logger.error(f"Failed to initialize robot: {e}")
        if not SIMULATION_MODE:
            CTkMessagebox(
                title="Robot Error",
                message=f"Could not connect to robot: {e}\nRunning in simulation mode.",
                icon="warning",
            )
        robot = UR5Robot(
            Settings.TRAVEL_HEIGHT,
            Settings.HOME,
            Settings.CONNECTION_IP,
            Settings.ACCELERATION,
            Settings.SPEED,
            Settings.GRIPPER_SPEED,
            Settings.GRIPPER_FORCE,
        )

    dgt = DGTBoard(Settings.PORT, simulation=SIMULATION_MODE)

    board = Board(
        Settings.START_FEN,
        Settings.BOARD_FEATURE,
        Settings.BOARD_SIZE,
        Settings.SQUARE_SIZE,
    )

    # Initialize Stockfish engine
    engine = None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(Settings.STOCKFISH_PATH)
        skill_levels = {"easy": 1, "medium": 5, "hard": 10}
        level = skill_levels.get(difficulty, 5)
        engine.configure({"Skill Level": level})
    except Exception as e:
        logger.error(f"Failed to start Stockfish engine: {e}")
        CTkMessagebox(
            title="Engine Error",
            message=f"Could not start Stockfish: {e}\nPlease check STOCKFISH_PATH in Settings.",
            icon="cancel",
        )
        navigation.navigate_to_home(root)
        return

    # Set FEN on DGT board in simulation mode
    dgt.sim_set_fen(Settings.START_FEN)

    gameInfo = chess.pgn.Game()
    capturePos = Settings.CAPTURE_POSE
    timeout = Settings.TIMEOUT
    game = Game(
        robot,
        dgt,
        board,
        engine,
        gameInfo,
        capturePos,
        timeout,
        skill_levels.get(difficulty, 5),
        color == "white",
    )

    # ------------------------------------------------------------------
    # UI Layout
    # ------------------------------------------------------------------
    ubuntu_font_large = ctk.CTkFont(size=48, weight="bold")

    BUTTON_HEIGHT = 150
    BUTTON_CORNER_RADIUS = 40
    BORDER_COLOR = "white"
    BORDER_WIDTH = 10

    game_frame = ctk.CTkFrame(root)
    game_frame.pack(fill="both", expand=True, padx=20, pady=20)

    flipped = color == "black"

    # ------------------------------------------------------------------
    # Click-to-move callback for simulation mode
    # ------------------------------------------------------------------
    def on_human_move(uci: str):
        """Called by the chessboard when the user clicks a move in sim mode.

        Injects the move into the DGT board's preview so that the next
        ``confirmMove()`` call will detect it. Also updates the visual
        board to show the pending move.
        """
        if _busy.is_set():
            return

        # Validate against the game's internal board
        legal_ucis = [m.uci() for m in game.board.board.legal_moves]
        if uci not in legal_ucis:
            logger.debug(
                f"Clicked move {uci} is not legal (legal: {legal_ucis[:5]}...)"
            )
            # Try without promotion suffix or with queen promotion
            if len(uci) == 4 and uci + "q" in legal_ucis:
                uci = uci + "q"
            else:
                return

        ok = dgt.sim_inject_human_move(uci)
        if ok:
            # Show the pending move visually on the canvas
            preview_fen = dgt.getCurentBoardFen()
            board_canvas.update_board(preview_fen)
            # Highlight from/to squares
            from_file = ord(uci[0]) - ord("a")
            from_rank = int(uci[1]) - 1
            to_file = ord(uci[2]) - ord("a")
            to_rank = int(uci[3]) - 1
            board_canvas.highlight_square(from_file, from_rank, color="#aaf0aa")
            board_canvas.highlight_square(to_file, to_rank, color="#aaf0aa")
            logger.info(f"Sim: human move {uci} injected, press Confirm Move")

    move_cb = on_human_move if SIMULATION_MODE else None

    # Chessboard
    board_frame = ctk.CTkFrame(game_frame)
    board_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n", rowspan=3)

    square_size = 100
    board_canvas = Chessboard(
        board_frame, square_size=square_size, flipped=flipped, move_callback=move_cb
    )
    board_canvas.pack()

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board_canvas.update_board(starting_fen)

    # Move history
    history_frame = ctk.CTkFrame(game_frame)
    history_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")

    # Action buttons
    action_frame = ctk.CTkFrame(game_frame)
    action_frame.grid(row=1, column=1, padx=20, pady=10, sticky="e")

    # State tracking for busy operations
    _busy = threading.Event()
    _active = (
        True  # Set to False when navigating away; prevents stale after() callbacks
    )
    _after_ids: list[str] = []  # Track after() IDs for cleanup

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
        command=lambda: confirm_move(),
    )
    confirm_move_button.pack(side="left", padx=10)

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
        command=lambda: resign_game(),
    )
    resign_button.pack()

    move_history = MoveHistory(history_frame, board_canvas, game)
    move_history.grid(row=0, column=0, padx=20, pady=20, sticky="n")

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------

    def return_to_home():
        nonlocal _active
        _active = False
        # Cancel pending after() callbacks
        for aid in _after_ids:
            try:
                root.after_cancel(aid)
            except Exception:
                pass
        _after_ids.clear()
        if engine:
            try:
                engine.quit()
            except Exception:
                pass
        robot.close()
        dgt.close()
        navigation.navigate_to_home(root)

    def message_callback(header, text):
        """Thread-safe message callback — schedules UI update on main thread."""
        if not _active:
            return

        def _show():
            if not _active:
                return
            logger.info(f"Message: {header} - {text}")
            if header in ["You won", "You lost", "It's a draw"]:
                msg = text + "\nDo you want to return to the home menu?"
                msg_box = CTkMessagebox(
                    title=header,
                    message=msg,
                    icon="question",
                    option_1="Yes",
                    option_2="No",
                )
                response = msg_box.get()
                if response == "Yes":
                    return_to_home()
            else:
                CTkMessagebox(title=header, message=text, icon="info", option_1="OK")

        root.after(0, _show)

    def _update_ui_after_move():
        """Update UI elements after a move (called on main thread)."""
        if not _active:
            return
        board_canvas.update_board(game.board.board.fen())
        move_history.load_moves(game.board.board)

    def confirm_move():
        """
        Handle the confirm move button press.
        Runs the game logic in a background thread to avoid freezing the UI.

        FIX: Removed infinite recursion from original.
        """
        if _busy.is_set():
            logger.debug("Confirm move ignored: already processing")
            return

        # In simulation mode, check that the user has clicked a move first
        if SIMULATION_MODE and dgt._sim_preview is None:
            CTkMessagebox(
                title="No Move",
                message="Click on a piece and then a destination square to make your move.",
                icon="info",
                option_1="OK",
            )
            return

        # Reset move history to show current position
        move_history.reset_to_current()

        def _worker():
            _busy.set()
            try:
                game.confirmMove(message_callback)
                # Update UI on main thread
                root.after(0, _update_ui_after_move)
            except Exception as e:
                logger.error(f"Error during confirmMove: {e}")
                root.after(
                    0,
                    lambda: CTkMessagebox(
                        title="Error",
                        message=f"An error occurred: {e}",
                        icon="cancel",
                    ),
                )
            finally:
                _busy.clear()

        threading.Thread(target=_worker, daemon=True).start()

    def resign_game():
        msg_box = CTkMessagebox(
            title="Resign",
            message="Are you sure you want to resign the game?",
            icon="question",
            option_1="Yes",
            option_2="No",
        )
        if msg_box.get() == "Yes":
            return_to_home()

    def play_first_move():
        """
        Handle the first move of the game.
        If human plays black, the robot moves first.

        FIX: Corrected tautological comparison (was correct_start_fen == correct_start_fen).
        """
        if not _active:
            return
        correct_start_fen = game.board.board.fen().split(" ")[0]

        sim_hint = (
            "\n\nClick on a piece, then click a destination square to move."
            if SIMULATION_MODE
            else ""
        )

        if color == "black":
            current_dgt_fen = game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                msg = "You are playing black. The engine will make the first move. Press OK when ready."
                CTkMessagebox(
                    title="Get Ready",
                    message=msg,
                    icon="info",
                    option_1="OK",
                )

                def _robot_first_move():
                    _busy.set()
                    try:
                        game.playRobotMove(message_callback)
                        root.after(0, _update_ui_after_move)
                    except Exception as e:
                        logger.error(f"Error during robot first move: {e}")
                        root.after(
                            0,
                            lambda: CTkMessagebox(
                                title="Error",
                                message=f"Engine move failed: {e}",
                                icon="cancel",
                            ),
                        )
                    finally:
                        _busy.clear()

                threading.Thread(target=_robot_first_move, daemon=True).start()
            else:
                CTkMessagebox(
                    title="Board Setup",
                    message="Please set the pieces in their starting positions and press OK.",
                    icon="info",
                    option_1="OK",
                )
                _after_ids.append(root.after(500, play_first_move))
        else:
            # FIX: actually compare DGT board FEN against expected start FEN
            current_dgt_fen = game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                msg = "You are playing white. Make your move!" + sim_hint
                CTkMessagebox(
                    title="Get Ready",
                    message=msg,
                    icon="info",
                    option_1="OK",
                )
            else:
                CTkMessagebox(
                    title="Board Setup",
                    message="Please set up the board correctly and press OK.",
                    icon="info",
                    option_1="OK",
                )
                _after_ids.append(root.after(500, play_first_move))

    # Start the game
    _after_ids.append(root.after(100, play_first_move))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Chess Game")
    root.geometry("1024x768")
    show_game_screen(root, "black", "medium")
    root.mainloop()
