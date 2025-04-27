# -*- coding: utf-8 -*-
"""
Chess960 Game Menu - Modified for Fischer Random Chess
"""

import tkinter as tk
from tkinter import ttk
from random import randrange

def mainMenu():
    """
    Displays startup menu for Chess960 game (Human vs Computer only).
    Returns:
        tuple: (humanWhite, humanBlack, theme_name)
    """
    WINDOW_TITLE = "Chess960 Settings"
    WINDOW_BG = "#5285b4"
    TEXT_COLOR = "#f5f5f5"
    SCREEN_SIZE = "500x300"
    
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(WINDOW_TITLE)
    root.configure(bg=WINDOW_BG)
    
    # Title Label
    tk.Label(
        root, text="Chess960 (Fischer Random Chess)", 
        font="Helvetica 20 bold", bg=WINDOW_BG, fg=TEXT_COLOR
    ).pack(pady=10)

    # Player Color Selection
    tk.Label(
        root, text="Play As:", font="Helvetica 14 bold", 
        bg=WINDOW_BG, fg=TEXT_COLOR
    ).place(x=20, y=60)
    
    color_var = tk.IntVar(value=2)  # Default: Random
    tk.Radiobutton(
        root, text="White", font="Helvetica 14",
        variable=color_var, value=0, bg=WINDOW_BG
    ).place(x=200, y=60)
    tk.Radiobutton(
        root, text="Black", font="Helvetica 14",
        variable=color_var, value=1, bg=WINDOW_BG
    ).place(x=300, y=60)
    tk.Radiobutton(
        root, text="Random", font="Helvetica 14",
        variable=color_var, value=2, bg=WINDOW_BG
    ).place(x=400, y=60)

    # Theme Selection
    tk.Label(
        root, text="Board Theme:", font="Helvetica 14 bold", 
        bg=WINDOW_BG, fg=TEXT_COLOR
    ).place(x=20, y=100)
    
    theme_list = ["blue", "bw", "yellow", "green", "wood", "purple"]
    theme_menu = ttk.Combobox(
        root, values=theme_list, state="readonly", font="Helvetica 14"
    )
    theme_menu.set("blue")  # Default theme
    theme_menu.place(x=200, y=100, width=150)

    # Game Start Button
    def getValues():
        nonlocal humanWhite, humanBlack, theme
        # Human vs Computer: Set human player based on color choice
        color = randrange(2) if color_var.get() == 2 else color_var.get()
        humanWhite, humanBlack = (color == 0), (color == 1)
        
        theme = theme_menu.get()
        root.destroy()

    humanWhite = humanBlack = theme = None
    
    tk.Button(
        root, text="Start Chess960 Game!", font="Helvetica 15 bold",
        fg="#222", bg="#EEE", padx=2, command=getValues
    ).place(x=150, y=180)

    root.mainloop()
    return (humanWhite, humanBlack, theme)