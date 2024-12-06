import tkinter as tk
from tkinter import messagebox

from constants import BOARD_COLS, BOARD_ROWS, CELL_PADDING, CELL_RADIUS, NOPE, PIECE_COLORS, PIECES
from _ui_.board import Board

class PieceHandler(Board):
    def __init__(self):
        """Initializes the PieceHandler, inheriting from the Board class."""
        super().__init__()

    def show_piece_preview(self, event):
        """
        Displays a preview of the selected piece at the mouse location.
        
        Args:
            event (tk.Event): The mouse event containing the mouse coordinates.
        """
        if not self.selected_piece:
            return

        # Calculate the row and column of the grid cell under the mouse cursor
        col = (event.x - CELL_PADDING) // (CELL_RADIUS * 2 + CELL_PADDING)
        row = (event.y - CELL_PADDING) // (CELL_RADIUS * 2 + CELL_PADDING)

        # Check if the calculated coordinates are within the board's bounds
        if row < 0 or row >= BOARD_ROWS or col < 0 or col >= BOARD_COLS:
            return

        # Clear any previous previews
        self.hide_piece_preview(self.selected_piece, False)

        # Display the piece preview if it can be placed in the current location
        piece = PIECES[self.selected_piece]
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    if row + r >= BOARD_ROWS or col + c >= BOARD_COLS:
                        # Out of bounds, print a message
                        print("Piece preview is out of bounds.")
                    else:
                        current_color = self.canvas.itemcget(self.circles[row + r][col + c], "fill")
                        if current_color == "white":
                            # Blend the preview piece with the empty cell
                            self.canvas.itemconfig(self.circles[row + r][col + c], 
                                                   fill=self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5))
                        if current_color in PIECE_COLORS:
                            # Show a "NOPE" message if the spot is already occupied by a piece
                            self.canvas.itemconfig(self.circles[row + r][col + c], 
                                                   fill=self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], 
                                                                          self.canvas.itemcget(self.circles[row + r][col + c], "fill"), 0.5))
                            NOPE.append(self.canvas.create_text(40 + 70 * (col + c), 40 + 70 * (row + r), 
                                                                text="NOPE", fill="white", font=('Helvetica', 12, 'bold')))

    def hide_piece_preview(self, piece_name, delete_all=True):
        """
        Hides the preview of the specified piece and restores the grid to its original state.
        
        Args:
            piece_name (str): The name of the piece to hide the preview for.
            delete_all (bool): Whether to delete all previews or just the specific one.
        """
        # Delete "NOPE" labels if present
        for id_nope in NOPE:
            self.canvas.delete(id_nope)

        # Delete the piece preview from the canvas
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            if delete_all:
                piece_canvas.delete("all")

        # Restore the original colors of the cells
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                current_color = self.canvas.itemcget(self.circles[r][c], "fill")
                if current_color == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                    self.canvas.itemconfig(self.circles[r][c], fill="white")
                for piece_color in PIECE_COLORS:
                    if current_color == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], piece_color, 0.5):
                        self.canvas.itemconfig(self.circles[r][c], fill=piece_color)

    def draw_piece_preview(self, parent, shape, color, piece_name):
        """
        Draws a preview of the given piece shape on a canvas.
        
        Args:
            parent (tk.Widget): The parent widget where the canvas will be added.
            shape (list): The 2D list representing the piece's shape.
            color (str): The color of the piece.
            piece_name (str): The name of the piece.
        """
        pieces_per_row = 6
        piece_index = list(PIECES.keys()).index(piece_name)
        row = piece_index // pieces_per_row
        col = piece_index % pieces_per_row

        # Create a canvas for the piece preview
        piece_canvas = tk.Canvas(parent, width=40 * len(shape[0]), height=61 * len(shape),
                                 highlightthickness=0, bg=self.cget("background"))
        piece_canvas.grid(row=row, column=col, padx=5, pady=5)

        self.piece_canvases[piece_name] = piece_canvas

        # Draw the piece shape on the canvas
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell == 1:
                    x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                    y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                    x1 = x0 + CELL_RADIUS
                    y1 = y0 + CELL_RADIUS
                    piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)

        # Bind click event to select the piece
        piece_canvas.bind("<Button-1>", lambda e, n=piece_name: self.select_piece(n))

    def highlight_piece_preview(self, piece_name, highlight=True):
        """
        Highlights the selected piece by changing its color.
        
        Args:
            piece_name (str): The name of the piece to highlight.
            highlight (bool): Whether to highlight or restore the piece's original color.
        """
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            color = PIECE_COLORS[list(PIECES.keys()).index(piece_name)]
            if highlight:
                # Lighten the color when highlighted
                lighter_color = self.blend_colors(color, 'grey', 0.5)
            else:
                lighter_color = color

            # Clear the canvas and redraw with the updated color
            piece_canvas.delete("all")
            shape = PIECES[piece_name]

            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=lighter_color, outline="black", width=2)

    def update_piece_preview(self, piece_name):
        """
        Updates the preview of a piece after a transformation (e.g., rotation or mirroring).
        
        Args:
            piece_name (str): The name of the piece to update.
        """
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            piece_canvas.delete("all")  # Clear the current preview
            color = self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(piece_name)], "grey", 0.5)
            shape = PIECES[piece_name]

            # Redraw the piece with the updated preview
            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)

    def destroy_preview(self, event):
        """
        Destroys any visible piece previews when the mouse leaves the canvas area.
        
        Args:
            event (tk.Event): The mouse leave event.
        """
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.selected_piece:
                    if self.canvas.itemcget(self.circles[r][c], "fill") == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                        self.canvas.itemconfig(self.circles[r][c], fill="white")

    def reset_piece_previews(self):
        """
        Resets all piece previews to their original state.
        """
        for name in PIECES.keys():
            piece_canvas = self.piece_canvases[name]
            piece_canvas.delete("all")
            color = PIECE_COLORS[list(PIECES.keys()).index(name)]
            shape = PIECES[name]

            # Redraw each piece in its original color
            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)

# ---------------------------------------------------------------------------------------------------------------

class PieceMovement(PieceHandler):
    def __init__(self):
        """
        Initializes the PieceMovement class, inheriting from PieceHandler.
        """
        super().__init__()
        self.current_row = 0  # Current row position of the piece
        self.current_col = 0  # Current column position of the piece

    def move_left(self):
        """
        Moves the selected piece one cell to the left.
        """
        if self.selected_piece and self.current_col > 0:
            self.current_col -= 1
            self.update_piece_position()

    def move_right(self):
        """
        Moves the selected piece one cell to the right.
        """
        if self.selected_piece and self.current_col < BOARD_COLS - 1:
            self.current_col += 1
            self.update_piece_position()

    def move_up(self):
        """
        Moves the selected piece one cell up.
        """
        if self.selected_piece and self.current_row > 0:
            self.current_row -= 1
            self.update_piece_position()

    def move_down(self):
        """
        Moves the selected piece one cell down.
        """
        if self.selected_piece and self.current_row < BOARD_ROWS - 1:
            self.current_row += 1
            self.update_piece_position()

    def update_piece_position(self):
        """
        Updates the preview of the piece at the new position.
        """
        self.hide_piece_preview(self.selected_piece, delete_all=False)
        self.show_piece_preview_from_position(self.current_row, self.current_col)

    def show_piece_preview_from_position(self, row, col):
        """
        Displays the preview of the selected piece at the specified grid position.

        Args:
            row (int): Row index for the piece.
            col (int): Column index for the piece.
        """
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            for r, row_piece in enumerate(piece):
                for c, cell in enumerate(row_piece):
                    if cell == 1 and 0 <= row + r < BOARD_ROWS and 0 <= col + c < BOARD_COLS:
                        self.canvas.itemconfig(
                            self.circles[row + r][col + c],
                            fill=self.blend_colors(
                                PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5
                            ),
                        )

    def next_piece(self):
        """
        Selects the next piece in the piece selector.
        """
        piece_names = list(PIECES.keys())
        if self.selected_piece:
            current_index = piece_names.index(self.selected_piece)
            next_index = (current_index + 1) % len(piece_names)
        else:
            next_index = 0

        self.select_piece(piece_names[next_index])
        
    def previous_piece(self):
        """
        Selects the previous piece in the piece selector.
        """
        piece_names = list(PIECES.keys())
        if self.selected_piece:
            current_index = piece_names.index(self.selected_piece)
            previous_index = (current_index - 1) % len(piece_names)
        else:
            previous_index = len(piece_names) - 1

        self.select_piece(piece_names[previous_index])

    def cell_click(self, row, col):
        """
        Handles the click event on a cell of the board.

        Args:
            row (int): The row index of the clicked cell.
            col (int): The column index of the clicked cell.
        """
        if self.selected_piece:
            # Attempt to place the selected piece
            piece = PIECES[self.selected_piece]
            if self.can_place_piece(piece, row, col):
                self.place_piece(piece, row, col)
            else:
                # Show error if placement is not possible
                self.hide_piece_preview(self.selected_piece, False)
                messagebox.showwarning("Error", "Cannot place the piece here.")
        else:
            # If no piece is selected, attempt to remove one
            self.remove_piece(row, col)

    def select_piece(self, piece_name):
        """
        Selects a piece to be placed on the board.

        Args:
            piece_name (str): The name of the piece to select.
        """
        if self.pieces_available.get(piece_name, False):
            # Unhighlight the previously selected piece
            if self.selected_piece:
                self.highlight_piece_preview(self.selected_piece, highlight=False)

            # Highlight the newly selected piece
            self.selected_piece = piece_name
            self.highlight_piece_preview(piece_name, highlight=True)
            #print(f"Selected piece: {self.selected_piece}")
        elif self.pieces_on_the_grid.get(piece_name, False):
            self.selected_piece = piece_name
            self.hide_piece_preview(piece_name, False)
        else:
            # Show a warning message if the selected piece has already been placed
            messagebox.showwarning("Error", "This piece has already been placed.")

    def can_place_piece(self, piece, row, col):
        """
        Checks if a piece can be placed at the specified position on the board.

        Args:
            piece (list): The 2D list representing the piece's shape.
            row (int): The row index where the piece is to be placed.
            col (int): The column index where the piece is to be placed.

        Returns:
            bool: True if the piece can be placed, False otherwise.
        """
        
        board_state = self.board_state
        
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    # Check if the piece is out of bounds
                    if row + r >= BOARD_ROWS or col + c >= BOARD_COLS:
                        return False
                    # Check if the cell is already occupied by another piece
                    current_color = self.canvas.itemcget(self.circles[row + r][col + c], "fill")
                    if current_color != "white" and current_color != self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                        return False
        return True
    
    def can_place_piece_depending_board(self, piece, row, col, board_state):
        """
        Checks if a piece can be placed at the specified position on the board.

        Args:
            piece (list): The 2D list representing the piece's shape.
            row (int): The row index where the piece is to be placed.
            col (int): The column index where the piece is to be placed.
            board_state (list): The current state of the board (2D list) where 0 indicates an empty cell, and 1 indicates an occupied cell.

        Returns:
            bool: True if the piece can be placed, False otherwise.
        """
        
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    # Check if the piece is out of bounds
                    if row + r >= BOARD_ROWS or col + c >= BOARD_COLS:
                        return False
                    # Check if the cell is already occupied by another piece (based on board_state)
                    if board_state[row + r][col + c] != 0:  # 0 means empty, anything else is occupied
                        return False
        return True

    def can_move_piece(self, piece_name, row, col, board_state):
        # Vérifier si la pièce peut être déplacée sur la case (row, col)
        
        piece = PIECES.get(piece_name)
        
        if not piece:  # Vérifier si la pièce existe
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")
        
        # Calculer la taille de la pièce à partir de sa forme
        piece_height = len(piece)  # Nombre de lignes de la forme
        piece_width = len(piece[0])  # Nombre de colonnes dans la première ligne (on suppose que toutes les lignes ont la même longueur)
        
        # Vérifier si la position est valide et dans les limites du tableau
        if row < 0 or col < 0 or row + piece_height > BOARD_ROWS or col + piece_width > BOARD_COLS:
            return False  # La pièce dépasse les limites du tableau

        # Vérifier si la zone est libre pour placer la pièce
        for r in range(row, row + piece_height):
            for c in range(col, col + piece_width):
                if board_state[r][c] != 0:  # Si la case est déjà occupée par une autre pièce
                    return False

        return True  # La pièce peut être déplacée à la position (row, col)

    def can_remove_piece(self, piece_name, row, col, board_state):
        # Vérifier si la pièce peut être retirée à la position (row, col)
        
        # Vérifier que la case contient bien la pièce spécifiée
        piece = PIECES.get(piece_name)
        if board_state[row][col] != piece_name:
            print("la piece n'est pas aux coordonnées")
            return False  # La pièce spécifiée n'est pas à cet endroit
        
        # Vérifier si le retrait de la pièce ne laissera pas un "trou" dans une zone nécessaire
        # Exemple : si le retrait de la pièce laisse un espace vide qui empêcherait de placer d'autres pièces
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.is_piece_placed(board_state[r][c]) and not self.can_move_piece(board_state[r][c], r, c, board_state):
                    return False  # Retirer la pièce créerait une situation impossible
        
        return True  # La pièce peut être retirée

    def can_remove_piece_by_name(self, piece_name):
        """
        Vérifie si le plateau contient une pièce spécifiée par son nom.
        """
        for row in range(len(self.board_state)):
            for col in range(len(self.board_state[row])):
                cell = self.board_state[row][col]
                if cell and cell.get('piece') == piece_name:
                    print(f"La pièce '{piece_name}' existe à ({row}, {col}).")
                    return True  # La pièce a été trouvée sur le plateau

        print(f"La pièce '{piece_name}' n'a pas été trouvée sur le plateau.")
        return False  # La pièce n'existe pas sur le plateau

    def place_piece(self, piece, row, col):
        """
        Places the selected piece on the board at the specified position.
        It also stores the piece's rotation and symmetry state in the board's state matrix.

        Args:
            piece (list): The 2D list representing the piece's shape.
            row (int): The row index where the piece is to be placed.
            col (int): The column index where the piece is to be placed.
        """
        # Mark the piece as placed
        self.pieces_available[self.selected_piece] = False
        self.pieces_on_the_grid[self.selected_piece] = True

        # Record piece information (rotation and symmetry)
        piece_color = PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)]
        rotation = self.get_piece_rotation(self.selected_piece)  # Obtain the rotation of the piece
        symmetry = self.get_piece_symmetry(self.selected_piece)  # Obtain if piece is flipped

        # Update the board with the placed piece
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:  # Only place pieces where the cell is filled
                    # Place the piece on the canvas
                    self.canvas.itemconfig(self.circles[row + r][col + c], fill=piece_color)

                    # Update board state with piece info (position, rotation, symmetry)
                    self.board_state[row + r][col + c] = {
                        'piece': self.selected_piece,
                        'rotation': rotation,
                        'symmetry': symmetry
                    }

        # Print the updated board state for debugging purposes
        print("Board State", self.board_state)
        print("---------------------")
        print(self.pieces_available)
        print("---------------------")
        print(self.pieces_on_the_grid)
        print("---------------------")

        # Hide the preview of the piece after it has been placed
        self.hide_piece_preview(self.selected_piece)
        self.selected_piece = None
        
    def update_visual_grid(self):
        """
        Met à jour l'affichage visuel de la grille en fonction de l'état actuel de la grille.
        """
        for row in range(len(self.board_state)):
            for col in range(len(self.board_state[row])):
                cell = self.board_state[row][col]
                if cell:
                    piece_color = PIECE_COLORS[list(PIECES.keys()).index(cell['piece'])]
                    self.canvas.itemconfig(self.circles[row][col], fill=piece_color)
                else:
                    self.canvas.itemconfig(self.circles[row][col], fill="white")  # Couleur de fond pour les cellules vides

    def is_piece_placed(self, piece_name):
        """
        Vérifie si une pièce est déjà marquée comme placée dans la grille.
        Args:
            piece_name (str): Le nom de la pièce à vérifier.
        Returns:
            bool: True si la pièce est placée, False sinon.
        """
        return self.pieces_on_the_grid.get(piece_name, False)

    def remove_piece(self, row, col):
        """
        Removes a piece from the board by finding all cells associated with it
        in the board state matrix based on the clicked cell.

        Args:
            row (int): The row index of the clicked cell.
            col (int): The column index of the clicked cell.
        """
        # Check if the clicked cell contains a piece
        cell_data = self.board_state[row][col]
        if cell_data:
            piece_name = cell_data['piece']

            # Mark the piece as available again
            self.pieces_available[piece_name] = True
            self.pieces_on_the_grid[piece_name] = False

            # Iterate through the board to find and clear all cells occupied by the piece
            for r in range(len(self.board_state)):
                for c in range(len(self.board_state[r])):
                    if self.board_state[r][c] and self.board_state[r][c]['piece'] == piece_name:
                        # Reset the cell visually and in the board state
                        self.canvas.itemconfig(self.circles[r][c], fill='white')  # Reset color
                        self.board_state[r][c] = 0  # Clear the cell in the state matrix

            print(f"Removed all instances of piece '{piece_name}'.")
        else:
            messagebox.showinfo("Info", "No piece to remove at this position.")
        
        # Draw each piece for selection with color and shape
        for i, (name, shape) in enumerate(PIECES.items()):
            piece_color = PIECE_COLORS[i]

            # Check if the piece is available before drawing it
            if self.pieces_available.get(name, True):  # Default to True if not explicitly set
                self.draw_piece_preview(self.piece_frame, shape, piece_color, name)
                
    def remove_piece_by_name(self, piece_name):
        """
        Removes all instances of a piece from the board by its name.

        Args:
            piece_name (str): The name of the piece to remove.
        """
        # Vérifier si la pièce est présente dans l'état du plateau
        if piece_name not in self.pieces_on_the_grid or not self.pieces_on_the_grid[piece_name]:
            print(f"La pièce '{piece_name}' n'est pas présente sur le plateau.")
            messagebox.showinfo("Info", f"La pièce '{piece_name}' n'est pas sur le plateau.")
            return

        # Marquer la pièce comme disponible à nouveau
        self.pieces_available[piece_name] = True
        self.pieces_on_the_grid[piece_name] = False

        # Itérer à travers l'état du plateau pour trouver et effacer toutes les cellules occupées par la pièce
        for r in range(len(self.board_state)):
            for c in range(len(self.board_state[r])):
                if self.board_state[r][c] and self.board_state[r][c]['piece'] == piece_name:
                    # Réinitialiser visuellement la cellule et dans l'état du plateau
                    self.canvas.itemconfig(self.circles[r][c], fill='white')  # Réinitialiser la couleur
                    self.board_state[r][c] = 0  # Effacer la cellule dans la matrice de l'état

        print(f"Supprimé toutes les instances de la pièce '{piece_name}'.")

        # Redessiner chaque pièce pour la sélection avec la couleur et la forme
        for i, (name, shape) in enumerate(PIECES.items()):
            piece_color = PIECE_COLORS[i]

            # Vérifier si la pièce est disponible avant de la dessiner
            if self.pieces_available.get(name, True):  # Par défaut à True si non explicitement défini
                self.draw_piece_preview(self.piece_frame, shape, piece_color, name)           
                   
    def get_piece_rotation(self, piece_name):
        """
        Retrieves the current rotation of the selected piece.

        Args:
            piece_name (str): The name of the piece.

        Returns:
            int: The current rotation of the piece (0, 90, 180, or 270).
        """
        return self.piece_states[piece_name]['rotation']
    
    def get_piece_symmetry(self, piece_name):
        """
        Retrieves whether the selected piece has been mirrored (flipped).

        Args:
            piece_name (str): The name of the piece.

        Returns:
            bool: Whether the piece has been mirrored (True) or not (False).
        """
        return self.piece_states[piece_name]['symmetry']
    
    def transform_piece(self, piece, rotation, symmetry):
        """
        Transforms a piece based on its rotation and symmetry.

        Args:
            piece (list): The original 2D matrix of the piece.
            rotation (int): The rotation angle (0, 90, 180, 270).
            symmetry (bool): Whether the piece is horizontally flipped.

        Returns:
            list: The transformed 2D matrix of the piece.
        """
        # Apply rotation
        for _ in range(rotation // 90):
            piece = [list(row) for row in zip(*piece[::-1])]
        # Apply symmetry (flip horizontally)
        if symmetry:
            piece = [row[::-1] for row in piece]
        return piece

# ---------------------------------------------------------------------------------------------------------------

class PieceTransformation(PieceMovement):
    def __init__(self):
        """
        Initializes the PieceTransformation class, inheriting from PieceMovement.
        This class adds functionality to rotate and mirror (flip horizontally) pieces.
        """
        super().__init__()

    def rotate_piece(self):
        """
        Rotates the selected piece clockwise by 90 degrees.
        """
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            # Rotate the piece matrix by transposing and reversing rows
            rotated_piece = [list(row) for row in zip(*piece[::-1])]
            PIECES[self.selected_piece] = rotated_piece
            
            # Update the rotation state (0 -> 90 -> 180 -> 270 -> 0)
            current_rotation = self.piece_states[self.selected_piece]['rotation']
            new_rotation = (current_rotation + 90) % 360
            self.piece_states[self.selected_piece]['rotation'] = new_rotation
            
            # Update the preview of the rotated piece
            self.update_piece_preview(self.selected_piece)
        else:
            print('select piece')
            messagebox.showinfo("Selection", "Please select a piece to rotate first.")

    def mirror_piece(self):
        """
        Applies a horizontal mirror (flip) to the selected piece.
        """
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            # Mirror the piece by reversing each row
            mirrored_piece = [row[::-1] for row in piece]
            PIECES[self.selected_piece] = mirrored_piece
            
            # Update the symmetry state (True for flipped, False for original)
            current_symmetry = self.piece_states[self.selected_piece]['symmetry']
            new_symmetry = not current_symmetry  # Toggle symmetry
            self.piece_states[self.selected_piece]['symmetry'] = new_symmetry
            
            # Update the preview of the mirrored piece
            self.update_piece_preview(self.selected_piece)
        else:
            print('select piece')
            messagebox.showinfo("Selection", "Please select a piece to mirror first.")