# navigation.py
def navigate_to_home(root):
    from home_screen import show_home_screen
    show_home_screen(root)

def navigate_to_selection(root):
    from selection_screen import show_selection_screen
    show_selection_screen(root)

def navigate_to_calibration(root):
    from calibration_screen import show_calibration_screen
    show_calibration_screen(root)
def navigate_to_game(root, color, difficulty):
    from game_screen import show_game_screen
    show_game_screen(root, color, difficulty)