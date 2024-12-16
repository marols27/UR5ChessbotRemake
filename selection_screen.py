import customtkinter as ctk
import navigation
def show_selection_screen(root):
    # Destroy any existing frames
    for widget in root.winfo_children():
        widget.destroy()

    # Padding variables for easy adjustment
    BUTTON_PADX = 20
    BUTTON_PADY = 20

    # Function to update button styles when selected
    def update_button_style(selected_var, buttons, color):
        for value, button in buttons.items():
            if selected_var.get() == value:
                button.configure(fg_color=color)
                if(color == "white" or color == "yellow"):
                    button.configure(text_color="black")                
            else:
                button.configure(fg_color="grey", text_color="white")

    # Main Frame
    selection_frame = ctk.CTkFrame(root, corner_radius=10)
    selection_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Configuring grid to be responsive
    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)
    selection_frame.grid_columnconfigure(2, weight=1)

    # Title label
    title_label = ctk.CTkLabel(
        selection_frame, text="Choose Difficulty and Piece Color", 
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.grid(row=0, column=0, columnspan=3, pady=10)

    # Difficulty variable
    difficulty_var = ctk.StringVar(value="easy")

    # Difficulty buttons
    difficulty_buttons = {
        "easy": ctk.CTkButton(
            selection_frame, text="EASY", fg_color="grey", text_color="white", hover = False,
            font=ctk.CTkFont(size=36, weight="bold"),
            command=lambda: [difficulty_var.set("easy"), update_button_style(difficulty_var, difficulty_buttons, "green")]
        ),
        "medium": ctk.CTkButton(
            selection_frame, text="MEDIUM", fg_color="grey", text_color="white", hover=False,
            font=ctk.CTkFont(size=36, weight="bold"),
            command=lambda: [difficulty_var.set("medium"), update_button_style(difficulty_var, difficulty_buttons, "yellow")]
        ),
        "hard": ctk.CTkButton(
            selection_frame, text="HARD", fg_color="grey", text_color="white", hover=False,
            font=ctk.CTkFont(size=36, weight="bold"),
            command=lambda: [difficulty_var.set("hard"), update_button_style(difficulty_var, difficulty_buttons, "red")]
        )
    }

    # Place difficulty buttons
    difficulty_buttons["easy"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    difficulty_buttons["medium"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    difficulty_buttons["hard"].grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Color variable
    color_var = ctk.StringVar(value="white")

    # Color buttons
    color_buttons = {
        "white": ctk.CTkButton(
            selection_frame, text="WHITE", fg_color="grey", text_color="white", hover=False,
            font=ctk.CTkFont(size=36, weight="bold"),
            command=lambda: [color_var.set("white"), update_button_style(color_var, color_buttons, "white")]
        ),
        "black": ctk.CTkButton(
            selection_frame, text="BLACK", fg_color="grey", text_color="white", hover=False,
            font=ctk.CTkFont(size=36, weight="bold"),
            command=lambda: [color_var.set("black"), update_button_style(color_var, color_buttons, "black")]
        )
    }

    # Place color buttons
    color_buttons["white"].grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    color_buttons["black"].grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

    # Function for "Next" button command
    def handle_next():
        selected_difficulty = difficulty_var.get()
        selected_color = color_var.get()
        print(f"Selected Difficulty: {selected_difficulty}, Selected Color: {selected_color}")
        navigation.navigate_to_game(root, selected_color, selected_difficulty)

    # Next Button
    next_button = ctk.CTkButton(
        selection_frame, text="NEXT", fg_color="#dc3545", text_color="white",
        font=ctk.CTkFont(size=36, weight="bold"),
        hover_color="#c82333", command=handle_next
    )
    next_button.grid(row=3, column=1, pady=20, sticky="nsew")

# Example usage
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Set the overall theme ("light" or "dark")
    ctk.set_default_color_theme("blue")  # Default theme
    root = ctk.CTk()
    root.geometry("800x600")  # Set window size
    root.title("HVL Robotics Chess Robot")
    show_selection_screen(root)
    root.mainloop()
