# Game board dimensions
BOARD_ROWS = 5  # Number of rows on the board
BOARD_COLS = 11  # Number of columns on the board

# Circle properties for cells on the board
CELL_RADIUS = 20  # Radius of the circles representing cells
CELL_PADDING = 10  # Padding between the circles

# Colors assigned to pieces
PIECE_COLORS = [
    "black", "green", "darkgrey", "lightblue", "blue", "brown", "orange", 
    "red", "yellow", "pink", "turquoise", "olive" #, "purple", "cyan"
]

# Placeholder for empty pieces (used when no piece is selected or valid)
NOPE = []

# Piece definitions: each piece is represented by a 2D array (matrix)
# The value `1` represents a filled cell, and `0` represents an empty cell
PIECES = {
    'Bleu Noir': [[1, 1, 1], 
                  [1, 0, 0]],  # Blue and Black piece
    'Bleu Vert': [[1, 1, 1], 
                  [0, 1, 0]],  # Blue and Green piece
    'Noir': [[0, 1, 1], 
             [1, 1, 0], 
             [1, 0, 0]],  # Black piece
    'Bleu ciel': [[1, 1], 
                  [1, 0]],  # Sky Blue piece
    'Bleu foncé': [[1, 1, 1], 
                   [1, 0, 0], 
                   [1, 0, 0]],  # Dark Blue piece
    'Marron': [[0, 1, 1], 
               [1, 1, 0]],  # Brown piece
    'Orange': [[0, 0, 1], 
               [1, 1, 1], 
               [0, 1, 0]],  # Orange piece
    'Rouge': [[1, 1, 1, 1], 
              [1, 0, 0, 0]],  # Red piece
    'Jaune': [[1, 1, 1, 1], 
              [0, 1, 0, 0]],  # Yellow piece
    'Rose': [[1, 1, 1, 0], 
             [0, 0, 1, 1]],  # Pink piece
    'Turquoise': [[1, 1, 1], 
                  [1, 1, 0]],  # Turquoise piece
    'Kaki': [[1, 1, 1], 
             [1, 0, 1]],  # Khaki piece
    
    # 'Purple': [[1, 1], 
    #           [1, 1]],  # Square piece (2x2)
    # 'Cyan': [[0, 1, 1, 1], 
    #          [1, 1, 0, 0]]  # 'S' shape piece
}
