import tkinter as tk
from tkinter import *
from avgui.avgui import Avgui

def main():
    root = Tk()
    avgui = Avgui(root)
    root.title("Artificial Vorzious Comparitor")
    root.mainloop()

if __name__ == "__main":
    main()