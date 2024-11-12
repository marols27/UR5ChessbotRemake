import tkinter as tk
from tkinter import ttk, font as tkfont
from game_screen import show_game_screen
from Game import Game

def show_selection_screen(root, home_frame):
    home_frame.destroy()

    # Padding variables for easy adjustment
    BUTTON_PADX = 20
    BUTTON_PADY = 20

    # Set up style configurations
    style = ttk.Style()
    style.theme_use("clam")

    # Define styles for buttons and labels
    style.configure("Title.TLabel", font=("Ubuntu", 30, "bold"), foreground="white", background="#333333")
    style.configure("Easy.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="green", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("Medium.TButton", font=("Ubuntu", 18, "bold"), foreground="black", background="yellow", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("Hard.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="red", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("Default.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="#1a237e", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("Color.TButton", font=("Ubuntu", 18, "bold"), padding=(BUTTON_PADX, BUTTON_PADY))
    style.map("Next.TButton",
              background=[("active", "#c82333")])

    # Main Frame
    selection_frame = ttk.Frame(root, style="TFrame")
    selection_frame.pack(fill="both", expand=True)

    # Configuring grid to be responsive
    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)
    selection_frame.grid_columnconfigure(2, weight=1)
    selection_frame.grid_rowconfigure(0, weight=1)
    selection_frame.grid_rowconfigure(1, weight=3)
    selection_frame.grid_rowconfigure(2, weight=3)
    selection_frame.grid_rowconfigure(3, weight=1)

    # Title label for difficulty selection
    difficulty_label = ttk.Label(selection_frame, text="Choose Difficulty", style="Title.TLabel")
    difficulty_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="s")

    # Difficulty variable
    difficulty_var = tk.StringVar(value="easy")

    # Difficulty buttons with responsiveness
    difficulty_buttons = {
        "easy": ttk.Radiobutton(
            selection_frame, text="EASY", variable=difficulty_var, value="easy",
            style="Default.TButton", command=lambda: update_button_style(difficulty_var, difficulty_buttons)
        ),
        "medium": ttk.Radiobutton(
            selection_frame, text="MEDIUM", variable=difficulty_var, value="medium",
            style="Default.TButton", command=lambda: update_button_style(difficulty_var, difficulty_buttons)
        ),
        "hard": ttk.Radiobutton(
            selection_frame, text="HARD", variable=difficulty_var, value="hard",
            style="Default.TButton", command=lambda: update_button_style(difficulty_var, difficulty_buttons)
        )
    }

    # Placing difficulty buttons
    difficulty_buttons["easy"].grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    difficulty_buttons["medium"].grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
    difficulty_buttons["hard"].grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

    # Title label for color selection
    color_label = ttk.Label(selection_frame, text="Choose Your Color", style="Title.TLabel")
    color_label.grid(row=2, column=0, columnspan=3, pady=20, sticky="s")

    # Piece color variable
    color_var = tk.StringVar(value="white")

    # Color selection buttons
    color_buttons = {
        "white": ttk.Radiobutton(
            selection_frame, text="WHITE", variable=color_var, value="white",
            style="Color.TButton"
        ),
        "black": ttk.Radiobutton(
            selection_frame, text="BLACK", variable=color_var, value="black",
            style="Color.TButton"
        )
    }

    # Placing color selection buttons
    color_buttons["white"].grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
    color_buttons["black"].grid(row=3, column=2, sticky="nsew", padx=10, pady=10)

    # Function for "Next" button command
    def handle_next():
        show_game_screen(root, selection_frame, color_var.get(), difficulty_var.get())

    # Next Button
    next_button = ttk.Button(
        selection_frame,
        text="NEXT",
        command=handle_next,
        style="Next.TButton"
    )
    next_button.grid(row=4, column=1, pady=20, sticky="se")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")  # Start app in fullscreen
    root.title("HVL Robotics Chess Robot")
    show_selection_screen(root, tk.Frame(root))
    root.mainloop()
