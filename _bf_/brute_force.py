import logging
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from constants import BOARD_COLS, BOARD_ROWS, PIECES
import threading

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

class BrutForceSolver:
    def __init__(self, canvas, circles, pieces_available, can_place_piece, can_remove_piece_by_name, remove_piece_by_name, update_visual_grid):
        self.canvas = canvas
        self.circles = circles
        self.pieces_available = pieces_available
        self.can_place_piece = can_place_piece
        self.can_remove_piece_by_name = can_remove_piece_by_name
        self.remove_piece_by_name = remove_piece_by_name
        self.update_visual_grid = update_visual_grid

        # Lock for thread safety and solution management
        self.solution_lock = threading.Lock()
        self.solution_found = None

    @staticmethod
    def different_piece(piece):
        """Return all variations of a piece, including rotations and mirror images."""
        piece_variations = set()
        mirrored_piece = [row[::-1] for row in piece]

        for variant in (piece, mirrored_piece):
            for _ in range(4):
                variant = [list(row) for row in zip(*variant[::-1])]
                piece_variations.add(tuple(map(tuple, variant)))  # Use tuples for immutability

        return [list(map(list, p)) for p in piece_variations]

    def where_place(self, piece, id_piece):
        """Determine all possible placements of a piece on the board in parallel."""
        placements = []

        def compute_placements(variant):
            local_placements = []
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if self.can_place_piece(variant, row, col):
                        local_placements.append([variant, row, col, id_piece])
            logging.debug(f"Thread {threading.current_thread().name} computed {len(local_placements)} placements for piece {id_piece}")
            return local_placements

        variants = self.different_piece(piece)
        with ThreadPoolExecutor() as executor:
            futures = executor.map(compute_placements, variants)
            for result in futures:
                placements.extend(result)

        logging.debug(f"Total placements found: {len(placements)}")
        return placements

    def brute_force_init(self, pieces):
        """Initialize the board and possible placements for pieces."""
        grid = [[1 if self.canvas.itemcget(self.circles[r][c], "fill") != "white" else 0 for c in range(BOARD_COLS)] for r in range(BOARD_ROWS)]
        where = []
        for i, piece in enumerate(pieces):
            where += self.where_place(piece, i)
        logging.debug(f"Initial grid setup complete, with {len(where)} placements to try.")
        return grid, where

    @staticmethod
    def coabite(piece1, piece2):
        """Check if two pieces overlap on the board."""
        if piece1[3] == piece2[3]:
            return False

        for r1, row1 in enumerate(piece1[0]):
            for c1, val1 in enumerate(row1):
                if val1:
                    for r2, row2 in enumerate(piece2[0]):
                        for c2, val2 in enumerate(row2):
                            if val2 and piece1[1] + r1 == piece2[1] + r2 and piece1[2] + c1 == piece2[2] + c2:
                                return False
        return True

    def brute_force_recurs(self, grid, where):
        """Recursive brute force solver with multithreading."""
        with self.solution_lock:
            if self.solution_found is not None:
                return False

        # Log the state of the grid at the start of each recursion
        logging.debug(f"Recursion step with grid state: {grid}")

        if all(all(cell for cell in row) for row in grid):
            with self.solution_lock:
                self.solution_found = [0]  # Mark the solution as found
            logging.info("Solution found!")
            return [0]

        if not where:
            logging.debug("No remaining placements to try.")
            return False

        def try_placement(idx):
            piece, row, col, piece_id = where[idx]
            new_grid = deepcopy(grid)

            logging.debug(f"Thread {threading.current_thread().name} trying to place piece {piece_id} at ({row}, {col})")

            # Place the piece temporarily
            can_place = True
            for i, piece_row in enumerate(piece):
                for j, cell in enumerate(piece_row):
                    grid_row, grid_col = row + i, col + j
                    if cell and (grid_row >= BOARD_ROWS or grid_col >= BOARD_COLS or new_grid[grid_row][grid_col] > 0):
                        can_place = False
                        logging.debug(f"Piece {piece_id} cannot be placed at ({row}, {col}) due to overlap or bounds.")
                        break
                if not can_place:
                    break

            if not can_place:
                return False

            # Update the grid with the piece
            for i, piece_row in enumerate(piece):
                for j, cell in enumerate(piece_row):
                    if cell:
                        new_grid[row + i][col + j] += cell

            # Log successful placement attempt
            logging.debug(f"Piece {piece_id} successfully placed at ({row}, {col})")

            # Filter placements for the next recursion
            new_where = [w for w in where if self.coabite(where[idx], w)]
            result = self.brute_force_recurs(new_grid, new_where)

            if result:
                result.append(where[idx])
                logging.debug(f"Thread {threading.current_thread().name} found a valid placement for piece {piece_id} at ({row}, {col})")
                return result

            return False

        # Parallelize the recursive calls
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(try_placement, idx) for idx in range(len(where))]

            for future in futures:
                result = future.result()
                if result:
                    with self.solution_lock:
                        if self.solution_found is None:
                            self.solution_found = result
                    logging.info(f"Solution found by thread {threading.current_thread().name}")
                    return result

        logging.debug("No valid placements found in this recursion step.")
        return False

    @staticmethod
    def find_piece(piece, pieces_available):
        """Find the name of the piece from its variations."""
        for name, available in pieces_available.items():
            if not available:
                continue
            if piece in BrutForceSolver.different_piece(PIECES[name]):
                return name

    def brute_force_solving(self, pieces):
        """Solve the puzzle using brute force."""
        grid, where = self.brute_force_init(pieces)

        solution = self.brute_force_recurs(grid, where)
        if solution:
            solution.pop(0)
            for step in solution:
                piece_name = self.find_piece(step[0], self.pieces_available)
                logging.info(f"Placing piece {piece_name} at ({step[1]}, {step[2]})")
                self.select_piece(piece_name)
                self.place_piece(step[0], step[1], step[2])
                if self.update_visual_grid:
                    self.update_visual_grid()
                    self.canvas.update()

        return solution

    def solve_game(self):
        """Entry point to solve the game."""
        pieces = [PIECES[name] for name, available in self.pieces_available.items() if available]
        return self.brute_force_solving(pieces)


if __name__ == "__main__":
    print("This is a utility class. Use it as part of a puzzle-solving application.")
