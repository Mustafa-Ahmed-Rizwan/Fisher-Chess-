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
    SCREEN_SIZE = "700x500"  # Increased width slightly, height more

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
    
    # Create canvas for background and border
    canvas = tk.Canvas(root, width=550, height=400, bg=WINDOW_BG_START, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Store references to widgets that need to be hidden/shown
    radio_buttons = []
    theme_menu = None
    
    def show_about_page():
        """Show the about Chess960 page"""
        canvas.delete("all")
        
        # Hide radio buttons and dropdown
        for radio in radio_buttons:
            radio.place_forget()
        if theme_menu:
            theme_menu.place_forget()
        
        # Draw faint chessboard grid with larger squares
        for i in range(0, 700, 100):
            for j in range(0, 500, 100):
                color = CHESS_SQUARE_LIGHT if (i // 100 + j // 100) % 2 == 0 else CHESS_SQUARE_DARK
                canvas.create_rectangle(i, j, i + 100, j + 100, fill=color, outline="", width=0)
        
        # Draw double-lined border with adjusted dimensions
        canvas.create_rectangle(5, 5, 695, 495, outline=BORDER_COLOR, width=2)
        canvas.create_rectangle(7, 7, 693, 493, outline=BORDER_COLOR, width=2)
        
        # Title with adjusted position
        canvas.create_text(350, 50, text="About Chess960", 
                          font=("Times", 24, "bold"), fill=TEXT_COLOR)
        
        # About text with adjusted position and larger font
        canvas.create_text(
    350, 110,
    text="Chess960 (also called Fischer Random Chess) is a variant of chess\n"
         "invented by former world champion Bobby Fischer.",
    font=("Times", 14), fill=TEXT_COLOR, justify=tk.CENTER
)

# "Key Rules:" centered
        canvas.create_text(
            350, 160,
            text="Key Rules:",
            font=("Times", 15, "bold"), fill=TEXT_COLOR, justify=tk.CENTER
        )

        # Numbered rules, left-aligned
        rules_text = (
            "1. The back row pieces are shuffled randomly at the start\n"
            "2. Bishops must be on opposite colors\n"
            "3. The king must be between the rooks (for castling)\n"
            "4. All other standard chess rules apply"
        )
        canvas.create_text(
            350, 185,  # This is the top of the rules block
            text=rules_text,
            font=("Times", 14), fill=TEXT_COLOR, justify=tk.LEFT, anchor="n"
        )

        # Centered outro - moved further down to avoid overlap
        canvas.create_text(
            350, 320,  # <-- Increased from 280 to 320
            text="The starting position must be one of 960 possible positions,\n"
                 "hence the name Chess960. This eliminates memorized openings\n"
                 "and emphasizes creativity and understanding.",
            font=("Times", 14), fill=TEXT_COLOR, justify=tk.CENTER
        )
                
                # Back button with adjusted position
        back_button_rect = canvas.create_rectangle(275, 400, 425, 450, fill=BUTTON_FILL, outline=BORDER_COLOR, width=2)
        back_button_text = canvas.create_text(350, 425, text="Back to Menu", 
                                                    font=("Times", 14), fill=TEXT_COLOR)
        
        def on_back():
            """Return to main menu"""
            show_main_menu()
        
        def on_enter_back(e):
            canvas.itemconfig(back_button_rect, fill=BUTTON_HOVER)
        
        def on_leave_back(e):
            canvas.itemconfig(back_button_rect, fill=BUTTON_FILL)
        
        canvas.tag_bind(back_button_text, "<Button-1>", lambda e: on_back())
        canvas.tag_bind(back_button_rect, "<Button-1>", lambda e: on_back())
        canvas.tag_bind(back_button_text, "<Enter>", on_enter_back)
        canvas.tag_bind(back_button_rect, "<Enter>", on_enter_back)
        canvas.tag_bind(back_button_text, "<Leave>", on_leave_back)
        canvas.tag_bind(back_button_rect, "<Leave>", on_leave_back)
    
    def show_main_menu():
        """Show the main menu page"""
        nonlocal theme_menu

        canvas.delete("all")

        # Draw faint chessboard grid with 100x100 squares
        chess_squares = []
        for i in range(0, 700, 100):  # Changed from 550 to 700
            for j in range(0, 500, 100):  # Changed from 400 to 500
                color = CHESS_SQUARE_LIGHT if (i // 100 + j // 100) % 2 == 0 else CHESS_SQUARE_DARK
                square = canvas.create_rectangle(i, j, i + 100, j + 100, fill=color, outline="", width=0)
                chess_squares.append(square)

        # Draw double-lined border with new dimensions
        border1 = canvas.create_rectangle(5, 5, 695, 495, outline=BORDER_COLOR, width=2)
        border2 = canvas.create_rectangle(7, 7, 693, 493, outline=BORDER_COLOR, width=2)

        # Title, centered at new position
        title = canvas.create_text(350, 60, text="Chess960 (Fischer Random Chess)", 
                                   font=("Times", 24, "bold"), fill=TEXT_COLOR)

        # Play As Label and Radio Buttons, centered with new positions
        play_as_label = canvas.create_text(350, 130, text="Play As:", 
                                           font=("Times", 18, "bold"), fill=TEXT_COLOR)

        color_var = tk.IntVar(value=2)  # Default: Random

        # Clear previous radio buttons (if any) and recreate
        for radio in radio_buttons:
            radio.destroy()
        radio_buttons.clear()

        # Create radio buttons with new positions
        white_radio = tk.Radiobutton(root, text="White", variable=color_var, value=0, 
                                     font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        black_radio = tk.Radiobutton(root, text="Black", variable=color_var, value=1, 
                                     font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)
        random_radio = tk.Radiobutton(root, text="Random", variable=color_var, value=2, 
                                      font=("Times", 15), bg=WINDOW_BG_START, selectcolor=WINDOW_BG_START)

        radio_buttons.extend([white_radio, black_radio, random_radio])

        # Place radio buttons at new positions
        white_radio.place(x=225, y=160)
        black_radio.place(x=325, y=160)
        random_radio.place(x=425, y=160)

        # Board Theme Label and Dropdown with new positions
        theme_label = canvas.create_text(350, 230, text="Board Theme:", 
                                         font=("Times", 18, "bold"), fill=TEXT_COLOR)

        if theme_menu is None:
            theme_list = ["blue", "bw", "green", "wood", "purple"]
            theme_menu = ttk.Combobox(root, values=theme_list, state="readonly", font=("Times", 15))
            theme_menu.set("blue")
        theme_menu.place(x=275, y=250, width=150)  # Centered, wider dropdown
        
        # Start Game Button, centered
        def getValues():
            nonlocal humanWhite, humanBlack, theme
            color = randrange(2) if color_var.get() == 2 else color_var.get()
            humanWhite, humanBlack = (color == 0), (color == 1)
            theme = theme_menu.get()
            # Clean up canvas items before destroying window
            canvas.delete("all")
            # Hide widgets
            for radio in radio_buttons:
                radio.place_forget()
            theme_menu.place_forget()
            root.destroy()
        
        def on_enter(e):
            canvas.itemconfig(start_button_rect, fill=BUTTON_HOVER)
        
        def on_leave(e):
            canvas.itemconfig(start_button_rect, fill=BUTTON_FILL)
        
        start_button_rect = canvas.create_rectangle(200, 300, 500, 350, 
                                          fill=BUTTON_FILL, 
                                          outline=BORDER_COLOR, 
                                          width=2)  # Increased width to 300px
        start_button_text = canvas.create_text(350, 325, 
                                            text="Start Chess960 Game!", 
                                            font=("Times", 18, "bold"),  # Increased font size
                                            fill=TEXT_COLOR)

        # About Button - keep same width as Start button
        about_button_rect = canvas.create_rectangle(200, 370, 500, 420, 
                                                fill=BUTTON_FILL, 
                                                outline=BORDER_COLOR, 
                                                width=2)
        about_button_text = canvas.create_text(350, 395, 
                                            text="About Chess960", 
                                            font=("Times", 18, "bold"),  # Match font size
                                            fill=TEXT_COLOR)
        
        def on_enter_about(e):
            canvas.itemconfig(about_button_rect, fill=BUTTON_HOVER)
        
        def on_leave_about(e):
            canvas.itemconfig(about_button_rect, fill=BUTTON_FILL)
        
        canvas.tag_bind(about_button_text, "<Button-1>", lambda e: show_about_page())
        canvas.tag_bind(about_button_rect, "<Button-1>", lambda e: show_about_page())
        canvas.tag_bind(about_button_text, "<Enter>", on_enter_about)
        canvas.tag_bind(about_button_rect, "<Enter>", on_enter_about)
        canvas.tag_bind(about_button_text, "<Leave>", on_leave_about)
        canvas.tag_bind(about_button_rect, "<Leave>", on_leave_about)
        
        # Store canvas items in a list
        canvas_items = [title, play_as_label, theme_label, start_button_rect, 
                       start_button_text, about_button_rect, about_button_text, 
                       border1, border2]
        canvas_items.extend(chess_squares)
        
        canvas.tag_bind(start_button_text, "<Button-1>", lambda e: getValues())
        canvas.tag_bind(start_button_rect, "<Button-1>", lambda e: getValues())
        canvas.tag_bind(start_button_text, "<Enter>", on_enter)
        canvas.tag_bind(start_button_rect, "<Enter>", on_enter)
        canvas.tag_bind(start_button_text, "<Leave>", on_leave)
        canvas.tag_bind(start_button_rect, "<Leave>", on_leave)
    
    humanWhite = humanBlack = theme = None
    show_main_menu()
    root.mainloop()
    
    # After mainloop exits (via "Start Game" button), return the selected values
    return (humanWhite, humanBlack, theme)