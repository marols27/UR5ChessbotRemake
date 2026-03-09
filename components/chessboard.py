"""
Chessboard canvas component: Renders a chess position from FEN.

Fixes over original:
- highlight_square correctly handles both flipped and non-flipped boards
- Uses os.path.dirname(__file__) for reliable image path resolution
"""

import os
import tkinter as tk
from PIL import Image, ImageTk


class Chessboard(tk.Canvas):
    """Chess board canvas that renders a position from FEN.

    In simulation mode, supports click-to-move: the user clicks a piece
    to select it (highlighted), then clicks a destination square. If a
    ``move_callback`` is provided, it is called with the UCI string of the
    move (e.g. ``"e2e4"``). The caller is responsible for validating
    legality.
    """

    def __init__(
        self, parent, square_size=80, flipped=False, move_callback=None, *args, **kwargs
    ):
        self.square_size = square_size
        width = square_size * 8
        height = square_size * 8
        super().__init__(parent, width=width, height=height, *args, **kwargs)
        self.flipped = flipped
        self.pieces = self.load_images()
        self.board = [[""] * 8 for _ in range(8)]
        self.current_fen = ""
        self.square_ids = [[None for _ in range(8)] for _ in range(8)]

        # Click-to-move state
        self._move_callback = move_callback
        self._selected_square: tuple[int, int] | None = None  # (file, rank) 0-indexed
        self._legal_targets: list[str] = []  # UCI target squares for selected piece

        if move_callback is not None:
            self.bind("<Button-1>", self._on_click)

    def load_images(self):
        pieces = {}
        piece_map = {
            "wp": "Chess_plt60.png",
            "wr": "Chess_rlt60.png",
            "wn": "Chess_nlt60.png",
            "wb": "Chess_blt60.png",
            "wq": "Chess_qlt60.png",
            "wk": "Chess_klt60.png",
            "bp": "Chess_pdt60.png",
            "br": "Chess_rdt60.png",
            "bn": "Chess_ndt60.png",
            "bb": "Chess_bdt60.png",
            "bq": "Chess_qdt60.png",
            "bk": "Chess_kdt60.png",
        }
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
        for key, filename in piece_map.items():
            image_path = os.path.join(base_path, filename)
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(
                    (self.square_size, self.square_size), Image.Resampling.LANCZOS
                )
                pieces[key] = ImageTk.PhotoImage(image)
            else:
                # Don't crash if image is missing
                pass
        return pieces

    def update_board(self, fen):
        self.current_fen = fen
        board = self.parse_fen(fen)
        self.render_board(board)

    def render_board(self, board):
        self.delete("all")
        file_labels = ["a", "b", "c", "d", "e", "f", "g", "h"]
        rank_labels = ["1", "2", "3", "4", "5", "6", "7", "8"]
        if self.flipped:
            rank_labels = rank_labels[::-1]
            file_labels = file_labels[::-1]

        for i in range(8):
            for j in range(8):
                x1, y1 = j * self.square_size, i * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
                square_id = self.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color
                )
                self.square_ids[i][j] = square_id

                # Map display position to board position
                if self.flipped:
                    i_render, j_render = 7 - i, 7 - j
                else:
                    i_render, j_render = i, j

                piece = self.fen_to_piece(board[i_render][j_render])

                if piece:
                    piece_image = self.pieces.get(piece)
                    if piece_image:
                        piece_id = self.create_image(
                            x1, y1, anchor="nw", image=piece_image
                        )
                        self.addtag_withtag(f"piece-{i_render}-{j_render}", piece_id)

                # File and rank labels
                if j == 0:
                    self.create_text(
                        x1 + 5,
                        y2 - 5,
                        text=rank_labels[7 - i],
                        anchor="sw",
                        font=("Helvetica", 18, "bold"),
                        fill="black" if color == "#f0d9b5" else "white",
                    )
                if i == 7:
                    self.create_text(
                        x2 - 5,
                        y2 - 5,
                        text=file_labels[j],
                        anchor="se",
                        font=("Helvetica", 18, "bold"),
                        fill="black" if color == "#f0d9b5" else "white",
                    )

    def highlight_square(self, file: int, rank: int, color="#ffff00"):
        """
        Highlight a square on the board.

        Args:
            file: 0-7 (a-h)
            rank: 0-7 (1-8)
            color: highlight color

        FIX: Correctly compute display row/col for both flipped and non-flipped.
        """
        # Convert chess coordinates (file, rank) to display grid (row, col)
        if self.flipped:
            display_col = 7 - file
            display_row = (
                rank  # rank 0 (rank 1) at bottom when flipped = row 0 at top visually
            )
        else:
            display_col = file
            display_row = 7 - rank  # rank 0 (rank 1) at bottom = row 7

        if not (0 <= display_row <= 7 and 0 <= display_col <= 7):
            return

        square_id = self.square_ids[display_row][display_col]
        if square_id:
            self.itemconfig(square_id, fill=color, outline=color)

        # Raise pieces above highlight
        piece_tag = (
            f"piece-{7 - rank}-{file}"
            if not self.flipped
            else f"piece-{7 - rank}-{file}"
        )
        # The piece tag uses board coordinates (i_render, j_render) which are the actual board row/col
        actual_row = 7 - rank  # board row (0 = rank 8)
        actual_col = file
        piece_id = self.find_withtag(f"piece-{actual_row}-{actual_col}")
        if piece_id:
            self.tag_raise(piece_id)

    def parse_fen(self, fen):
        rows = fen.split(" ")[0].split("/")
        board = []
        for row in rows:
            board_row = []
            for char in row:
                if char.isdigit():
                    board_row.extend([""] * int(char))
                else:
                    board_row.append(char)
            board.append(board_row)
        return board

    def fen_to_piece(self, char):
        piece_map = {
            "p": "bp",
            "r": "br",
            "n": "bn",
            "b": "bb",
            "q": "bq",
            "k": "bk",
            "P": "wp",
            "R": "wr",
            "N": "wn",
            "B": "wb",
            "Q": "wq",
            "K": "wk",
        }
        return piece_map.get(char, "")

    # ------------------------------------------------------------------
    # Click-to-move (simulation mode)
    # ------------------------------------------------------------------

    def _pixel_to_square(self, x: int, y: int) -> tuple[int, int]:
        """Convert pixel coordinates to (file, rank) each 0-indexed.

        file 0 = a, rank 0 = rank 1.
        """
        col = x // self.square_size
        row = y // self.square_size
        col = max(0, min(7, col))
        row = max(0, min(7, row))

        if self.flipped:
            file = 7 - col
            rank = row  # row 0 = rank 1 when flipped
        else:
            file = col
            rank = 7 - row  # row 0 = rank 8, so rank = 7-row

        return file, rank

    @staticmethod
    def _square_name(file: int, rank: int) -> str:
        """Return algebraic name like 'e4' for file=4, rank=3."""
        return chr(ord("a") + file) + str(rank + 1)

    def _on_click(self, event):
        """Handle a click on the board canvas."""
        file, rank = self._pixel_to_square(event.x, event.y)

        if self._selected_square is None:
            # First click — select a piece
            self._try_select(file, rank)
        else:
            sel_file, sel_rank = self._selected_square
            if (file, rank) == (sel_file, sel_rank):
                # Clicked the same square — deselect
                self._deselect()
            else:
                # Second click — attempt move
                from_name = self._square_name(sel_file, sel_rank)
                to_name = self._square_name(file, rank)
                uci = from_name + to_name

                # Check for pawn promotion (pawn reaching last rank)
                board_row = 7 - (sel_rank)  # display row in parse_fen order
                parsed = self.parse_fen(self.current_fen)
                if 0 <= board_row < 8 and 0 <= sel_file < 8:
                    piece_char = parsed[board_row][sel_file]
                    if piece_char.lower() == "p" and (rank == 7 or rank == 0):
                        # Auto-promote to queen (most common)
                        uci += "q"

                self._deselect()
                if self._move_callback:
                    self._move_callback(uci)

    def _try_select(self, file: int, rank: int):
        """Try to select a piece at the given square."""
        # Check there's actually a piece here
        board_row = 7 - rank
        parsed = self.parse_fen(self.current_fen)
        if board_row < 0 or board_row >= 8 or file < 0 or file >= 8:
            return
        piece_char = parsed[board_row][file]
        if piece_char == "" or piece_char == ".":
            return  # empty square

        self._selected_square = (file, rank)

        # Highlight the selected square
        self.highlight_square(file, rank, color="#7fc97f")

    def _deselect(self):
        """Deselect the current piece and redraw the board."""
        self._selected_square = None
        if self.current_fen:
            self.update_board(self.current_fen)

    def set_move_callback(self, callback):
        """Set or update the move callback after construction."""
        self._move_callback = callback
        if callback is not None:
            self.bind("<Button-1>", self._on_click)
        else:
            self.unbind("<Button-1>")
