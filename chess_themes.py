# -*- coding: utf-8 -*-
"""
Color themes for Chess960 (Fischer Random Chess) board
Each theme contains colors for:
1. Light squares
2. Dark squares 
3. Light highlighted squares
4. Dark highlighted squares
5. Light last move squares
6. Dark last move squares
"""

themes = {
    'blue': (
        (214, 221, 229),  # Light squares
        (82, 133, 180),   # Dark squares
        (253, 187, 115),  # Light highlighted
        (255, 129, 45),   # Dark highlighted
        (116, 194, 229),  # Light last move
        (32, 154, 215),   # Dark last move
    ),
    
    'bw': (
        (255, 255, 255),  # Light squares (white)
        (100, 100, 100),  # Dark squares (gray)
        (140, 236, 146),  # Light highlighted
        (30, 183, 37),    # Dark highlighted
        (116, 194, 229),  # Light last move
        (32, 154, 215),   # Dark last move
    ),
    
    'green': (
        (232, 235, 239),  # Light squares
        (119, 153, 84),    # Dark squares
        (247, 247, 105),   # Light highlighted
        (247, 214, 61),    # Dark highlighted
        (255, 170, 66),    # Light last move
        (255, 132, 66),    # Dark last move
    ),
    
    'wood': (
        (210, 180, 140),   # Light squares (light wood)
        (139, 69, 19),     # Dark squares (dark wood)
        (255, 215, 0),     # Light highlighted (gold)
        (255, 165, 0),     # Dark highlighted (orange)
        (255, 200, 100),   # Light last move
        (255, 150, 50),    # Dark last move
    ),
    
    'purple': (
        (220, 208, 255),   # Light squares
        (138, 102, 204),   # Dark squares
        (255, 187, 187),   # Light highlighted
        (255, 119, 119),   # Dark highlighted
        (187, 221, 255),   # Light last move
        (102, 170, 255),   # Dark last move
    )
}