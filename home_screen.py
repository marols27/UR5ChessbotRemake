import customtkinter as ctk
from selection_screen import show_selection_screen
from PoseConfigure import PoseConfigure
import Settings

def show_home_screen(root):
    root.attributes('-fullscreen', True)

    for widget in root.winfo_children():
        widget.destroy()

    # Configure appearance and theme
    ctk.set_appearance_mode("dark")  # Dark mode
    ctk.set_default_color_theme("blue")  # Default theme

    pose = PoseConfigure()

    # Create the main frame with a dark background
    home_frame = ctk.CTkFrame(root, corner_radius=10)
    home_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Welcome label with large, bold text
    welcome_label = ctk.CTkLabel(
        home_frame, 
        text="The HVL Robotics Chess Robot", 
        font=ctk.CTkFont(size=48, weight="bold")
    )
    welcome_label.place(relx=0.5, rely=0.2, anchor="center")

    # Subtitle label with medium-sized text
    subtitle_label = ctk.CTkLabel(
        home_frame, 
        text="Challenge the HVL Robotics chess robot.\nDeveloped by students, funded by teknoløftet", 
        font=ctk.CTkFont(size=24)
    )
    subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

    # Button frame to align buttons horizontally
    buttons_frame = ctk.CTkFrame(home_frame, corner_radius=10)
    buttons_frame.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.8, relheight=0.1)

    # Add buttons with correct spacing
    total_buttons = 3  # Number of buttons
    button_spacing = 0.05  # Relative spacing between buttons
    button_width = (1.0 - (button_spacing * (total_buttons - 1))) / total_buttons  # Calculate button width

    # Start Game button
    start_button = ctk.CTkButton(
        buttons_frame, 
        text="Start Game", 
        font=ctk.CTkFont(size=24, weight="bold"),
        command=lambda: show_selection_screen(root)
    )
    start_button.place(relx=0, rely=0.1, relwidth=button_width, relheight=0.8)

    # Configure Robot button
    configure_robot_button = ctk.CTkButton(
        buttons_frame,
        text="Configure Robot",
        font=ctk.CTkFont(size=24, weight="bold"),
        command=lambda: pose.firstTimeSettup(connectionIP=Settings.CONNECTION_IP)
    )
    configure_robot_button.place(relx=button_width + button_spacing, rely=0.1, relwidth=button_width, relheight=0.8)

    # Exit button
    exit_button = ctk.CTkButton(
        buttons_frame, 
        text="Exit", 
        font=ctk.CTkFont(size=24, weight="bold"),
        command=root.quit
    )
    exit_button.place(relx=2 * (button_width + button_spacing), rely=0.1, relwidth=button_width, relheight=0.8)
