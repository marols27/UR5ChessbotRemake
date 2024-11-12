import tkinter as tk
from tkinter import ttk
from selection_screen import show_selection_screen
from PoseConfigure import PoseConfigure
import Settings

def show_home_screen(root):
    # Set up the main frame with a dark background
    pose = PoseConfigure()

    home_frame = tk.Frame(root, bg="#1a237e")
    home_frame.pack(fill="both", expand=True)

    # Welcome label with large, bold text
    welcome_label = tk.Label(
        home_frame, 
        text="The HVL Robotics Chess Robot", 
        font=("Helvetica", 32, "bold"), 
        fg="white", 
        bg="#1a237e"
    )
    welcome_label.place(relx=0.5, rely=0.2, anchor="center")

    # Subtitle label with medium-sized text
    subtitle_label = tk.Label(
        home_frame, 
        text="Challenge the HVL Robotics chess robot.\nDeveloped by students, funded by teknoløftet", 
        font=("Helvetica", 16), 
        fg="white", 
        bg="#1a237e"
    )
    subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

    # Button frame to align buttons horizontally
    buttons_frame = tk.Frame(home_frame, bg="#1a237e")
    buttons_frame.place(relx=0.5, rely=0.6, anchor="center")

    # Start Game button with modern styling
    start_button = tk.Button(
        buttons_frame, 
        text="Start Game", 
        font=("Helvetica", 14, "bold"), 
        bg="#ff5722", 
        fg="#252525", 
        activebackground="#e64a19", 
        activeforeground="white", 
        relief="flat",
        command=lambda: show_selection_screen(root, home_frame)
    )
    start_button.place(relx=0, rely=0, relwidth=0.4, relheight=1)

    configure_robot_button = tk.Button(
        buttons_frame,
        text="Configure Robot",
        font=("Helvetica", 14, "bold"),
        bg="#ff5722",
        fg="#252525",
        activebackground="#e64a19",
        activeforeground="white",
        relief="flat",
        command=lambda: pose.firstTimeSettup(connectionIP=Settings.CONNECTION_IP)
    )

    configure_robot_button.place(relx=0.5, rely=0, relwidth=0.4, relheight=1)

    # Exit button with modern styling
    exit_button = tk.Button(
        buttons_frame, 
        text="Exit", 
        font=("Helvetica", 14, "bold"), 
        bg="#1a237e", 
        fg="#252525", 
        activebackground="#1a237e", 
        activeforeground="white", 
        relief="solid", 
        borderwidth=2
    )
    #exit_button.place(relx=0.5, rely=0, relwidth=0.4, relheight=1)

    # Ensure the buttons frame expands with the window
    buttons_frame.place(relwidth=0.8, relheight=0.1)
