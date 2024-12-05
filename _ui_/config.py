import tkinter as tk
from tkinter import ttk
from constants import BOARD_COLS, BOARD_ROWS, CELL_PADDING, CELL_RADIUS, PIECE_COLORS, PIECES


class Config(tk.Tk):
    """
    A configuration class that extends the Tkinter `Tk` class to create the main application window. 
    It includes a grid of circles representing the game board and provides functionality for handling 
    user interactions and tracking the game state.
    """

    def __init__(self):
        """
        Initializes the main application window with a title, size, and canvas for the game board.
        Sets up the game state, including board grid, piece states, and user interaction variables.
        """
        super().__init__()

        # Window settings
        self.title("IQ Puzzler Pro XXL")
        self.geometry(f"{BOARD_COLS * (CELL_RADIUS * 2 + CELL_PADDING)}x"
                      f"{(BOARD_ROWS + 2) * (CELL_RADIUS * 2 + CELL_PADDING)}")

        # Initialize game state variables
        self.initial_colors = {}  # Tracks initial cell colors for undo functionality
        self.board_state = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]  # Grid state
        self.initial_board_state = self.board_state
        self.piece_states = {name: {'rotation': 0, 'symmetry': False} for name in PIECES.keys()}  # Piece states
        self.pieces_available = {name: True for name in PIECES}  # Tracks available pieces
        self.pieces_on_the_grid = {}  # Tracks pieces placed on the grid
        self.selected_piece = None  # Currently selected piece
        self.preview_piece = None  # Piece preview for placement
        self.piece_canvases = {}  # Dictionary for managing piece visuals

        # Create the game board canvas
        self.canvas = tk.Canvas(
            self,
            width=BOARD_COLS * (CELL_RADIUS * 2 + CELL_PADDING),
            height=BOARD_ROWS * (CELL_RADIUS * 2 + CELL_PADDING),
            bd=0
        )
        self.canvas.pack(padx=20, pady=20)

        # Initialize the circles grid
        self.circles = []
        self._create_board()

    def _create_board(self):
        """
        Creates the game board by rendering a grid of circles on the canvas. Each circle 
        represents a cell, and click events are bound to enable user interaction.
        """
        for row in range(BOARD_ROWS):
            row_circles = []  # List to store circles in the current row
            for col in range(BOARD_COLS):
                # Calculate circle dimensions
                x0 = col * (CELL_RADIUS * 2 + CELL_PADDING) + CELL_PADDING
                y0 = row * (CELL_RADIUS * 2 + CELL_PADDING) + CELL_PADDING
                x1 = x0 + CELL_RADIUS * 2
                y1 = y0 + CELL_RADIUS * 2

                # Create a circle and add it to the canvas
                circle = self.canvas.create_oval(x0, y0, x1, y1, fill="white", outline="#fff")

                # Bind a click event to the circle
                self.canvas.tag_bind(circle, "<Button-1>", lambda e, r=row, c=col: self.cell_click(r, c))

                # Store the circle in the row list
                row_circles.append(circle)

            # Append the row circles to the main circles grid
            self.circles.append(row_circles)
            
    