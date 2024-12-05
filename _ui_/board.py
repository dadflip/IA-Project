from matplotlib import colors
from tkinter import messagebox
from _ui_.config import Config
from constants import BOARD_COLS, BOARD_ROWS, PIECES


class Board(Config):
    """
    Represents the game board with features such as piece selection, rotation, mirroring, 
    color blending, and board reset. This class provides the user interface for interacting
    with the game board and managing the game state.
    """

    def __init__(self):
        """
        Initializes the Board, setting up the user interface and initial game state.
        """
        super().__init__()
        self.initial_colors = {}  # Stores the initial colors of cells for undo operations
        self.selected_piece = None  # Currently selected piece
        self.preview_piece = None  # Preview of the piece being placed
        self.pieces_available = {name: True for name in PIECES}  # Tracks available pieces
        self.pieces_on_the_grid = {name: False for name in PIECES}  # Tracks placed pieces

    def name_to_rgb(self, color_name):
        """
        Converts a color name to an RGB tuple in the 0-255 range.

        Args:
            color_name (str): The name of the color.

        Returns:
            tuple: The RGB values as integers in the range 0-255.
        """
        try:
            rgb = colors.to_rgb(color_name)  # Converts to RGB (0-1 range)
            return tuple(int(c * 255) for c in rgb)  # Scale to 0-255 range
        except ValueError:
            print(f"Color '{color_name}' not recognized.")
            return (0, 0, 0)  # Defaults to black if color is invalid

    def save_initial_colors(self):
        """
        Saves the current colors of all cells on the board to enable undo functionality.
        """
        self.initial_colors = {
            (row, col): self.canvas.itemcget(self.circles[row][col], "fill")
            for row in range(BOARD_ROWS) for col in range(BOARD_COLS)
        }

    def blend_colors(self, color1_name, color2_name, alpha):
        """
        Blends two colors based on the specified transparency factor (alpha).

        Args:
            color1_name (str): The name of the first color.
            color2_name (str): The name of the second color.
            alpha (float): Transparency factor for blending, in the range 0-1.

        Returns:
            str: The resulting blended color in hexadecimal format.
        """
        color1 = self.name_to_rgb(color1_name)
        color2 = self.name_to_rgb(color2_name)

        # Blend the RGB components
        blended_color = tuple(
            int(c1 * (1 - alpha) + c2 * alpha) for c1, c2 in zip(color1, color2)
        )

        # Convert to hexadecimal color string
        return f'#{blended_color[0]:02x}{blended_color[1]:02x}{blended_color[2]:02x}'

    def undo_color_blend(self):
        """
        Restores the board to its initial colors, undoing any color modifications.
        """
        if not self.initial_colors:
            messagebox.showwarning("Error", "No modifications to undo.")
            return

        for (row, col), color in self.initial_colors.items():
            self.canvas.itemconfig(self.circles[row][col], fill=color)

    def reset_board(self):
        """
        Resets the board to its initial state. All cells are set to white, and the
        game state is cleared.
        """
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                self.canvas.itemconfig(self.circles[row][col], fill="white")

        # Reset game state
        self.selected_piece = None
        self.preview_piece = None
        self.pieces_available = {name: True for name in PIECES}
        self.pieces_on_the_grid = {name: False for name in PIECES}
        self.reset_piece_previews()