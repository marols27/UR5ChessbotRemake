import tkinter as tk
from navigation import navigate_to_home
import os
import sys

class app():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('hvlChessRobot')
        self.root.geometry('800x600')
        navigate_to_home(self.root)
        self.root.mainloop()

if __name__ == '__main__':
    app()