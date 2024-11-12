import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class Chessboard(tk.Canvas):
    def __init__(self, parent, square_size=80, flipped=False, *args, **kwargs):
        self.square_size = square_size
        width = square_size * 8
        height = square_size * 8
        super().__init__(parent, width=width, height=height, *args, **kwargs)
        self.flipped = flipped  # Add a flag to flip the board
        self.pieces = self.load_images()
        self.board = [[''] * 8 for _ in range(8)]  # 8x8 empty board
        self.current_fen = ""  # Track the current FEN
        self.square_ids = [[None for _ in range(8)] for _ in range(8)]  # Store square ids for later access

    def load_images(self):
        pieces = {}
        piece_map = {
            'wp': 'Chess_plt60.png', 'wr': 'Chess_rlt60.png', 'wn': 'Chess_nlt60.png',
            'wb': 'Chess_blt60.png', 'wq': 'Chess_qlt60.png', 'wk': 'Chess_klt60.png',
            'bp': 'Chess_pdt60.png', 'br': 'Chess_rdt60.png', 'bn': 'Chess_ndt60.png',
            'bb': 'Chess_bdt60.png', 'bq': 'Chess_qdt60.png', 'bk': 'Chess_kdt60.png'
        }
        base_path = os.path.join(os.path.dirname(__file__), '../assets/images/')
        for key, filename in piece_map.items():
            image_path = os.path.join(base_path, filename)
            image = Image.open(image_path)
            image = image.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
            pieces[key] = ImageTk.PhotoImage(image)
        return pieces

    def update_board(self, fen):
        self.current_fen = fen
        board = self.parse_fen(fen)
        self.render_board(board)

    def render_board(self, board):
        self.delete("all")  # Clear the board
        file_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        rank_labels = ['1', '2', '3', '4', '5', '6', '7', '8']
        if self.flipped:
            rank_labels = rank_labels[::-1]
            file_labels = file_labels[::-1]
        
        for i in range(8):
            for j in range(8):
                x1, y1 = j * self.square_size, i * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
                square_id = self.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
                self.square_ids[i][j] = square_id

                # Flip the board if necessary
                if self.flipped:
                    i_render, j_render = 7 - i, 7 - j
                else:
                    i_render, j_render = i, j

                piece = self.fen_to_piece(board[i_render][j_render])
                
                if piece:
                    piece_image = self.pieces.get(piece)
                    if piece_image is None:
                        print(f"Warning: No image found for piece '{piece}'")
                    else:
                        # Create and tag the piece with its position
                        piece_id = self.create_image(x1, y1, anchor='nw', image=piece_image)
                        self.addtag_withtag(f"piece-{i_render}-{j_render}", piece_id)  # Tag the piece with its position

                # Add file and rank labels
                if j == 0:  # Label the ranks on the first file
                    self.create_text(x1 + 5, y2 - 5, text=rank_labels[7 - i], anchor='sw', font=("Helvetica", 18,"bold"), fill="black" if color == "#f0d9b5" else "white")
                
                if i == 7:  # Label the files on the first rank
                    self.create_text(x2 - 5, y2 - 5, text=file_labels[j], anchor='se', font=("Helvetica", 18, "bold"), fill="black" if color == "#f0d9b5" else "white")

    def highlight_square(self, file, rank, color="#ffff00"):
        """Highlight an existing square on the board."""
        if not self.flipped:
            rank = 7 - rank
        else:
            file = 7 - file

        # Get the square ID and update its color
        square_id = self.square_ids[rank][file]
        self.itemconfig(square_id, fill=color, outline=color)

        # Find and raise the piece on this square, if it exists
        piece_id = self.find_withtag(f"piece-{rank}-{file}")
        if piece_id:
            self.tag_raise(piece_id)


    def parse_fen(self, fen):
        rows = fen.split(' ')[0].split('/')
        board = []
        for row in rows:
            board_row = []
            for char in row:
                if char.isdigit():
                    board_row.extend([''] * int(char))
                else:
                    board_row.append(char)
            board.append(board_row)
        return board

    def fen_to_piece(self, char):
        piece_map = {
            'p': 'bp', 'r': 'br', 'n': 'bn', 'b': 'bb', 'q': 'bq', 'k': 'bk',
            'P': 'wp', 'R': 'wr', 'N': 'wn', 'B': 'wb', 'Q': 'wq', 'K': 'wk'
        }
        return piece_map.get(char, '')