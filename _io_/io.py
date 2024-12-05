from tkinter import messagebox
from _ui_.piece import PieceTransformation

class InputHandler(PieceTransformation):
    """
    Handles keyboard and mouse inputs, associating specific keys and mouse actions 
    with functions for piece manipulation.

    Inherits:
        PieceTransformation: Base class that provides methods for piece transformations 
        (e.g., rotation and mirroring).

    Attributes:
        piece_transformation (PieceTransformation): An instance of the PieceTransformation class.
        key_bindings (dict): A dictionary mapping key symbols to their corresponding functions.
    """

    def __init__(self, piece_transformation):
        """
        Initializes the InputHandler class.

        Args:
            piece_transformation (PieceTransformation): An instance of the PieceTransformation 
            class, used to manipulate pieces on the board.
        """
        self.piece_transformation = piece_transformation  # Reference to the instance of PieceTransformation

        # Dictionary mapping keyboard keys to transformation and movement methods
        self.key_bindings = {
            'r': self.piece_transformation.rotate_piece,  # 'R': Rotate the selected piece
            'space': self.piece_transformation.mirror_piece,  # 'Space': Mirror the selected piece
            'left': self.piece_transformation.move_left,  # 'Left Arrow': Move left
            'right': self.piece_transformation.move_right,  # 'Right Arrow': Move right
            'up': self.piece_transformation.move_up,  # 'Up Arrow': Move up
            'down': self.piece_transformation.move_down,  # 'Down Arrow': Move down
            'e': self.piece_transformation.next_piece,  # 'Tab': Select next piece
            'a': self.piece_transformation.previous_piece,  # 'Shift+Tab': Select previous piece
        }

    def on_key_press(self, event):
        """
        Handles key press events and executes the corresponding transformation.

        Args:
            event (tk.Event): The event triggered by a key press, containing information 
            about the pressed key.

        Behavior:
            - If the pressed key is in the `key_bindings` dictionary, the associated function 
              is called.
            - If the key is not mapped, a message box is displayed informing the user.
        """
        key = event.keysym.lower()  # Retrieve the pressed key symbol in lowercase
        if key in self.key_bindings:
            self.key_bindings[key]()
        else:
            messagebox.showinfo("Error", "No function assigned to this key.")

    def on_mouse_event(self, event):
        """
        Handles mouse events and executes the corresponding transformation.

        Args:
            event (tk.Event): The event triggered by mouse actions.
        """
        # Handle left-click (Button-1)
        if event.num == 1:  # Left click
            self.piece_transformation.rotate_piece()

        # Handle right-click (Button-3)
        elif event.num == 3:  # Right click
            self.piece_transformation.mirror_piece()

    def on_mouse_wheel(self, event):
        """
        Handles the mouse wheel event and rotates the piece.

        Args:
            event (tk.Event): The mouse wheel event containing delta values.
        """
        if event.delta > 0 or event.num == 4:  # Scroll up
            self.piece_transformation.rotate_piece()
        elif event.delta < 0 or event.num == 5:  # Scroll down
            self.piece_transformation.rotate_piece()

    def enable_input(self, root):
        """
        Activates input handling by binding key and mouse events to the application.

        Args:
            root (tk.Tk): The main application window.
        """
        # Bind keyboard events
        root.bind("<KeyPress>", self.on_key_press)

        # Bind mouse button events
        # root.bind("<Button-1>", self.on_mouse_event)  # Left click
        root.bind("<Button-3>", self.on_mouse_event)  # Right click

        # Bind mouse wheel events
        root.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows/macOS
        root.bind("<Button-4>", self.on_mouse_wheel)  # Scroll up (Linux)
        root.bind("<Button-5>", self.on_mouse_wheel)  # Scroll down (Linux)
