from copy import deepcopy
from _ai_.ai_solver import IQPuzzlerProXXL
from constants import BOARD_COLS, BOARD_ROWS, PIECES

class GameSolver(IQPuzzlerProXXL):
    def __init__(self, update_ui=True):
        super().__init__(update_ui=update_ui)  # Calling the parent class constructor to initialize the game
        self.solve_game()

    def different_piece(self, piece):
        """Returns the different variations of a piece (rotations + symmetries)."""
        Piece_variation = []
        mirror_piece = [row[::-1] for row in piece]
        var_piece = [piece, mirror_piece]
        for k in range(4):
            for i in range(2):
                temp_piece = [list(row) for row in zip(*var_piece[i][::-1])]
                var_piece[i] = temp_piece
                if temp_piece not in Piece_variation:
                    Piece_variation.append(temp_piece)
        return Piece_variation

    def where_place(self, piece, id_piece, can_place_piece):
        """Returns all the possible positions for a given piece."""
        Where_piece = []
        Var_piece = self.different_piece(piece)
        for piece in Var_piece:
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if can_place_piece(piece, row, col):
                        Where_piece.append([piece, row, col, id_piece])
        return Where_piece

    def brute_force_init(self, Piece, can_place_piece):
        """Initializes the grid and possible positions for each piece."""
        Grid = []
        for r in range(BOARD_ROWS):
            Grid.append([])
            for c in range(BOARD_COLS):
                current_color = self.canvas.itemcget(self.circles[r][c], "fill")
                if current_color != "white":
                    Grid[-1].append(1)
                else:
                    Grid[-1].append(0)

        Where = []
        for piece in range(len(Piece)):
            Where += self.where_place(Piece[piece], piece, can_place_piece)
        return Grid, Where

    def cohabitate(self, Piece1, Piece2):
        """Checks if two pieces interfere with each other."""
        if Piece1[3] == Piece2[3]:
            return False
        for row1 in range(len(Piece1[0])):
            for col1 in range(len(Piece1[0][row1])):
                for row2 in range(len(Piece2[0])):
                    for col2 in range(len(Piece2[0][row2])):
                        if Piece1[1] + row1 == Piece2[1] + row2 and Piece1[2] + col1 == Piece2[2] + col2:
                            if Piece1[0][row1][col1] == Piece2[0][row2][col2] == 1:
                                return False
        return True

    def brute_force_recurs(self, Grid, Where, can_place_piece, update_ui_callback):
        """Brute-force algorithm to solve the grid."""
        if all(0 not in row for row in Grid):
            print("Solution found!")
            return [0]

        if len(Where) == 0:
            print("No solution possible with current placements.")
            return False

        new_Grid = deepcopy(Grid)
        for row in range(len(Where[0][0])):
            for col in range(len(Where[0][0][row])):
                new_Grid[row + Where[0][1]][col + Where[0][2]] += Where[0][0][row][col]

        new_Where = deepcopy(Where)
        for k in range(len(new_Where) - 1, -1, -1):
            if not self.cohabitate(new_Where[0], new_Where[k]):
                del new_Where[k]

        update_ui_callback()

        Test = self.brute_force_recurs(new_Grid, new_Where, can_place_piece, update_ui_callback)
        if Test:
            Test.append(Where[0])
            return Test
        else:
            del Where[0]
            return self.brute_force_recurs(Grid, Where, can_place_piece, update_ui_callback)

    def find_piece(self, Piece):
        """Finds the identifier of a given piece."""
        for name, available in self.pieces_available.items():
            piece = PIECES[name]
            if available and len(Piece) + len(Piece[0]) == len(piece) + len(piece[0]):
                if Piece in self.different_piece(piece):
                    return name

    def brute_force_solving(self, Piece):
        """Solves the game using the brute-force algorithm."""
        Grid, Where = self.brute_force_init(Piece, self.can_place_piece)
        Solution = self.brute_force_recurs(Grid, Where, self.can_place_piece, self.update_visual_grid)
        if Solution:
            del Solution[0]
            for k in range(len(Solution)):
                piece_name = self.find_piece(Solution[k][0])
                self.select_piece(piece_name)
                self.place_piece(Solution[k][0], Solution[k][1], Solution[k][2])
                if self.update_ui:
                    self.update_visual_grid()
                    self.canvas.update()
        return Solution

    def solve_game(self):
        """Main method to solve the game."""
        Piece = [PIECES[piece] for piece, available in self.pieces_available.items() if available]
        return self.brute_force_solving(Piece)
    
# Entry point
if __name__ == "__main__":
    game = GameSolver(update_ui=False)  # Create an instance of the App class with UI updates disabled
    game.mainloop()  # Start the main event loop, keeping the game running
