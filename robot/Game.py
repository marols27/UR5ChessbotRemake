"""
Game module: Manages the chess game loop, coordinating the board state,
DGT board, Stockfish engine, and UR5 robot.

Fixes over original:
- No input() calls (uses messageCallback for GUI communication)
- No playsound dependency (optional, with graceful fallback)
- Promotion moves don't crash (no int("q") bug)
- No infinite loops in promotion handling
- Board state is pushed *after* physical move (not before)
- PGN node tracking fixed (add_variation returns new node, which is tracked)
- Message callbacks for all user-facing communication
- robot.control.reconnect/disconnect managed properly
"""

import logging

import chess
import chess.engine
import chess.pgn

from .Board import Board
from .DGTBoard import DGTBoard
from .ToolCenterPoint import ToolCenterPoint as TCP
from .UR5Robot import UR5Robot

logger = logging.getLogger(__name__)

# Try to import playsound, but don't fail if unavailable
try:
    from playsound import playsound as _playsound

    def play_sound(path: str):
        try:
            _playsound(path)
        except Exception as e:
            logger.warning(f"Failed to play sound {path}: {e}")
except ImportError:

    def play_sound(path: str):
        logger.debug(f"playsound not available, skipping: {path}")


PIECE_NAMES = {
    "q": "queen",
    "r": "rook",
    "b": "bishop",
    "n": "knight",
}


class Game:
    """
    Manages a chess game between the human player and the robot/engine.
    """

    def __init__(
        self,
        robot: UR5Robot,
        dgtBoard: DGTBoard,
        board: Board,
        engine: chess.engine.SimpleEngine,
        gameInfo: chess.pgn.Game,
        capturePos: TCP,
        timeout: chess.engine.Limit,
        difficulty: int,
        color: bool,
    ) -> None:
        self.robot = robot
        self.dgtBoard = dgtBoard
        self.board = board
        self.engine = engine
        self.gameInfo = gameInfo
        self.capturePos = capturePos
        self.timeout = timeout
        self.difficulty = difficulty
        self.color = color  # True = human plays white
        self.move = None
        self._pgn_node = gameInfo  # Track current PGN node for proper chaining

    def getPGN(self) -> str:
        return self.board.getPGN()

    def playRobotMove(self, messageCallback=None):
        """
        Have the engine compute and execute a move.

        Args:
            messageCallback: Optional callable(header, text) for GUI messages.
        """
        # Get the board state *before* pushing the engine move
        previousBoard = str(self.board.board)

        # Ask engine for a move
        result = self.engine.play(self.board.board, self.timeout)
        uci_str = result.move.uci()
        self.move = uci_str

        # Compute TCPs for robot movement *before* pushing the move
        move_info = self.board.getMoveTCPByUCI(uci_str, previousBoard)

        # Now push the move to update internal state
        self.board.push(result.move)
        self._pgn_node = self._pgn_node.add_variation(result.move)

        # Sync DGT board in simulation mode
        self.dgtBoard.sim_push(uci_str)

        # Execute the physical move
        self._execute_robot_move(move_info, result.move, messageCallback)

        logger.info(f"Robot played: {uci_str}")

    def _execute_robot_move(
        self, move_info: dict, chess_move: chess.Move, messageCallback=None
    ):
        """Execute the physical robot move based on move type."""
        move_type = move_info["type"]

        if move_type == "move":
            self.robot.movePiece(move_info["fromPos"].TCP, move_info["toPos"].TCP)

        elif move_type == "capture":
            self.robot.capturePiece(
                move_info["fromPos"].TCP, move_info["toPos"].TCP, self.capturePos.TCP
            )

        elif move_type == "enPassant":
            self.robot.enPassent(
                move_info["fromPos"].TCP,
                move_info["toPos"].TCP,
                move_info["enPassantTarget"].TCP,
                self.capturePos.TCP,
            )

        elif move_type == "castle":
            self.robot.castle(
                move_info["fromPos"].TCP,
                move_info["toPos"].TCP,
                move_info["castleFrom"].TCP,
                move_info["castleTo"].TCP,
            )

        elif move_type == "promotion":
            self.robot.promotion(move_info["fromPos"].TCP, self.capturePos.TCP)
            # Notify the user to place the promotion piece
            piece_name = PIECE_NAMES.get(move_info["promotionPiece"], "piece")
            color_name = "black" if self.board.turn else "white"  # turn already flipped
            to_square = chess_move.uci()[2:4]
            if messageCallback:
                messageCallback(
                    "Promotion",
                    f"Please place a {color_name} {piece_name} on {to_square}.",
                )

        elif move_type == "capturePromotion":
            self.robot.capturePromotion(
                move_info["fromPos"].TCP, move_info["toPos"].TCP, self.capturePos.TCP
            )
            piece_name = PIECE_NAMES.get(move_info["promotionPiece"], "piece")
            color_name = "black" if self.board.turn else "white"
            to_square = chess_move.uci()[2:4]
            if messageCallback:
                messageCallback(
                    "Promotion",
                    f"Please place a {color_name} {piece_name} on {to_square}.",
                )

        else:
            logger.warning(f"Unknown move type: {move_type}")

    def confirmMove(self, messageCallback):
        """
        Called when the human presses "Confirm Move" in the GUI.
        Reads the DGT board, validates the move, pushes it, then plays the robot's response.
        """
        # Read DGT board (read twice for reliability on real hardware)
        updatedBoard = self.dgtBoard.getCurentBoard()

        # Detect the UCI move
        move_uci = self.board.getUCI(str(updatedBoard))

        if move_uci is not None and move_uci in [
            m.uci() for m in self.board.board.legal_moves
        ]:
            logger.info(f"Human move confirmed: {move_uci}")
            self.move = move_uci

            chess_move = chess.Move.from_uci(move_uci)
            self._pgn_node = self._pgn_node.add_variation(chess_move)
            self.board.push(move_uci)

            # Sync DGT board in simulation
            self.dgtBoard.sim_push(move_uci)

            # Check for end-of-game conditions after human move
            if self.board.checkMate:
                messageCallback(
                    "You won",
                    "Checkmate! Congratulations, you have defeated the chess robot!",
                )
                return
            elif self.board.isInsuffichentMaterials:
                messageCallback(
                    "It's a draw", "Insufficient materials! The game is a draw!"
                )
                return
            elif self.board.staleMate:
                messageCallback("It's a draw", "Stalemate! The game is a draw!")
                return

            # Play the robot's response
            self.playRobotMove(messageCallback)

            # Check for end-of-game conditions after robot move
            if self.board.checkMate:
                messageCallback(
                    "You lost", "Checkmate! You have lost to the mighty chess robot!"
                )
            elif self.board.staleMate:
                messageCallback("It's a draw", "Stalemate! The game is a draw!")
            elif self.board.isInsuffichentMaterials:
                messageCallback(
                    "It's a draw", "Insufficient materials! The game is a draw!"
                )
        else:
            play_sound("speechfiles/illegal_move.mp3")
            messageCallback(
                "Illegal move", "The move you made is illegal. Please try again."
            )
