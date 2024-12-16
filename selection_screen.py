import customtkinter as ctk
import navigation

def show_selection_screen(root):
    # Destroy any existing frames
    for widget in root.winfo_children():
        widget.destroy()

    # Common button dimensions
    BUTTON_HEIGHT = 150
    BUTTON_FONT = ctk.CTkFont(size=36, weight="bold")
    CORNER__RADIUS = 40
    BORDER_COLOR = "white"
    BORDER_WIDTH = 10
    FG_COLOR_DEFAULT = "#252525"
    TEXT_COLOR_DEFAULT = "white"

    # Function to update button styles when selected
    def update_button_style(selected_var, buttons, color):
        for value, button in buttons.items():
            if selected_var.get() == value:
                button.configure(fg_color=color)
                button.configure(border_color=color)
                if color in ["white", "yellow"]:  # Ensure text is visible on light backgrounds
                    button.configure(text_color="black")
                else:
                    button.configure(text_color="white")
            else:
                button.configure(fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, border_color=BORDER_COLOR)

    # Main Frame
    selection_frame = ctk.CTkFrame(root, corner_radius=10)
    selection_frame.pack(fill="both", padx=20, pady=20)

    # Configuring grid to be responsive
    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)
    selection_frame.grid_columnconfigure(2, weight=1)

    # Title label
    title_label = ctk.CTkLabel(
        selection_frame, text="Choose Difficulty", 
        font=ctk.CTkFont(size=72, weight="bold")
    )
    title_label.grid(row=0, column=0, columnspan=3, pady=40)

    # Difficulty variable
    difficulty_var = ctk.StringVar(value="easy")

    # Difficulty buttons
    difficulty_buttons = {
        "easy": ctk.CTkButton(
            selection_frame, text="EASY", fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, 
            corner_radius=CORNER__RADIUS, border_color=BORDER_COLOR, border_width=BORDER_WIDTH,
            font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
            command=lambda: [difficulty_var.set("easy"), update_button_style(difficulty_var, difficulty_buttons, "green")]
        ),
        "medium": ctk.CTkButton(
            selection_frame, text="MEDIUM", fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, 
            corner_radius=CORNER__RADIUS, border_color=BORDER_COLOR, border_width=BORDER_WIDTH,
            font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
            command=lambda: [difficulty_var.set("medium"), update_button_style(difficulty_var, difficulty_buttons, "yellow")]
        ),
        "hard": ctk.CTkButton(
            selection_frame, text="HARD", fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, 
            corner_radius=CORNER__RADIUS, border_color=BORDER_COLOR, border_width=BORDER_WIDTH,
            font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
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
            selection_frame, text="WHITE", fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, 
            corner_radius=CORNER__RADIUS, border_color=BORDER_COLOR, border_width=BORDER_WIDTH,
            font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
            command=lambda: [color_var.set("white"), update_button_style(color_var, color_buttons, "white")]
        ),
        "black": ctk.CTkButton(
            selection_frame, text="BLACK", fg_color=FG_COLOR_DEFAULT, text_color=TEXT_COLOR_DEFAULT, 
            corner_radius=CORNER__RADIUS, border_color=BORDER_COLOR, border_width=BORDER_WIDTH,
            font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
            command=lambda: [color_var.set("black"), update_button_style(color_var, color_buttons, "black")]
        )
    }

    # Label for Color Section
    color_label = ctk.CTkLabel(
        selection_frame, text="Choose Color", 
        font=ctk.CTkFont(size=72, weight="bold")
    )
    color_label.grid(row=2, column=0, columnspan=3, pady=40)

    # Place color buttons
    color_buttons["white"].grid(row=3, column=0, padx=10, pady=50, sticky="nsew")
    color_buttons["black"].grid(row=3, column=1, padx=10, pady=50, sticky="nsew")

    # Function for "Next" button command
    def handle_next():
        selected_difficulty = difficulty_var.get()
        selected_color = color_var.get()
        print(f"Selected Difficulty: {selected_difficulty}, Selected Color: {selected_color}")
        navigation.navigate_to_game(root, selected_color, selected_difficulty)

    # Back Button
    back_button = ctk.CTkButton(
        
        selection_frame, text="BACK", text_color="white", fg_color="#ff6f68", 
        corner_radius=CORNER__RADIUS, border_color="black", border_width=BORDER_WIDTH,
        font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
        hover_color="#0056b3", command=lambda: navigation.navigate_to_home(root)
    )
    back_button.grid(row=5, column=0, pady=50, sticky="nsew")

    # Start Button
    start_button = ctk.CTkButton(
        selection_frame, text="START", text_color="white", fg_color="#00cdac", 
        corner_radius=CORNER__RADIUS, border_color="black", border_width=BORDER_WIDTH,
        font=BUTTON_FONT, height=BUTTON_HEIGHT, hover=False,
        hover_color="#c82333", command=handle_next,
    )
    start_button.grid(row=5, column=2, pady=50, sticky="nsew")

# Example usage
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Set the overall theme ("light" or "dark")
    ctk.set_default_color_theme("blue")  # Default theme
    root = ctk.CTk()
    root.geometry("800x600")  # Set window size
    root.title("HVL Robotics Chess Robot")
    show_selection_screen(root)
    root.mainloop()
