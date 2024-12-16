import customtkinter as ctk
from PoseConfigure import PoseConfigure
from navigation import navigate_to_home
import Settings

def show_calibration_screen(root):
    pose = None
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create main calibration frame
    calibration_frame = ctk.CTkFrame(root, corner_radius=10)
    calibration_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def calibrate_point(point):
        if pose is not None:
            pose.calibrate_point(point)
            Settings.update_config()
        else:
            print("PoseConfigure object not initialized!")

    def start_calibration():
        nonlocal pose
        pose = PoseConfigure()

        pose.start_teach_mode()

        # Frame for buttons
        cal_button_frame = ctk.CTkFrame(calibration_frame, corner_radius=10)
        cal_button_frame.pack(pady=20)

        # Buttons
        set_origin_button = ctk.CTkButton(
            cal_button_frame, text="Set Origin", font=ctk.CTkFont(size=26, weight="bold"), 
            command=lambda: pose.calibrate_point("origin")
        )
        set_x_axis_button = ctk.CTkButton(
            cal_button_frame, text="Set X Axis", font=ctk.CTkFont(size=26, weight="bold"), 
            command=lambda: calibrate_point("xAxis")
        )
        set_xy_plane_button = ctk.CTkButton(
            cal_button_frame, text="Set XY Plane", font=ctk.CTkFont(size=26, weight="bold"), 
            command=lambda: calibrate_point("xyPlane")
        )
        set_home_button = ctk.CTkButton(
            cal_button_frame, text="Set Home", font=ctk.CTkFont(size=26, weight="bold"), 
            command=lambda: calibrate_point("home")
        )
        set_drop_button = ctk.CTkButton(
            cal_button_frame, text="Set Drop", font=ctk.CTkFont(size=26, weight="bold"), 
            command=lambda: calibrate_point("drop")
        )

        # Add buttons to grid layout (horizontally aligned)
        set_origin_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        set_x_axis_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        set_xy_plane_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        set_home_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        set_drop_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        # Define function to navigate home
        def nav_home():
            pose.end_teach_mode()
            navigate_to_home(root)

        # Done button (on a separate row below, centered)
        done_button = ctk.CTkButton(
            cal_button_frame, text="Done", font=ctk.CTkFont(size=26, weight="bold"), 
            command=nav_home
        )
        done_button.grid(row=1, column=0, columnspan=5, pady=20)

    # Start Calibration button
    start_calibration_button = ctk.CTkButton(
        calibration_frame,
        text="Start Calibration",
        font=ctk.CTkFont(size=28, weight="bold"),
        command=start_calibration  # Pass the function reference, no parentheses
    )
    start_calibration_button.pack(pady=20)
