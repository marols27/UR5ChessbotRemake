"""
Game screen: Main chess game UI.

Refactored:
- Extracted _GameController class from closures for cleaner state management
- StatusBar with live connection status
- GameInfoPanel with turn indicator and inline status messages
- 5 CTkMessagebox calls replaced with inline status panel messages
- 4 CTkMessagebox calls kept for critical actions (robot/engine error, game end, resign)
- Last-move highlighting after robot plays
- Modernized buttons via theme factories
"""

import logging
import threading

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from .components.chessboard import Chessboard
from .components.move_history import MoveHistory
from .components.status_bar import StatusBar
from .components.game_info import GameInfoPanel
from robot.DGTBoard import DGTBoard
from robot.UR5Robot import UR5Robot
from robot.Board import Board
from robot.Game import Game
from robot.simulation import SIMULATION_MODE
from .theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_SUBTLE,
    primary_button, danger_button, card_frame,
    BOARD_HIGHLIGHT,
)
import robot.Settings as Settings
import chess
import chess.engine
import chess.pgn
from . import navigation

logger = logging.getLogger(__name__)


class _GameController:
    """Manages game state and operations, extracted from nested closures."""

    def __init__(self, root, game, dgt, robot, engine, board_canvas,
                 move_history, info_panel, status_bar, color):
        self.root = root
        self.game = game
        self.dgt = dgt
        self.robot = robot
        self.engine = engine
        self.board_canvas = board_canvas
        self.move_history = move_history
        self.info_panel = info_panel
        self.status_bar = status_bar
        self.color = color

        self._busy = threading.Event()
        self._active = True
        self._after_ids: list[str] = []

    def cleanup(self):
        """Clean up resources when navigating away."""
        self._active = False
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()
        if self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass
        self.robot.close()
        self.dgt.close()

    def return_to_home(self):
        self.cleanup()
        navigation.navigate_to_home(self.root)

    def message_callback(self, header, text):
        """Thread-safe message callback — schedules UI update on main thread."""
        if not self._active:
            return

        def _show():
            if not self._active:
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
                if msg_box.get() == "Yes":
                    self.return_to_home()
            elif header == "Promotion":
                # Promotion placement info -> inline status
                self.info_panel.set_status(text, "info")
            else:
                self.info_panel.set_status(f"{header}: {text}", "info")

        try:
            self.root.after(0, _show)
        except RuntimeError:
            pass

    def _update_ui_after_move(self):
        """Update UI elements after a move (called on main thread)."""
        if not self._active:
            return
        fen = self.game.board.board.fen()
        self.board_canvas.update_board(fen)
        self.move_history.load_moves(self.game.board.board)

        # Highlight last move
        moves = list(self.game.board.board.move_stack)
        if moves:
            last = moves[-1]
            uci = last.uci()
            self.board_canvas.highlight_last_move(uci)
            # Update last move display in info panel
            try:
                display_board = chess.Board()
                for m in moves[:-1]:
                    display_board.push(m)
                san = display_board.san(last)
                self.info_panel.set_last_move(san)
            except Exception:
                self.info_panel.set_last_move(uci)

        # Update turn indicator
        is_human_turn = self._is_human_turn()
        self.info_panel.set_turn(is_human_turn)
        if is_human_turn:
            hint = " Click a piece to move." if SIMULATION_MODE else ""
            self.status_bar.set_context("Your turn" + hint)
        else:
            self.status_bar.set_context("Robot thinking...")

    def _is_human_turn(self):
        """Check if it's the human player's turn."""
        board = self.game.board.board
        if self.color == "white":
            return board.turn == chess.WHITE
        else:
            return board.turn == chess.BLACK

    def confirm_move(self):
        """Handle the confirm move button press."""
        if self._busy.is_set():
            logger.debug("Confirm move ignored: already processing")
            return

        if SIMULATION_MODE and self.dgt._sim_preview is None:
            self.info_panel.set_status(
                "Click on a piece and then a destination square to make your move.",
                "info",
            )
            return

        self.move_history.reset_to_current()
        self.info_panel.set_turn(False)
        self.info_panel.set_status("Processing move...", "info")
        self.status_bar.set_context("Processing...")

        def _worker():
            self._busy.set()
            try:
                self.game.confirmMove(self.message_callback)
                if self._active:
                    try:
                        self.root.after(0, self._update_ui_after_move)
                    except RuntimeError:
                        pass
            except Exception as e:
                logger.error(f"Error during confirmMove: {e}")
                if self._active:
                    try:
                        self.root.after(
                            0,
                            lambda: self.info_panel.set_status(
                                f"Error: {e}", "error"
                            ),
                        )
                    except RuntimeError:
                        pass
            finally:
                self._busy.clear()

        threading.Thread(target=_worker, daemon=True).start()

    def resign_game(self):
        msg_box = CTkMessagebox(
            title="Resign",
            message="Are you sure you want to resign the game?",
            icon="question",
            option_1="Yes",
            option_2="No",
        )
        if msg_box.get() == "Yes":
            self.return_to_home()

    def play_first_move(self):
        """Handle the first move of the game."""
        if not self._active:
            return
        correct_start_fen = self.game.board.board.fen().split(" ")[0]

        if self.color == "black":
            current_dgt_fen = self.game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                self.info_panel.set_status(
                    "You are playing black. The engine will make the first move.",
                    "info",
                )
                self.info_panel.set_turn(False)
                self.status_bar.set_context("Robot's first move...")

                def _robot_first_move():
                    self._busy.set()
                    try:
                        self.game.playRobotMove(self.message_callback)
                        if self._active:
                            try:
                                self.root.after(0, self._update_ui_after_move)
                            except RuntimeError:
                                pass
                    except Exception as e:
                        logger.error(f"Error during robot first move: {e}")
                        if self._active:
                            try:
                                self.root.after(
                                    0,
                                    lambda: CTkMessagebox(
                                        title="Error",
                                        message=f"Engine move failed: {e}",
                                        icon="cancel",
                                    ),
                                )
                            except RuntimeError:
                                pass
                    finally:
                        self._busy.clear()

                threading.Thread(target=_robot_first_move, daemon=True).start()
            else:
                self.info_panel.set_status(
                    "Please set the pieces in their starting positions.", "info"
                )
                self._after_ids.append(self.root.after(500, self.play_first_move))
        else:
            current_dgt_fen = self.game.dgtBoard.getCurentBoardFen()
            if current_dgt_fen == correct_start_fen:
                sim_hint = (
                    " Click a piece to move." if SIMULATION_MODE else ""
                )
                self.info_panel.set_status(
                    "You are playing white. Make your move!" + sim_hint,
                    "info",
                )
                self.info_panel.set_turn(True)
                self.status_bar.set_context("Your turn")
            else:
                self.info_panel.set_status(
                    "Please set up the board correctly.", "info"
                )
                self._after_ids.append(self.root.after(500, self.play_first_move))

    def on_human_move(self, uci: str):
        """Called by the chessboard when the user clicks a move in sim mode."""
        if self._busy.is_set():
            return

        legal_ucis = [m.uci() for m in self.game.board.board.legal_moves]
        if uci not in legal_ucis:
            if len(uci) == 4 and uci + "q" in legal_ucis:
                uci = uci + "q"
            else:
                return

        ok = self.dgt.sim_inject_human_move(uci)
        if ok:
            preview_fen = self.dgt.getCurentBoardFen()
            self.board_canvas.update_board(preview_fen)
            self.board_canvas.highlight_last_move(uci)
            self.info_panel.set_status("Move ready. Press Confirm Move.", "info")
            logger.info(f"Sim: human move {uci} injected, press Confirm Move")


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
    container = ctk.CTkFrame(root, fg_color=BG_PRIMARY, corner_radius=0)
    container.pack(fill="both", expand=True)

    # We create a placeholder for the controller's return_to_home
    # since we need status_bar first
    ctrl_ref = [None]

    status_bar = StatusBar(
        container,
        back_command=lambda: ctrl_ref[0].return_to_home() if ctrl_ref[0] else None,
        show_connections=True,
    )
    status_bar.pack(fill="x")
    status_bar.set_connection("engine", "connected")

    # Main content frame
    game_frame = ctk.CTkFrame(container, fg_color="transparent")
    game_frame.pack(fill="both", expand=True, padx=20, pady=10)
    game_frame.grid_columnconfigure(1, weight=1)
    game_frame.grid_rowconfigure(0, weight=1)

    flipped = color == "black"

    # Chessboard (left)
    board_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
    board_frame.grid(row=0, column=0, padx=(0, 16), pady=0, sticky="n")

    square_size = 100
    board_canvas = Chessboard(
        board_frame, square_size=square_size, flipped=flipped, move_callback=None
    )
    board_canvas.pack()

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board_canvas.update_board(starting_fen)

    # Right panel: info + history + buttons
    right_panel = ctk.CTkFrame(game_frame, fg_color="transparent")
    right_panel.grid(row=0, column=1, sticky="nsew", pady=0)
    right_panel.grid_rowconfigure(1, weight=1)

    # Game info panel
    info_panel = GameInfoPanel(right_panel, width=320)
    info_panel.grid(row=0, column=0, sticky="new", pady=(0, 10))

    # Move history
    history_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    history_frame.grid(row=1, column=0, sticky="new", pady=(0, 10))

    move_history = MoveHistory(history_frame, board_canvas, game)
    move_history.pack()

    # Create the controller
    ctrl = _GameController(
        root, game, dgt, robot, engine,
        board_canvas, move_history, info_panel, status_bar, color,
    )
    ctrl_ref[0] = ctrl

    # Set up click-to-move callback for simulation
    if SIMULATION_MODE:
        board_canvas.set_move_callback(ctrl.on_human_move)

    # Action buttons (stacked vertically)
    action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    action_frame.grid(row=2, column=0, sticky="sew", pady=(0, 0))

    confirm_btn = primary_button(
        action_frame, "Confirm Move", ctrl.confirm_move
    )
    confirm_btn.pack(fill="x", pady=(0, 8))

    resign_btn = danger_button(
        action_frame, "Resign", ctrl.resign_game
    )
    resign_btn.pack(fill="x")

    # Start the game
    ctrl._after_ids.append(root.after(100, ctrl.play_first_move))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Chess Game")
    root.geometry("1024x768")
    show_game_screen(root, "black", "medium")
    root.mainloop()
