# -*- coding: utf-8 -*-
"""
Chess960 Game Menu - Modified for Fischer Random Chess with Vintage Theme
"""

import tkinter as tk
from tkinter import ttk
from random import randrange
import sys

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
    SCREEN_SIZE = "550x400"  # Increased width slightly, height more

    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(WINDOW_TITLE)
    
    # Make window non-resizable and disable maximize
    root.resizable(False, False)
    try:
        if sys.platform == 'win32':
            from ctypes import windll
            # Get window handle
            hwnd = windll.user32.GetParent(root.winfo_id())
            # Get current style
            style = windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
            # Remove maximize button but keep minimize
            style = style & ~0x10000  # Remove WS_MAXIMIZEBOX
            # Set new style
            windll.user32.SetWindowLongW(hwnd, -16, style)
    except:
        pass  # Fallback for non-Windows platforms

    # Handle window close event (clicking "X")
    def on_closing():
        root.destroy()
        sys.exit()  # Exit the program entirely when the window is closed

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Register the close event handler
    
    try:
        # Create canvas for background and border
        canvas = tk.Canvas(root, width=550, height=400, bg=WINDOW_BG_START, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Draw faint chessboard grid with 100x100 squares
        chess_squares = []
        for i in range(0, 550, 100):
            for j in range(0, 400, 100):
                color = CHESS_SQUARE_LIGHT if (i // 100 + j // 100) % 2 == 0 else CHESS_SQUARE_DARK
                square = canvas.create_rectangle(i, j, i + 100, j + 100, fill=color, outline="", width=0)
                chess_squares.append(square)
        
        # Draw double-lined border
        border1 = canvas.create_rectangle(5, 5, 545, 395, outline=BORDER_COLOR, width=2)
        border2 = canvas.create_rectangle(7, 7, 543, 393, outline=BORDER_COLOR, width=2)
        
        # Title, centered
        title = canvas.create_text(275, 50, text="Chess960 (Fischer Random Chess)", 
                                  font=("Times", 20, "bold"), fill=TEXT_COLOR)
        
        # Play As Label and Radio Buttons, centered
        # Play As Label and Radio Buttons, centered
        play_as_label = canvas.create_text(275, 100, text="Play As:", 
                                           font=("Times", 15, "bold"), fill=TEXT_COLOR)
        
        color_var = tk.IntVar(value=2)  # Default: Random
        
        # Store radio buttons in a list to prevent garbage collection
        radio_buttons = []
        white_radio = tk.Radiobutton(root, text="White", variable=color_var, value=0, 
                                     font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        black_radio = tk.Radiobutton(root, text="Black", variable=color_var, value=1, 
                                     font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        random_radio = tk.Radiobutton(root, text="Random", variable=color_var, value=2, 
                                      font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        
        radio_buttons.extend([white_radio, black_radio, random_radio])
        
        
        white_radio.place(x=150, y=130)    
        black_radio.place(x=250, y=130)    
        random_radio.place(x=350, y=130)   
        
        # Board Theme Label and Dropdown, centered
        theme_label = canvas.create_text(275, 190, text="Board Theme:", 
                                        font=("Times", 15, "bold"), fill=TEXT_COLOR)
        theme_list = ["blue", "bw", "green", "wood", "purple"]
        theme_menu = ttk.Combobox(root, values=theme_list, state="readonly", font=("Times", 15))
        theme_menu.set("blue")
        theme_menu.place(x=200, y=210, width=150)  # Centered, wider dropdown
        
        # Start Game Button, centered
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
        
        start_button_rect = canvas.create_rectangle(200, 260, 350, 310, fill=BUTTON_FILL, outline=BORDER_COLOR, width=2)
        start_button_text = canvas.create_text(275, 285, text="Start Chess960 Game!", 
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
        
        # After mainloop exits (via "Start Game" button), return the selected values
        return (humanWhite, humanBlack, theme)
        
    except Exception as e:
        print(f"Error in menu: {str(e)}")
        root.destroy()
        sys.exit()  # Exit the program on any error
        return (None, None, "blue")  # This line will never be reached due to sys.exit()