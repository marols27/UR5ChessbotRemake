import tkinter as tk
from home_screen import show_home_screen

class GUI():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('hvlChessRobot')
        self.root.geometry('800x600')
        show_home_screen(self.root)
        self.root.mainloop()
        