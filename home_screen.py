import customtkinter as ctk
from navigation import navigate_to_selection, navigate_to_calibration
from PIL import Image

def show_home_screen(root):
    root.attributes('-fullscreen', True)

    for widget in root.winfo_children():
        widget.destroy()

    # Configure appearance and theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Shared button styling constants
    BUTTON_HEIGHT = 120
    BUTTON_FONT = ctk.CTkFont(size=36, weight="bold")
    CORNER_RADIUS = 40
    BORDER_COLOR = "white"
    BORDER_WIDTH = 10
    FG_COLOR_DEFAULT = "#252525"
    TEXT_COLOR_DEFAULT = "white"

    # Main Frame
    home_frame = ctk.CTkFrame(root, corner_radius=10)
    home_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Grid layout configuration
    home_frame.grid_rowconfigure(0, weight=0)  # Title and Image section
    home_frame.grid_rowconfigure(1, weight=0)  # Buttons section
    home_frame.grid_columnconfigure(0, weight=1)
    home_frame.grid_columnconfigure(1, weight=1)
    
    # LEFT SECTION (Title and Subtitle)
    left_frame = ctk.CTkFrame(home_frame, corner_radius=10)
    left_frame.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))
    
    welcome_label = ctk.CTkLabel(
        left_frame, 
        text="The HVL Robotics Chess Robot", 
        anchor="w",
        font=ctk.CTkFont(size=52, weight="bold")
    )
    welcome_label.pack()

    subtitle_text = '''
        Challenge the HVL Robotics chess robot.
        Developed by students, funded by teknoløftet

        READ THIS BEFORE PLAYING:

        1. Press the "Play Game" button to get started.
        2. Choose the difficulty level and a color to play as.
        3. Press confirm move after making a move.
        4. The robot will make its move after you confirm yours.
        5. Let the robot finish its move before making your next move.
        '''


    subtitle_label = ctk.CTkLabel(
        left_frame, 
        text=subtitle_text,
        anchor="w",
        font=ctk.CTkFont(size=40)
    )
    subtitle_label.pack(pady=(0, 10))

    # RIGHT SECTION (Image)
    right_frame = ctk.CTkFrame(home_frame, corner_radius=10)
    right_frame.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(10, 10))

    robotics_logo = ctk.CTkImage(Image.open("assets/images/robotics_logo.jpg"), size=(500, 500))
    logo_label = ctk.CTkLabel(right_frame, image=robotics_logo)
    logo_label.pack(pady=(0, 0))
    
    # BUTTONS SECTION
    buttons_frame = ctk.CTkFrame(home_frame, corner_radius=10)
    buttons_frame.grid(row=1, column=0, columnspan=3, pady=(100, 10), sticky="w")

    # Configure grid for buttons
    for i in range(3):
        buttons_frame.grid_columnconfigure(i, weight=1, uniform="buttons")

    # Start Button
    play_button = ctk.CTkButton(
        buttons_frame, 
        text="Play Game", 
        font=BUTTON_FONT,
        text_color="black",
        fg_color="#00cdac",
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_COLOR,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT,
        hover=False,
        command=lambda: navigate_to_selection(root)
    )
    play_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

    # Configure Robot Button
    configure_robot_button = ctk.CTkButton(
        buttons_frame, 
        text="Configure Robot", 
        font=BUTTON_FONT,
        text_color=TEXT_COLOR_DEFAULT,
        fg_color=FG_COLOR_DEFAULT,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_COLOR,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT,
        hover=False,
        command=lambda: navigate_to_calibration(root)
    )
    configure_robot_button.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

    # Exit Button
    exit_button = ctk.CTkButton(
        buttons_frame, 
        text="Exit", 
        font=BUTTON_FONT,
        text_color=TEXT_COLOR_DEFAULT,
        fg_color=FG_COLOR_DEFAULT,
        corner_radius=CORNER_RADIUS,
        border_color=BORDER_COLOR,
        border_width=BORDER_WIDTH,
        height=BUTTON_HEIGHT,
        hover=False,
        command=root.destroy
    )
    exit_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
