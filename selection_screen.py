import tkinter as tk
from tkinter import font as tkfont
from game_screen import show_game_screen
from Game import Game
import random
from playsound import playsound

def show_selection_screen(root, home_frame):
    home_frame.destroy()
    # Padding variables for easy adjustment
    BUTTON_PADX = 70
    BUTTON_PADY = 40

    playsound("speechfiles/welcome.mp3")

    # Function to update button colors when selected
    def update_button_color(var, buttons):
        for value, button in buttons.items():
            if var.get() == value:
                if value == "easy":
                    button.config(bg="green", fg="white")
                    #playsound("speechfiles/easy.mp3")
                elif value == "medium":
                    button.config(bg="yellow", fg="black")
                    #playsound("speechfiles/medium.mp3")
                elif value == "hard":
                    button.config(bg="red", fg="white")
                    #playsound("speechfiles/hard.mp3")
            else:
                button.config(bg="#1a237e", fg="white")

    # Main Frame
    selection_frame = tk.Frame(root, bg="#1a237e")
    selection_frame.pack(fill="both", expand=True)
    
    # Configuring grid to be responsive
    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)
    selection_frame.grid_rowconfigure(0, weight=1)
    selection_frame.grid_rowconfigure(1, weight=4)
    selection_frame.grid_rowconfigure(2, weight=4)
    selection_frame.grid_rowconfigure(3, weight=4)
    selection_frame.grid_rowconfigure(4, weight=1)

    # Custom font
    title_font = tkfont.Font(family="Helvetica", size=30, weight="bold")
    button_font = tkfont.Font(family="Helvetica", size=30, weight="bold")

    # Difficulty Section
    difficulty_label = tk.Label(selection_frame, text="Choose Difficulty", font=title_font, fg="white", bg="#1a237e")
    difficulty_label.grid(row=0, column=0, pady=10, sticky="s")

    difficulty_var = tk.StringVar(value="easy")
    
    # Difficulty Buttons
    difficulty_buttons = {
        "easy": tk.Radiobutton(
            selection_frame, text="EASY", variable=difficulty_var, value="easy",
            font=button_font, fg="white", bg="#1a237e", indicatoron=0, padx=BUTTON_PADX, pady=BUTTON_PADY, borderwidth=5, relief="solid",
            command=lambda: update_button_color(difficulty_var, difficulty_buttons)
        ),
        "medium": tk.Radiobutton(
            selection_frame, text="MEDIUM", variable=difficulty_var, value="medium",
            font=button_font, fg="white", bg="#1a237e", indicatoron=0, padx=BUTTON_PADX, pady=BUTTON_PADY, borderwidth=5, relief="solid",
            command=lambda: update_button_color(difficulty_var, difficulty_buttons)
        ),
        "hard": tk.Radiobutton(
            selection_frame, text="HARD", variable=difficulty_var, value="hard",
            font=button_font, fg="white", bg="#1a237e", indicatoron=0, padx=BUTTON_PADX, pady=BUTTON_PADY, borderwidth=5, relief="solid",
            command=lambda: update_button_color(difficulty_var, difficulty_buttons)
        )
    }

    difficulty_buttons["easy"].grid(row=1, column=0, sticky="n")
    difficulty_buttons["medium"].grid(row=1, column=1, sticky="n")
    difficulty_buttons["hard"].grid(row=1, column=2, sticky="n")

    def handle_next():
        
        show_game_screen(root, selection_frame, "black" ,difficulty_var.get())
    # Next Button
    next_button = tk.Button(
        selection_frame, 
        text="NEXT", 
        command=lambda: handle_next(),
        font=button_font, 
        fg="white", 
        bg="#dc3545",        # Set background color to #dc3545
        activebackground="#c82333",  # Set active background to a slightly darker shade
        padx=BUTTON_PADX, 
        pady=BUTTON_PADY, 
        borderwidth=0, 
        relief="solid"
    )
    next_button.grid(row=2, column=1, pady=20, sticky="se")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    selection_frame.grid(sticky="nsew")

    # Initial color setup
    update_button_color(difficulty_var, difficulty_buttons)