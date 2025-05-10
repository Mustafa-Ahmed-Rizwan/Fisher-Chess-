# -*- coding: utf-8 -*-
"""
Chess960 Game Menu - Modified for Fischer Random Chess with Vintage Theme
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
    WINDOW_BG_START = "#dec79b"
    WINDOW_BG_END = "#cdb279"
    CHESS_SQUARE_LIGHT = "#e8d3a4"
    CHESS_SQUARE_DARK = "#cba86f"
    TEXT_COLOR = "#3b2b1d"
    BORDER_COLOR = "#3b2b1d"
    BUTTON_FILL = "#f3e1b8"
    BUTTON_HOVER = "#e0d0a6"
    SCREEN_SIZE = "400x240"  # Reduced size to fit theme better
    
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(WINDOW_TITLE)
    
    try:
        # Create canvas for background and border
        canvas = tk.Canvas(root, width=400, height=240, bg=WINDOW_BG_START, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Draw faint chessboard grid with smaller scale
        chess_squares = []
        for i in range(0, 400, 80):  # Reduced grid size
            for j in range(0, 240, 80):
                color = CHESS_SQUARE_LIGHT if (i // 80 + j // 80) % 2 == 0 else CHESS_SQUARE_DARK
                square = canvas.create_rectangle(i, j, i + 80, j + 80, fill=color, outline="", width=0)
                chess_squares.append(square)
        
        # Draw double-lined border
        border1 = canvas.create_rectangle(5, 5, 395, 235, outline=BORDER_COLOR, width=2)
        border2 = canvas.create_rectangle(7, 7, 393, 233, outline=BORDER_COLOR, width=2)
        
        # Title with smaller font and shifted right
        title = canvas.create_text(180, 30, text="Chess960 (Fischer Random Chess)", 
                                  font=("Times", 16, "bold"), fill=TEXT_COLOR)
        
        # Play As Label and Radio Buttons with smaller font
        play_as_label = canvas.create_text(40, 60, text="Play As:", 
                                           font=("Times", 12, "bold"), fill=TEXT_COLOR)
        
        color_var = tk.IntVar(value=2)  # Default: Random
        
        # Store radio buttons in a list to prevent garbage collection
        radio_buttons = []
        white_radio = tk.Radiobutton(root, text="White", variable=color_var, value=0, 
                                     font=("Times", 12), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        black_radio = tk.Radiobutton(root, text="Black", variable=color_var, value=1, 
                                     font=("Times", 12), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        random_radio = tk.Radiobutton(root, text="Random", variable=color_var, value=2, 
                                      font=("Times", 12), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        
        radio_buttons.extend([white_radio, black_radio, random_radio])
        
        white_radio.place(x=120, y=50)
        black_radio.place(x=200, y=50)
        random_radio.place(x=280, y=50)
        
        # Board Theme Label and Dropdown with smaller font and shifted right
        theme_label = canvas.create_text(60, 100, text="Board Theme:", 
                                        font=("Times", 12, "bold"), fill=TEXT_COLOR)
        theme_list = ["blue", "bw","green", "wood", "purple"]
        theme_menu = ttk.Combobox(root, values=theme_list, state="readonly", font=("Times", 12))
        theme_menu.set("blue")
        theme_menu.place(x=120, y=90, width=120)  # Adjusted position and width
        
        # Start Game Button with smaller font
        def getValues():
            nonlocal humanWhite, humanBlack, theme
            color = randrange(2) if color_var.get() == 2 else color_var.get()
            humanWhite, humanBlack = (color == 0), (color == 1)
            theme = theme_menu.get()
            # Clean up canvas items before destroying window
            canvas.delete("all")
            root.destroy()
        
        def on_enter(e):
            canvas.itemconfig(start_button_rect, fill=BUTTON_HOVER)
        
        def on_leave(e):
            canvas.itemconfig(start_button_rect, fill=BUTTON_FILL)
        
        start_button_rect = canvas.create_rectangle(120, 150, 280, 180, fill=BUTTON_FILL, outline=BORDER_COLOR, width=2)
        start_button_text = canvas.create_text(200, 165, text="Start Chess960 Game!", 
                                              font=("Times", 12), fill=TEXT_COLOR)
        
        # Store canvas items in a list
        canvas_items = [title, play_as_label, theme_label, start_button_rect, start_button_text, border1, border2]
        canvas_items.extend(chess_squares)
        
        canvas.tag_bind(start_button_text, "<Button-1>", lambda e: getValues())
        canvas.tag_bind(start_button_rect, "<Button-1>", lambda e: getValues())
        canvas.tag_bind(start_button_text, "<Enter>", on_enter)
        canvas.tag_bind(start_button_rect, "<Enter>", on_enter)
        canvas.tag_bind(start_button_text, "<Leave>", on_leave)
        canvas.tag_bind(start_button_rect, "<Leave>", on_leave)
        
        humanWhite = humanBlack = theme = None
        root.mainloop()
        
        return (humanWhite, humanBlack, theme)
        
    except Exception as e:
        print(f"Error in menu: {str(e)}")
        root.destroy()
        return (None, None, "blue")  # Return default values if error occurs