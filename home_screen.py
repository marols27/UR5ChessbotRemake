import tkinter as tk
from tkinter import ttk, font, messagebox
from selection_screen import show_selection_screen
from PoseConfigure import PoseConfigure
import Settings

def show_home_screen(root):
    # Set up style configurations
    style = ttk.Style()
    style.theme_use("clam")  # You can also try "alt", "default", or "classic"

    # Configure styles for the labels and buttons
    style.configure("Home.TLabel", font=("Ubuntu", 48, "bold"), foreground="white", background="#333333")
    style.configure("Subtitle.TLabel", font=("Ubuntu", 24), foreground="white", background="#333333")
    style.configure("TFrame", background="#333333")  # Dark background for frames
    style.configure("TButton", font=("Ubuntu", 24), foreground="#ffffff", background="#555555", padding=10)
    style.map("TButton",
              background=[("active", "#777777")],
              foreground=[("active", "#ffffff")])

    # Create the main frame with a dark background
    pose = PoseConfigure()
    home_frame = ttk.Frame(root, style="TFrame")
    home_frame.pack(fill="both", expand=True)

    # Welcome label with large, bold text
    welcome_label = ttk.Label(
        home_frame, 
        text="The HVL Robotics Chess Robot", 
        style="Home.TLabel"
    )
    welcome_label.place(relx=0.5, rely=0.2, anchor="center")

    # Subtitle label with medium-sized text
    subtitle_label = ttk.Label(
        home_frame, 
        text="Challenge the HVL Robotics chess robot.\nDeveloped by students, funded by teknoløftet", 
        style="Subtitle.TLabel"
    )
    subtitle_label.place(relx=0.5, rely=0.3, anchor="center")

    # Button frame to align buttons horizontally
    buttons_frame = ttk.Frame(home_frame, style="TFrame")
    buttons_frame.place(relx=0.5, rely=0.6, anchor="center")

    # Start Game button with modern styling
    start_button = ttk.Button(
        buttons_frame, 
        text="Start Game", 
        style="TButton",
        command=lambda: show_selection_screen(root, home_frame)
    )
    start_button.place(relx=0, rely=0, relwidth=0.3, relheight=1)

    # Configure Robot button
    configure_robot_button = ttk.Button(
        buttons_frame,
        text="Configure Robot",
        style="TButton",
        command=lambda: pose.firstTimeSettup(connectionIP=Settings.CONNECTION_IP)
    )
    configure_robot_button.place(relx=0.35, rely=0, relwidth=0.3, relheight=1)

    # Exit button
    exit_button = ttk.Button(
        buttons_frame, 
        text="Exit", 
        style="TButton",
        command=root.quit
    )
    exit_button.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

    # Ensure the buttons frame expands with the window
    buttons_frame.place(relwidth=0.8, relheight=0.1)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1920x1080")
    root.title("HVL Robotics Chess Robot")
    show_home_screen(root)
    root.mainloop()
