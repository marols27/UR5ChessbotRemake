import logging
import chess

logger = logging.getLogger(__name__)


class DGTBoard:
    """
    Interface to the DGT electronic chess board.

    In simulation mode, this uses an internal chess.Board to track state
    and allows moves to be injected programmatically.

    The simulation maintains two boards:
    - ``_sim_board``: the "official" board state (matches the Game's internal board)
    - ``_sim_preview``: a copy where the human's click-to-move is applied so that
      ``getCurentBoard()`` returns a state with the human's move already made.
      This is how the real DGT board works: the physical board reflects the
      move *before* the user presses "Confirm Move".
    """

    def __init__(self, port: str = "/dev/ttyS0", simulation: bool = False) -> None:
        self.simulation = simulation
        self._sim_board = chess.Board() if simulation else None
        self._sim_preview: chess.Board | None = None  # set when human clicks a move

        if not simulation:
            try:
                import asyncio
                import asyncdgt

                self.loop = asyncio.new_event_loop()
                self.dgtConnection = asyncdgt.auto_connect(self.loop, [port])
            except ImportError:
                raise RuntimeError(
                    "asyncdgt library not available. "
                    "Set CHESSBOT_SIMULATE=1 or install asyncdgt."
                )
            except Exception as e:
                raise RuntimeError(f"Failed to connect to DGT board on {port}: {e}")

    def getCurentBoard(self) -> str:
        """Returns a string representation of the current board (8 rows of space-separated pieces).

        In simulation mode, if a human move has been injected via
        ``sim_inject_human_move()``, returns the preview board (which
        includes the human's pending move). Otherwise returns the
        official sim board.
        """
        if self.simulation:
            board = (
                self._sim_preview if self._sim_preview is not None else self._sim_board
            )
            return str(board)

        try:
            strBoard = str(self.loop.run_until_complete(self.dgtConnection.get_board()))
            return strBoard
        except Exception as e:
            logger.error(f"Failed to read DGT board: {e}")
            raise

    def getCurentBoardFen(self) -> str:
        """Returns a FEN position string of the current board."""
        if self.simulation:
            board = (
                self._sim_preview if self._sim_preview is not None else self._sim_board
            )
            return board.board_fen()

        boardStr = self.getCurentBoard()
        return self._boardStringToFen(boardStr)

    def _boardStringToFen(self, boardStr: str) -> str:
        """Convert DGT board string format to FEN position string."""
        try:
            rows = boardStr.strip().split("\n")
            fen_rows = []
            for row in rows:
                cells = row.split()
                fen_row = ""
                empty_count = 0
                for cell in cells:
                    if cell == ".":
                        empty_count += 1
                    else:
                        if empty_count > 0:
                            fen_row += str(empty_count)
                            empty_count = 0
                        fen_row += cell
                if empty_count > 0:
                    fen_row += str(empty_count)
                fen_rows.append(fen_row)
            return "/".join(fen_rows)
        except Exception as e:
            logger.error(f"Failed to convert board string to FEN: {e}")
            return ""

    def sim_inject_human_move(self, move_uci: str) -> bool:
        """Inject a human move in simulation mode.

        Creates a preview board (copy of the official board + the move applied)
        so that ``getCurentBoard()`` returns the post-move state. The official
        ``_sim_board`` is *not* modified; that happens later when
        ``sim_push()`` is called from ``Game.confirmMove()``.

        Returns True if the move was applied, False otherwise.
        """
        if not self.simulation or self._sim_board is None:
            return False
        try:
            preview = self._sim_board.copy()
            preview.push_uci(move_uci)
            self._sim_preview = preview
            return True
        except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError) as e:
            logger.warning(f"sim_inject_human_move: invalid move {move_uci}: {e}")
            return False

    def sim_clear_preview(self):
        """Clear any pending preview (e.g. if the user deselects)."""
        self._sim_preview = None

    def sim_push(self, move_uci: str):
        """Push a move in simulation mode (used by Game to sync DGT board state).

        Also clears any preview board since the move is now officially applied.
        """
        if self.simulation and self._sim_board is not None:
            self._sim_board.push_uci(move_uci)
            self._sim_preview = None

    def sim_set_fen(self, fen: str):
        """Set the board to a specific FEN in simulation mode."""
        if self.simulation and self._sim_board is not None:
            self._sim_board.set_fen(fen)

    def close(self):
        """Clean up resources."""
        if not self.simulation and hasattr(self, "loop"):
            try:
                if hasattr(self, "dgtConnection"):
                    self.dgtConnection.close()
                self.loop.close()
            except Exception:
                pass
