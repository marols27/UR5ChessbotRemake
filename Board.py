"""
Board module: Manages the virtual chess board state, move detection, and
coordinate mapping between board squares and robot TCP positions.
"""

import logging
import chess
import chess.pgn
from UR5Feature import UR5Feature
from ToolCenterPoint import ToolCenterPoint as TCP

logger = logging.getLogger(__name__)

FILES = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}


class Board:
    """
    Virtual representation of the chess board that tracks game state and
    maps board positions to physical robot TCP coordinates.

    Fixes over original:
    - str.replace() return values are now captured (were silently discarded)
    - getPGN() uses a chess.pgn.Game *instance* and advances the node
    - En passant target uses string concatenation (not str + int)
    - strBoardToMatrix is robust (doesn't require exactly 127 chars)
    - getSquareTCP validates input
    - Legal moves are obtained via chess.Move.__str__ directly
    """

    def __init__(
        self,
        start_fen: str,
        feature: UR5Feature,
        board_size: float = 0.54,
        square_size: float = 0.055,
    ):
        self.board_size = board_size
        self.square_size = square_size
        self.feature = feature
        self.board = chess.Board(fen=start_fen)
        self._sync_state()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _sync_state(self):
        """Refresh cached state properties from the underlying chess.Board."""
        self.turn = self.board.turn
        self.checkMate = self.board.is_checkmate()
        self.staleMate = self.board.is_stalemate()
        self.isInsuffichentMaterials = self.board.is_insufficient_material()
        self.legalMoves = [m.uci() for m in self.board.legal_moves]

    # ------------------------------------------------------------------
    # Coordinate mapping
    # ------------------------------------------------------------------

    def getSquareTCP(self, board_pos) -> TCP:
        """
        Get the robot TCP for a board square.

        Args:
            board_pos: Either a string like "e4" or a list like ["e", 4].

        Returns:
            TCP for that square relative to the board feature.
        """
        if isinstance(board_pos, (list, tuple)):
            file_letter = str(board_pos[0]).lower()
            rank_number = int(board_pos[1])
        elif isinstance(board_pos, str) and len(board_pos) == 2:
            file_letter = board_pos[0].lower()
            rank_number = int(board_pos[1])
        else:
            raise ValueError(f"Invalid board position: {board_pos!r}")

        if file_letter not in FILES:
            raise ValueError(f"Invalid file letter: {file_letter!r}")
        if not 1 <= rank_number <= 8:
            raise ValueError(f"Invalid rank number: {rank_number}")

        file_idx = FILES[file_letter]
        return self.feature.getFeatureRelativeTCP(
            self.square_size * (file_idx - 1),
            self.square_size * (rank_number - 1),
            0,
        )

    # ------------------------------------------------------------------
    # Move detection from board comparison
    # ------------------------------------------------------------------

    def getUCI(self, to_board_str: str) -> str | None:
        """
        Detect the UCI move by comparing the current internal board state
        with a new board string (as returned by DGTBoard.getCurentBoard()).

        Returns the UCI string if a valid move is detected, or None.
        """

        def file_number_to_letter(number: int) -> str:
            for letter, num in FILES.items():
                if num == number:
                    return letter
            return ""

        from_board = self.strBoardToMatrix(str(self.board))
        to_board = self.strBoardToMatrix(to_board_str)
        if from_board is None or to_board is None:
            logger.warning("Could not parse board strings for move detection")
            return None

        changed_squares: list[dict] = []
        for x in range(1, 9):
            for y in range(1, 9):
                before = from_board[8 - y][x - 1]
                after = to_board[8 - y][x - 1]
                if before != after:
                    changed_squares.append(
                        {
                            "file": x,
                            "fileLetter": file_number_to_letter(x),
                            "rank": y,
                            "before": before,
                            "after": after,
                        }
                    )

        n = len(changed_squares)

        # Piece picked up (incomplete move)
        if n == 1:
            return None

        # Normal move / capture / promotion
        if n == 2:
            cs = changed_squares
            moving_pawn = (
                cs[0]["before"].lower() == "p" or cs[1]["before"].lower() == "p"
            )
            changing_files = cs[0]["file"] != cs[1]["file"]
            en_passant_swap = (
                cs[0]["before"] == cs[1]["after"] and cs[0]["after"] == cs[1]["before"]
            )
            king_castling = (
                cs[0]["before"].lower() == "k" or cs[1]["before"].lower() == "k"
            ) and abs(cs[0]["file"] - cs[1]["file"]) == 2

            incomplete_cases = [
                cs[0]["after"] == cs[1]["after"],  # During capture, both emptied
                moving_pawn and changing_files and en_passant_swap,
                king_castling,
            ]
            if any(incomplete_cases):
                return None

            if cs[0]["after"] == ".":
                from_sq, to_sq = cs[0], cs[1]
            else:
                from_sq, to_sq = cs[1], cs[0]

            uci = from_sq["fileLetter"] + str(from_sq["rank"])
            uci += to_sq["fileLetter"] + str(to_sq["rank"])

            # Promotion detection
            if from_sq["before"].lower() == "p" and to_sq["after"].lower() != "p":
                uci += to_sq["after"].lower()

            return uci

        # En passant (3 changed squares)
        if n == 3:
            pawn_squares = []
            empty_square = None
            for sq in changed_squares:
                if sq["before"].lower() == "p":
                    pawn_squares.append(sq)
                else:
                    empty_square = sq

            if len(pawn_squares) != 2 or empty_square is None:
                return None

            a_ok = (
                pawn_squares[0]["before"].lower() == "p"
                and pawn_squares[0]["after"] == "."
            )
            b_ok = (
                pawn_squares[1]["before"].lower() == "p"
                and pawn_squares[1]["after"] == "."
            )
            to_ok = (
                empty_square["before"] == "." and empty_square["after"].lower() == "p"
            )

            if not (a_ok and b_ok and to_ok):
                return None

            # The assaulting pawn changed files
            assaulting = (
                pawn_squares[0]
                if pawn_squares[0]["file"] != empty_square["file"]
                else pawn_squares[1]
            )
            return (
                assaulting["fileLetter"]
                + str(assaulting["rank"])
                + empty_square["fileLetter"]
                + str(empty_square["rank"])
            )

        # Castling (4 changed squares)
        if n == 4:
            kings_move = [None, None]
            rooks_move = [None, None]
            for sq in changed_squares:
                if sq["before"].lower() == "k":
                    kings_move[0] = sq
                elif sq["before"].lower() == "r":
                    rooks_move[0] = sq
                elif sq["after"].lower() == "k":
                    kings_move[1] = sq
                elif sq["after"].lower() == "r":
                    rooks_move[1] = sq
                else:
                    return None

            if kings_move[0] is None or kings_move[1] is None:
                return None

            if (
                abs(kings_move[0]["file"] - kings_move[1]["file"]) == 2
                and kings_move[0]["rank"] == kings_move[1]["rank"]
            ):
                return (
                    kings_move[0]["fileLetter"]
                    + str(kings_move[0]["rank"])
                    + kings_move[1]["fileLetter"]
                    + str(kings_move[1]["rank"])
                )
            return None

        return None

    # ------------------------------------------------------------------
    # Move TCP computation for the robot
    # ------------------------------------------------------------------

    def getMoveTCPByUCI(self, uci_move: str, previous_board: str) -> dict:
        """
        Given a UCI move string and the board state *before* the move was
        pushed, return a dict describing the move type and relevant TCPs.
        """
        from_sq = [uci_move[0], int(uci_move[1])]
        to_sq = [uci_move[2], int(uci_move[3])]
        from_board = self.strBoardToMatrix(previous_board)
        to_board = self.strBoardToMatrix(str(self.board))

        if from_board is None or to_board is None:
            logger.error("Cannot parse board for getMoveTCPByUCI")
            return {
                "type": "move",
                "fromPos": self.getSquareTCP(from_sq),
                "toPos": self.getSquareTCP(to_sq),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None,
            }

        to_file_idx = FILES[to_sq[0]] - 1
        from_file_idx = FILES[from_sq[0]] - 1

        is_to_occupied = from_board[8 - to_sq[1]][to_file_idx] != "."
        is_from_pawn = from_board[8 - from_sq[1]][from_file_idx].lower() == "p"
        is_to_empty = from_board[8 - to_sq[1]][to_file_idx] == "."
        is_file_changing = from_sq[0] != to_sq[0]
        is_from_king = from_board[8 - from_sq[1]][from_file_idx].lower() == "k"
        is_moving_2_files = abs(FILES[from_sq[0]] - FILES[to_sq[0]]) == 2

        # Promotion (5-char UCI)
        if len(uci_move) == 5:
            return {
                "type": "capturePromotion" if is_to_occupied else "promotion",
                "fromPos": self.getSquareTCP(from_sq),
                "toPos": self.getSquareTCP(to_sq),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": uci_move[4],
            }

        # En passant
        if is_from_pawn and is_to_empty and is_file_changing:
            # FIX: use string concatenation, not str + int
            ep_target = to_sq[0] + str(from_sq[1])
            return {
                "type": "enPassant",
                "fromPos": self.getSquareTCP(from_sq),
                "toPos": self.getSquareTCP(to_sq),
                "enPassantTarget": self.getSquareTCP(ep_target),
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None,
            }

        # Castling
        if is_from_king and is_moving_2_files:
            rank_str = str(from_sq[1])
            if to_sq[0] == "c":
                rook_from = "a" + rank_str
                rook_to = "d" + rank_str
            else:
                rook_from = "h" + rank_str
                rook_to = "f" + rank_str
            return {
                "type": "castle",
                "fromPos": self.getSquareTCP(from_sq),
                "toPos": self.getSquareTCP(to_sq),
                "enPassantTarget": None,
                "castleFrom": self.getSquareTCP(rook_from),
                "castleTo": self.getSquareTCP(rook_to),
                "promotionPiece": None,
            }

        # Capture
        if is_to_occupied:
            return {
                "type": "capture",
                "fromPos": self.getSquareTCP(from_sq),
                "toPos": self.getSquareTCP(to_sq),
                "enPassantTarget": None,
                "castleFrom": None,
                "castleTo": None,
                "promotionPiece": None,
            }

        # Normal move
        return {
            "type": "move",
            "fromPos": self.getSquareTCP(from_sq),
            "toPos": self.getSquareTCP(to_sq),
            "enPassantTarget": None,
            "castleFrom": None,
            "castleTo": None,
            "promotionPiece": None,
        }

    # ------------------------------------------------------------------
    # Board string parsing
    # ------------------------------------------------------------------

    @staticmethod
    def strBoardToMatrix(board_str: str) -> list[list[str]] | None:
        """
        Parse a board string (8 rows of space-separated pieces) into an 8x8 matrix.

        More robust than the original: does not require exactly 127 chars.
        """
        try:
            rows = board_str.strip().split("\n")
            if len(rows) != 8:
                logger.warning(f"Expected 8 rows, got {len(rows)}")
                return None
            matrix = []
            for row in rows:
                cells = row.split()
                if len(cells) != 8:
                    logger.warning(
                        f"Expected 8 cells in row, got {len(cells)}: {row!r}"
                    )
                    return None
                matrix.append(cells)
            return matrix
        except Exception as e:
            logger.error(f"Failed to parse board string: {e}")
            return None

    # ------------------------------------------------------------------
    # Push move
    # ------------------------------------------------------------------

    def push(self, uci):
        """Push a move (UCI string or chess.Move) onto the board."""
        if isinstance(uci, chess.Move):
            self.board.push(uci)
        else:
            self.board.push_uci(str(uci))
        self._sync_state()

    # ------------------------------------------------------------------
    # PGN generation
    # ------------------------------------------------------------------

    def getPGN(self) -> str:
        """
        Return the game in PGN format.

        FIX: uses chess.pgn.Game() *instance* and advances the node pointer.
        """
        game = chess.pgn.Game()
        node = game
        for move in self.board.move_stack:
            node = node.add_variation(move)
        return str(game)
