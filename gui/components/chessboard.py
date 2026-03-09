"""
Chessboard canvas component: Renders a chess position from FEN.

Fixes over original:
- highlight_square correctly handles both flipped and non-flipped boards
- Uses os.path.dirname(__file__) for reliable image path resolution
- Board colors and highlight colors imported from theme
- Wrapped in styled CTkFrame for modern border treatment
- Coordinate label font reduced to 14
- Added highlight_last_move() method
"""

import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from ..theme import (
    BOARD_LIGHT, BOARD_DARK, BOARD_HIGHLIGHT, BOARD_SELECT,
    BOARD_NAV_HIGHLIGHT, BG_SECONDARY, BORDER_SUBTLE, BORDER_WIDTH,
    CORNER_RADIUS,
)


class Chessboard(ctk.CTkFrame):
    """Chess board wrapped in a styled frame.

    In simulation mode, supports click-to-move: the user clicks a piece
    to select it (highlighted), then clicks a destination square. If a
    ``move_callback`` is provided, it is called with the UCI string of the
    move (e.g. ``"e2e4"``). The caller is responsible for validating
    legality.
    """

    def __init__(
        self, parent, square_size=80, flipped=False, move_callback=None, *args, **kwargs
    ):
        super().__init__(
            parent,
            fg_color=BG_SECONDARY,
            corner_radius=CORNER_RADIUS,
            border_color=BORDER_SUBTLE,
            border_width=BORDER_WIDTH,
            *args, **kwargs,
        )
        self.square_size = square_size
        width = square_size * 8
        height = square_size * 8
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self.canvas.pack(padx=6, pady=6)
        self.flipped = flipped
        self.pieces = self._load_images()
        self.board = [[""] * 8 for _ in range(8)]
        self.current_fen = ""
        self.square_ids = [[None for _ in range(8)] for _ in range(8)]

        # Click-to-move state
        self._move_callback = move_callback
        self._selected_square: tuple[int, int] | None = None
        self._legal_targets: list[str] = []

        if move_callback is not None:
            self.canvas.bind("<Button-1>", self._on_click)

    def _load_images(self):
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
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images")
        for key, filename in piece_map.items():
            image_path = os.path.join(base_path, filename)
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(
                    (self.square_size, self.square_size), Image.Resampling.LANCZOS
                )
                pieces[key] = ImageTk.PhotoImage(image)
        return pieces

    def update_board(self, fen):
        self.current_fen = fen
        board = self._parse_fen(fen)
        self._render_board(board)

    def _render_board(self, board):
        self.canvas.delete("all")
        file_labels = ["a", "b", "c", "d", "e", "f", "g", "h"]
        rank_labels = ["1", "2", "3", "4", "5", "6", "7", "8"]
        if self.flipped:
            rank_labels = rank_labels[::-1]
            file_labels = file_labels[::-1]

        for i in range(8):
            for j in range(8):
                x1, y1 = j * self.square_size, i * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                color = BOARD_LIGHT if (i + j) % 2 == 0 else BOARD_DARK
                square_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color
                )
                self.square_ids[i][j] = square_id

                if self.flipped:
                    i_render, j_render = 7 - i, 7 - j
                else:
                    i_render, j_render = i, j

                piece = self._fen_to_piece(board[i_render][j_render])

                if piece:
                    piece_image = self.pieces.get(piece)
                    if piece_image:
                        piece_id = self.canvas.create_image(
                            x1, y1, anchor="nw", image=piece_image
                        )
                        self.canvas.addtag_withtag(
                            f"piece-{i_render}-{j_render}", piece_id
                        )

                # File and rank labels
                if j == 0:
                    self.canvas.create_text(
                        x1 + 5,
                        y2 - 5,
                        text=rank_labels[7 - i],
                        anchor="sw",
                        font=("Helvetica", 14, "bold"),
                        fill="black" if color == BOARD_LIGHT else "white",
                    )
                if i == 7:
                    self.canvas.create_text(
                        x2 - 5,
                        y2 - 5,
                        text=file_labels[j],
                        anchor="se",
                        font=("Helvetica", 14, "bold"),
                        fill="black" if color == BOARD_LIGHT else "white",
                    )

    def highlight_square(self, file: int, rank: int, color=None):
        """Highlight a square on the board.

        Args:
            file: 0-7 (a-h)
            rank: 0-7 (1-8)
            color: highlight color (defaults to BOARD_HIGHLIGHT)
        """
        if color is None:
            color = BOARD_HIGHLIGHT

        if self.flipped:
            display_col = 7 - file
            display_row = rank
        else:
            display_col = file
            display_row = 7 - rank

        if not (0 <= display_row <= 7 and 0 <= display_col <= 7):
            return

        square_id = self.square_ids[display_row][display_col]
        if square_id:
            self.canvas.itemconfig(square_id, fill=color, outline=color)

        actual_row = 7 - rank
        actual_col = file
        piece_id = self.canvas.find_withtag(f"piece-{actual_row}-{actual_col}")
        if piece_id:
            self.canvas.tag_raise(piece_id)

    def highlight_last_move(self, uci: str):
        """Highlight the from/to squares of a move given as UCI string (e.g. 'e2e4')."""
        if len(uci) < 4:
            return
        from_file = ord(uci[0]) - ord("a")
        from_rank = int(uci[1]) - 1
        to_file = ord(uci[2]) - ord("a")
        to_rank = int(uci[3]) - 1
        self.highlight_square(from_file, from_rank, color=BOARD_HIGHLIGHT)
        self.highlight_square(to_file, to_rank, color=BOARD_HIGHLIGHT)

    def _parse_fen(self, fen):
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

    def _fen_to_piece(self, char):
        piece_map = {
            "p": "bp", "r": "br", "n": "bn", "b": "bb", "q": "bq", "k": "bk",
            "P": "wp", "R": "wr", "N": "wn", "B": "wb", "Q": "wq", "K": "wk",
        }
        return piece_map.get(char, "")

    # ------------------------------------------------------------------
    # Click-to-move (simulation mode)
    # ------------------------------------------------------------------

    def _pixel_to_square(self, x: int, y: int) -> tuple[int, int]:
        col = x // self.square_size
        row = y // self.square_size
        col = max(0, min(7, col))
        row = max(0, min(7, row))

        if self.flipped:
            file = 7 - col
            rank = row
        else:
            file = col
            rank = 7 - row

        return file, rank

    @staticmethod
    def _square_name(file: int, rank: int) -> str:
        return chr(ord("a") + file) + str(rank + 1)

    def _on_click(self, event):
        file, rank = self._pixel_to_square(event.x, event.y)

        if self._selected_square is None:
            self._try_select(file, rank)
        else:
            sel_file, sel_rank = self._selected_square
            if (file, rank) == (sel_file, sel_rank):
                self._deselect()
            else:
                from_name = self._square_name(sel_file, sel_rank)
                to_name = self._square_name(file, rank)
                uci = from_name + to_name

                board_row = 7 - sel_rank
                parsed = self._parse_fen(self.current_fen)
                if 0 <= board_row < 8 and 0 <= sel_file < 8:
                    piece_char = parsed[board_row][sel_file]
                    if piece_char.lower() == "p" and (rank == 7 or rank == 0):
                        uci += "q"

                self._deselect()
                if self._move_callback:
                    self._move_callback(uci)

    def _try_select(self, file: int, rank: int):
        board_row = 7 - rank
        parsed = self._parse_fen(self.current_fen)
        if board_row < 0 or board_row >= 8 or file < 0 or file >= 8:
            return
        piece_char = parsed[board_row][file]
        if piece_char == "" or piece_char == ".":
            return

        self._selected_square = (file, rank)
        self.highlight_square(file, rank, color=BOARD_SELECT)

    def _deselect(self):
        self._selected_square = None
        if self.current_fen:
            self.update_board(self.current_fen)

    def set_move_callback(self, callback):
        self._move_callback = callback
        if callback is not None:
            self.canvas.bind("<Button-1>", self._on_click)
        else:
            self.canvas.unbind("<Button-1>")
