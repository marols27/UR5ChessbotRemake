import tkinter as tk
from tkinter import ttk
from game_screen import show_game_screen

def show_selection_screen(root):
    # Destroy any existing frames
    for widget in root.winfo_children():
        widget.destroy()

    # Padding variables for easy adjustment
    BUTTON_PADX = 20
    BUTTON_PADY = 20

    # Function to update button styles when selected
    def update_button_style(var, buttons, styles):
        for value, button in buttons.items():
            if var.get() == value:
                button.config(style=styles[value]['selected'])
            else:
                button.config(style=styles[value]['default'])

    # Set up style configurations
    style = ttk.Style()
    style.theme_use("clam")

    # Define styles for difficulty buttons
    difficulty_styles = {
        "easy": {
            "default": "EasyDefault.TButton",
            "selected": "EasySelected.TButton"
        },
        "medium": {
            "default": "MediumDefault.TButton",
            "selected": "MediumSelected.TButton"
        },
        "hard": {
            "default": "HardDefault.TButton",
            "selected": "HardSelected.TButton"
        }
    }

    # Define styles for color buttons
    color_styles = {
        "white": {
            "default": "ColorDefault.TButton",
            "selected": "WhiteSelected.TButton"
        },
        "black": {
            "default": "ColorDefault.TButton",
            "selected": "BlackSelected.TButton"
        }
    }

    # Configure default styles (black background) for all difficulty buttons
    style.configure("EasyDefault.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="black", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("MediumDefault.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="black", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("HardDefault.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="black", padding=(BUTTON_PADX, BUTTON_PADY))

    # Configure selected styles for difficulty buttons
    style.configure("EasySelected.TButton", font=("Ubuntu", 18, "bold"), foreground="black", background="green", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("MediumSelected.TButton", font=("Ubuntu", 18, "bold"), foreground="black", background="yellow", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("HardSelected.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="red", padding=(BUTTON_PADX, BUTTON_PADY))

    # Configure default style (black background) for color buttons
    style.configure("ColorDefault.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="black", padding=(BUTTON_PADX, BUTTON_PADY))

    # Configure selected styles for color buttons
    style.configure("WhiteSelected.TButton", font=("Ubuntu", 18, "bold"), foreground="black", background="white", padding=(BUTTON_PADX, BUTTON_PADY))
    style.configure("BlackSelected.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="black", padding=(BUTTON_PADX, BUTTON_PADY))

    # Main Frame
    selection_frame = ttk.Frame(root, padding="20")
    selection_frame.pack(fill="both", expand=True)

    # Configuring grid to be responsive
    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)
    selection_frame.grid_columnconfigure(2, weight=1)
    selection_frame.grid_rowconfigure(0, weight=1)
    selection_frame.grid_rowconfigure(1, weight=1)
    selection_frame.grid_rowconfigure(2, weight=1)
    selection_frame.grid_rowconfigure(3, weight=1)
    selection_frame.grid_rowconfigure(4, weight=1)

    # Title label
    title_label = ttk.Label(selection_frame, text="Choose Difficulty and Piece Color", font=("Ubuntu", 24, "bold"))
    title_label.grid(row=0, column=0, columnspan=3, pady=10)

    # Difficulty variable
    difficulty_var = tk.StringVar(value="easy")

    # Difficulty buttons
    difficulty_buttons = {
        "easy": ttk.Button(
            selection_frame, text="EASY", style="EasyDefault.TButton",
            command=lambda: update_button_style(difficulty_var, difficulty_buttons, difficulty_styles)
        ),
        "medium": ttk.Button(
            selection_frame, text="MEDIUM", style="MediumDefault.TButton",
            command=lambda: update_button_style(difficulty_var, difficulty_buttons, difficulty_styles)
        ),
        "hard": ttk.Button(
            selection_frame, text="HARD", style="HardDefault.TButton",
            command=lambda: update_button_style(difficulty_var, difficulty_buttons, difficulty_styles)
        )
    }

    # Place difficulty buttons
    difficulty_buttons["easy"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    difficulty_buttons["medium"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    difficulty_buttons["hard"].grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Color variable
    color_var = tk.StringVar(value="white")

    # Color buttons
    color_buttons = {
        "white": ttk.Button(
            selection_frame, text="WHITE", style="ColorDefault.TButton",
            command=lambda: update_button_style(color_var, color_buttons, color_styles)
        ),
        "black": ttk.Button(
            selection_frame, text="BLACK", style="ColorDefault.TButton",
            command=lambda: update_button_style(color_var, color_buttons, color_styles)
        )
    }

    # Place color buttons
    color_buttons["white"].grid(row=2, column=0, columnspan=1, padx=10, pady=10, sticky="nsew")
    color_buttons["black"].grid(row=2, column=2, columnspan=1, padx=10, pady=10, sticky="nsew")

    # Function for "Next" button command
    def handle_next():
        selected_difficulty = difficulty_var.get()
        selected_color = color_var.get()
        print(f"Selected Difficulty: {selected_difficulty}, Selected Color: {selected_color}")
        # Proceed to the next screen or function
        show_game_screen(root, selected_color, selected_difficulty)

    # Next Button
    next_button = ttk.Button(
        selection_frame,
        text="NEXT",
        style="Next.TButton",
        command=handle_next
    )
    style.configure("Next.TButton", font=("Ubuntu", 18, "bold"), foreground="white", background="#dc3545", padding=(BUTTON_PADX, BUTTON_PADY))
    style.map("Next.TButton", background=[("active", "#c82333")])
    next_button.grid(row=3, column=1, pady=20, sticky="nsew")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")  # Start app in fullscreen
    root.title("HVL Robotics Chess Robot")
    show_selection_screen(root)
    root.mainloop()
