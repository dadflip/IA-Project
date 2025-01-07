import threading
import tkinter as tk
from tkinter import messagebox
from _ai_.ACTIONS import CHECK, DISPLAY, Endpoint
from _ai_.MEMORY import MemoryManager
from _ai_._agents_.Q_AGENT import QLearningAgent
from _io_.io import InputHandler
from _ui_.piece import PieceTransformation
from constants import PIECE_COLORS, PIECES
from utils.utils import transform_to_matrix
from _bf_.brute_force import BrutForceSolver

class IQSolver(Endpoint):
    """
    Handles the solving logic of the puzzle game using Q-learning with backtracking.
    """
    def __init__(self, update_ui=True):
        super().__init__()
        self.check = CHECK()
        self.display = DISPLAY()
        self.stop_flag = threading.Event()  # Flag to stop the algorithm
        self.pause_flag = threading.Event()  # Flag to pause the algorithm
        self.update_ui = update_ui  # Flag to control UI updates
        self.solve_thread = None  # Thread for solving algorithm
        self.best_solution = None
        self.best_score = float('inf')
        self.brutforce = BrutForceSolver(self.canvas, self.circles, 
                                    self.pieces_available, self.can_place_piece,
                                    self.can_remove_piece_by_name, self.remove_piece_by_name,
                                    self.update_visual_grid)
    
    def stop_algorithm(self):
        """
        Stops the currently running solving algorithm.
        """
        print("Stopping algorithm...")
        self.stop_flag.set()
        if self.solve_thread:
            self.solve_thread.join()  # Wait for the thread to finish
    
    def resume_algorithm(self):
        """
        Resumes the currently paused solving algorithm.
        """
        print("Resuming algorithm...")
        self.pause_flag.clear()
        
    def toggle_visualization(self):
        """
        Toggles the visualization of pieces on the graphical interface.
        """
        self.update_ui = not self.update_ui
        print(f"Visualization {'enabled' if self.update_ui else 'disabled'}.")

    def validate_pieces(self, available_pieces, placed_pieces):
        """
        Compare two lists to check if they contain the same elements, regardless of order.

        Args:
            available_pieces (list): List of available piece names.
            placed_pieces (list): List of placed piece names.

        Returns:
            bool: True if both lists contain the same elements, False otherwise.
        """
        if set(available_pieces) == set(placed_pieces):
            print("Both lists contain the same elements.")
            return True
        else:
            print("The lists do not contain the same elements.")
            return False

    def solve_with_q_agent(self):
        """
        Solves the puzzle using Q-learning with backtracking.
        """
        grid = self.get_board_state()
        available_pieces = self.get_available_pieces()
        placed_pieces = self.get_placed_pieces()

        if not available_pieces:
            raise ValueError("No pieces available for the AI to select.")

        agent = QLearningAgent(actions=[])
        state_history = []  # Stack to store states for backtracking
        excluded_moves = []

        while not self.validate_pieces(available_pieces, placed_pieces):
            # Check stop flag
            if self.stop_flag.is_set():
                self._display_message("Q-learning stopped by user.")
                return False

            for piece_name in available_pieces:
                # Check stop flag
                if self.stop_flag.is_set():
                    self._display_message("Q-learning stopped by user.")
                    return False

                # Check pause flag
                while self.pause_flag.is_set():
                    if self.stop_flag.is_set():
                        self._display_message("Q-learning stopped by user.")
                        return False
                    self.pause_flag.wait(0.1)

                placed_pieces = self.get_placed_pieces()
                print(f"Available pieces: {available_pieces}   Placed pieces: {placed_pieces}")
            
                if piece_name in placed_pieces:
                    continue

                self.select_piece(piece_name)
                possible_moves = self.get_possible_moves(piece_name, grid, state_history, excluded_moves)  # Pass state history here
                if not possible_moves:
                    continue

                excluded_moves.clear()  # Clear excluded_moves before testing new actions
                agent.actions = possible_moves
                self._place_piece(agent, grid, piece_name, placed_pieces, state_history, excluded_moves)

            if self.check.is_solution(grid):
                self._display_message("Puzzle solved using Q-learning!")
                return True

        self._display_message("No solution found using Q-learning.")
        return False

    def _place_piece(self, agent, grid, piece_name, placed_pieces, state_history, excluded_moves):
        """
        Attempts to place a piece using Q-learning with backtracking.
        """
        for episode in range(50):  # Can be set to 1000 as well
            if self._run_q_learning_episode(agent, grid, piece_name, placed_pieces, state_history, excluded_moves):
                break  # Move to the next piece

    def _run_q_learning_episode(self, agent, initial_state, piece_name, placed_pieces, state_history, excluded_moves):
        """
        Runs a single episode of Q-learning with backtracking and exclusion of blocked actions.
        """
        state = initial_state
        memory_manager = MemoryManager()
        
        # Filter excluded actions before choosing an action
        possible_actions = self.get_possible_moves(piece_name, state, state_history, excluded_moves)
        if not possible_actions:
            print("No remaining possible actions. Attempting to backtrack.")
            
            # Limit the depth of backtracking to avoid going too far back
            state_history_cpy = state_history[-10:]  # Limit to 5 previous states
            
            while state_history_cpy:
                if len(state_history_cpy) > 0:
                    previous_state, previous_action, _ = state_history_cpy.pop()
                    excluded_moves.append((previous_state, previous_action))  # Add to the list of excluded actions

                    # Check if a new action can be performed from this state
                    possible_actions = self.get_possible_moves(piece_name, previous_state, state_history_cpy, excluded_moves)

                    if possible_actions:
                        action = agent.choose_action(previous_state, possible_actions)  # Choose with epsilon-greedy
                        reward = agent.calculate_reward(previous_state, action)
                        next_state = self.set_move(previous_state, piece_name, action)
                        agent.update_q_value(previous_state, action, reward, next_state)
                        
                        # Save the new state in the real history
                        state_history.append((previous_state, action, reward))
                        return True

                # If no possible action, revisit placed pieces
                for placed_piece in placed_pieces:
                    excluded_moves.clear()  # Reset excluded_moves before testing new actions
                    
                    possible_actions_for_placed = self.get_possible_moves(placed_piece, state, state_history_cpy, excluded_moves)
                    if possible_actions_for_placed:
                        action = agent.choose_action(state, possible_actions_for_placed)
                        reward = agent.calculate_reward(state, action)
                        next_state = self.set_move(state, placed_piece, action)
                        agent.update_q_value(state, action, reward, next_state)
                        
                        # Save the new state in the real history
                        state_history.append((state, action, reward))
                        return True

            print("Unable to find a possible action in the history. Ending episode.")
            return False  # No solution found, end of episode

        # If possible actions exist, choose an action and continue
        action = agent.choose_action(state, possible_actions)  # Choose with epsilon-greedy
        reward = agent.calculate_reward(state, action)
        next_state = self.set_move(state, piece_name, action)
        
        memory_manager.add_entry(state, action, reward, next_state)

        agent.update_q_value(state, action, reward, next_state)

        # Save the state in the history for backtracking
        state_history.append((state, action, reward))

        if self.is_piece_placed(piece_name):
            if self.update_ui:
                self.update_visual_grid()
                self.canvas.update()
            return True

        # Backtracking: If the state leads to a blocked configuration, revert to the previous state
        if self.is_blocked(next_state):
            print(f"Blocked state reached. Adding action {action} to the exclusion list.")
            
            # Add the blocking action to the exclusion list
            excluded_moves.append((state, action))

            # Undo the last action and revert to the previous state
            if state_history:
                state_history.pop()  # Remove the last state-action
                if state_history:
                    previous_state, _, _ = state_history[-1]  # Retrieve the previous state
                    self.board_state = previous_state  # Revert to the previous state
                else:
                    print("History is empty, unable to revert to a previous state.")
            
            return False  # Search for another move from this state

    def _display_message(self, message):
        """
        Displays an informational message to the user.
        """
        messagebox.showinfo("Solve", message)
        
    def solve_with_dfs(self, verbose=True):
        """
        Solves the puzzle using DFS with backtracking,
        placing one piece at a time and backtracking if necessary.
        """
        initial_grid = self.get_board_state()  # Initial state of the grid
        available_pieces = self.get_available_pieces()  # List of available pieces
        visited_states = set()

        if verbose:
            print("Starting DFS resolution...\n")

        # Sort pieces by size (larger pieces first)
        available_pieces.sort(key=lambda piece: -self.get_piece_size(PIECES.get(piece)))
        print(f"AVAILABLE :::: {available_pieces}")

        # Call the recursive backtracking function
        result = self.dfs_recursive(initial_grid, available_pieces, [], 0, visited_states, True)
        
        if self.stop_flag.is_set():
            self._display_message("DFS stopped by user.")
            return False

        if result:
            self._display_message("Puzzle solved with DFS and backtracking!")
            return True
        else:
            self._display_message("No solution found with DFS.")
            return False

    def dfs_recursive(self, current_grid, remaining_pieces, path, depth, visited_states, verbose=True):
        """
        Recursive function to solve the puzzle with DFS and backtracking.
        Includes logic for 'jumping' to another piece when completing key zones (like rows, columns, corners).
        """
        if self.stop_flag.is_set():
            return False

        grid_hash = self.grid_to_hashable(current_grid)
        if grid_hash in visited_states:
            return False  # If this state has already been explored, avoid revisiting it.

        visited_states.add(grid_hash)

        indent = "  " * depth  # Indentation for each tree level
        if verbose:
            print(f"{indent}Exploring level {depth}:")
            print(f"{indent}Current grid:")
            self.print_grid(current_grid)  # Display the grid for better visualization of the state
            print(f"{indent}Remaining pieces: {remaining_pieces}")

        # If all pieces have been placed and the grid is correct
        if not remaining_pieces:
            if self.check.is_solution(current_grid):
                score = self.evaluate(current_grid)
                if score < self.best_score:
                    self.best_score = score
                    self.best_solution = current_grid
                if verbose:
                    print(f"{indent}Solution found!")
                self.replay_solution(path)  # Replay the solution
                return True
            else:
                if verbose:
                    print(f"{indent}Incorrect solution, backtracking.")
                return False  # Incorrect solution

        # Take the next piece to place
        piece = remaining_pieces[0]
        self.select_piece(piece)  # Select the piece
        if verbose:
            print(f"{indent}Trying to place the piece: {piece}")

        # Generate all possible placement moves for this piece
        possible_moves = [move for move in self.get_possible_moves(piece, current_grid, [], []) if move[0] == 'place' or move[0] == 'remove']  # Filter to keep only 'place' moves

        # Sort moves by heuristic (e.g., filling the most space)
        possible_moves.sort(key=lambda move: self.evaluate_move_with_heuristics(current_grid, move, depth))

        # Try each possible placement move for this piece
        for move in possible_moves:
            # Apply the move
            new_grid = self.set_move(current_grid, piece, move)

            # Check if the piece is well placed
            if self.is_piece_placed(piece):
                if verbose:
                    print(f"{indent}Piece placed: {piece}")
                if self.update_ui:
                    self.update_visual_grid()
                    self.canvas.update()

                new_remaining_pieces = remaining_pieces[1:]  # Remove the piece from the list
                new_path = path + [(piece, move)]  # Add this move to the path

                # Check if a zone is filled (like a row, column, or corner)
                if self.is_zone_filled(new_grid):
                    # Jump to another piece that might better fit the now partially solved puzzle
                    next_piece = self.select_next_piece(new_remaining_pieces, new_grid)
                    if next_piece:
                        # Recurse with the new piece
                        new_remaining_pieces.remove(next_piece)
                        return self.dfs_recursive(new_grid, new_remaining_pieces, new_path, depth + 1, visited_states, verbose)

                # Otherwise, continue with the next piece
                if self.dfs_recursive(new_grid, new_remaining_pieces, new_path, depth + 1, visited_states, verbose):
                    return True  # Solution found, end recursion

                # If the solution was not found, backtrack
                if verbose:
                    print(f"{indent}Incorrect solution, backtracking.")
                self.remove_piece_by_name(piece)
                if self.update_ui:
                    self.update_visual_grid()
                    self.canvas.update()

        if verbose:
            print(f"{indent}No valid move, backtracking.")
        return False


    def is_zone_filled(self, grid):
        """
        Checks if a row, column, or corner is filled after a move.
        This function can be expanded to check other types of zones (e.g., 2x2 square regions, etc.).
        """
        # Check rows and columns for completion
        for i in range(len(grid)):
            if all(grid[i][j] != 0 for j in range(len(grid[i]))):  # Row filled
                return True
            if all(grid[j][i] != 0 for j in range(len(grid))):  # Column filled
                return True

        # Check corners (example: top-left, top-right, bottom-left, bottom-right)
        if all(grid[i][j] != 0 for i in range(2) for j in range(2)):  # Top-left corner
            return True
        if all(grid[i][j] != 0 for i in range(len(grid) - 2, len(grid)) for j in range(2)):  # Bottom-left corner
            return True
        if all(grid[i][j] != 0 for i in range(2) for j in range(len(grid) - 2, len(grid))):  # Top-right corner
            return True
        if all(grid[i][j] != 0 for i in range(len(grid) - 2, len(grid)) for j in range(len(grid) - 2, len(grid))):  # Bottom-right corner
            return True

        return False


    def select_next_piece(self, remaining_pieces, grid):
        """
        Selects the next piece to place, prioritizing pieces that can fill new zones.
        """
        # For now, we simply return the first available piece.
        # This logic can be improved to select pieces that are more likely to fill gaps.
        for piece in remaining_pieces:
            if self.is_hard_to_place(piece):
                continue  # Skip hard-to-place pieces
            return piece
        return None

    def solve_with_brute_force(self):
        """
        Solves the puzzle using brute force algorithm.
        """
        print("Starting brute force solving...")
        pieces = [PIECES[piece] for piece in self.get_available_pieces()]
        Grille, Where = self.brutforce.brute_force_init(pieces)
        print("Initial grid and possible placements generated.")
        solution = self.brutforce.brute_force_recurs(Grille, Where)
        if solution:
            del solution[0]  # Remove the initial zero
            for sol in solution:
                piece_name = self.brutforce.find_piece(sol[0], self.pieces_available)
                print(f"Placing piece {piece_name} at ({sol[1]}, {sol[2]})")
                self.select_piece(piece_name)
                self.place_piece(sol[0], sol[1], sol[2])
                if self.update_ui:
                    self.update_visual_grid()
                    self.canvas.update()
            self._display_message("Puzzle solved using brute force!")
            return True
        else:
            self._display_message("No solution found using brute force.")
            return False

    def update_ui_callback(self):
        """
        Callback function to update the UI.
        """
        if self.update_ui:
            self.update_visual_grid()
            self.canvas.update()

    def is_hard_to_place(self, piece):
        """
        Returns True if the piece is considered difficult to place, False otherwise.
        The difficulty can be based on size, shape complexity, and the number of filled cells.
        """
        # Example criteria: 
        # 1. If the piece is large (e.g., larger than 3x3)
        # 2. If the piece has an irregular shape (many scattered 1s)
        # 3. If the piece occupies a large part of the grid

        height = len(piece)
        width = len(piece[0]) if height > 0 else 0

        # Criterion 1: Piece size (e.g., larger than 3x3)
        if height > 3 or width > 3:
            return True

        # Criterion 2: Shape complexity (e.g., check the dispersion of '1's in the piece)
        filled_cells = sum(sum(1 for cell in row if cell == 1) for row in piece)
        if filled_cells > (height * width) // 2:  # More than half of the piece is filled
            return True

        # Criterion 3: Check if the piece occupies a large part of the grid
        # (This could be based on specific puzzle or game characteristics)
        if filled_cells > 2:  # Example rule: more than 2 filled cells may indicate difficulty
            return True

        return False

    def evaluate_move_with_heuristics(self, grid, move, depth):
        """
        Evaluates a move using a heuristic based on f(n) = g(n) + h(n).
        """
        g_n = depth  # Cost of the path from the initial state to the current state
        h_n = self.heuristic(grid, move)  # Estimated cost to reach the final state
        return g_n + h_n

    def heuristic(self, grid, move):
        """
        Heuristic to evaluate the quality of a move.
        """
        piece_name = move[3]
        row, col = move[1], move[2]
        piece = PIECES.get(piece_name)
        if not piece:
            return float('inf')  # Return a high value if the piece does not exist

        # 1. Heuristic: Number of correctly placed pieces
        correct_placements = 0
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if 0 <= row + i < len(grid) and 0 <= col + j < len(grid[0]):
                    if piece[i][j] == 1 and grid[row + i][col + j] == 0:
                        correct_placements += 1

        # Return negative of correct placements to prioritize better placements
        return -correct_placements

    def coverage_heuristic(self, grid, move):
        """
        Heuristic based on maximizing grid coverage with pieces.
        """
        piece_name = move[3]
        row, col = move[1], move[2]
        piece = PIECES.get(piece_name)
        if not piece:
            return float('inf')

        coverage = 0
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if 0 <= row + i < len(grid) and 0 <= col + j < len(grid[0]):
                    if piece[i][j] == 1 and grid[row + i][col + j] == 0:
                        coverage += 1
        return -coverage

    def remaining_pieces_heuristic(self, grid, remaining_pieces):
        """
        Heuristic based on the number of difficult-to-place pieces remaining.
        """
        # Prioritize harder-to-place pieces
        hard_to_place_count = 0
        for piece in remaining_pieces:
            if self.is_hard_to_place(piece):  # Custom function to determine difficulty
                hard_to_place_count += 1
        return hard_to_place_count

    def evaluate_move_with_combined_heuristics(self, grid, move, depth, remaining_pieces):
        """
        Combines multiple heuristics to evaluate a move more effectively.
        """
        g_n = depth
        h_n1 = self.heuristic(grid, move)  # Correct placements heuristic
        h_n2 = self.coverage_heuristic(grid, move)  # Grid coverage heuristic
        h_n3 = self.remaining_pieces_heuristic(grid, remaining_pieces)  # Difficult pieces heuristic

        # Combine heuristics with weighted factors
        h_n = h_n1 + h_n2 + h_n3
        return g_n + h_n

    def get_piece_size(self, piece):
        """
        Calculates the size of a piece by counting the total number of occupied cells (1).
        
        :param piece: A matrix (list of lists) representing the piece.
        :return: An integer representing the number of occupied cells.
        """
        return sum(cell for row in piece for cell in row)
 
    def evaluate_move(self, move, grid, piece):
        """
        Evaluates a move to prioritize those that are most likely to succeed.
        For example, maximizing covered space or minimizing empty areas.
        """
        # Implement specific evaluation logic
        return self.calculate_filled_area_after_move(grid, move, piece)

    def calculate_filled_area_after_move(self, grid, move, piece):
        """
        Calculates the total filled area on the grid after applying a move.
        This includes adding the piece and evaluates the occupied space to prioritize this move.
        
        :param grid: The current grid.
        :param move: The move to evaluate (includes position and orientation).
        :param piece: The piece to place.
        :return: A numerical value representing the filled area after the move.
        """
        # Create a copy of the grid to simulate the move
        simulated_grid = [row[:] for row in grid]

        # Apply the move to the simulated grid
        simulated_grid = self.set_move(simulated_grid, piece, move)

        # Calculate the filled area after the move
        filled_area = sum(row.count(1) for row in simulated_grid)  # Assume 1 represents an occupied cell

        # Optionally, penalize holes or inaccessible areas
        penalty = self.calculate_penalty_for_holes(simulated_grid)

        return filled_area - penalty
    
    def calculate_penalty_for_holes(self, grid):
        """
        Calculates a penalty based on holes or unusable spaces in the grid.
        
        :param grid: The current grid after simulation.
        :return: A numerical penalty (higher if the grid contains many holes).
        """
        # Identify empty cells
        empty_cells = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == 0]

        # Find groups of connected empty cells
        visited = set()
        penalty = 0

        def dfs(cell):
            stack = [cell]
            connected = []
            while stack:
                x, y = stack.pop()
                if (x, y) in visited:
                    continue
                visited.add((x, y))
                connected.append((x, y))
                # Check adjacent neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                        stack.append((nx, ny))
            return connected

        for cell in empty_cells:
            if cell not in visited:
                hole = dfs(cell)
                penalty += len(hole)  # Add a penalty proportional to the size of the hole

        return penalty

    def remove_piece_from_grid(self, grid, piece):
        """
        Removes the piece from the grid. This method should be adapted according to your grid structure.
        """
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                # If the cell contains the piece, remove it (or reset)
                if grid[row][col] == piece:  # Adapted to your placement logic
                    grid[row][col] = None  # Or reset to an appropriate empty state
        print(f"Piece {piece} removed from the grid.")

    def print_grid(self, grid):
        """
        Displays the grid in a readable format for debugging.
        """
        for row in grid:
            print(" ".join(str(cell) for cell in row))
        print("\n")

    def grid_to_hashable(self, grid):
        """Convert the grid to a hashable structure."""
        return tuple(
            tuple(
                frozenset(cell.items()) if isinstance(cell, dict) else cell
                for cell in row
            )
            for row in grid
        )

    def replay_solution(self, path):
        """
        Replay the solution step by step.
        """
        print("Replaying the solution...")
        for piece, move in path:
            self.select_piece(piece)
            self.set_move(self.get_board_state(), piece, move)
            if self.update_ui:
                self.update_visual_grid()
                self.canvas.update()

class IQPuzzlerProXXL(IQSolver):
    """
    Extends IQSolver with user interface features like piece preview, reset, and solve.
    """
    def __init__(self, update_ui=True):
        """
        Initializes the puzzle interface, events, and controls.
        """
        super().__init__(update_ui=update_ui)
        self.setup_ui()
        self.bind_events()
        self.reset_board()
        self.keyboard_handler = InputHandler(self)
        self.keyboard_handler.enable_input(self)

    def setup_ui(self):
        """
        Sets up the user interface: control buttons, dropdown, and piece previews.
        """
        self._create_control_buttons()
        self._create_algorithm_dropdown()
        self._create_piece_previews()
        

    def _create_control_buttons(self):
        """
        Dynamically creates control buttons.
        """
        button_properties = [
            ("Reset", self.reset_board),
            ("Solve", self.solve_puzzle),
            ("Stop", self.stop_algorithm),
            ("Resume", self.resume_algorithm),
            ("Toggle Visualization", self.toggle_visualization),
            ("Mirror", self.mirror_piece),
            ("Rotate", self.rotate_piece)
        ]
        self.button_frame = self._create_frame(self, button_properties)

    def _create_algorithm_dropdown(self):
        """
        Creates a dropdown to select the solving algorithm.
        """
        self.algorithm_var = tk.StringVar(value="DFS")
        dropdown = tk.OptionMenu(
            self.button_frame, self.algorithm_var, "Q-learning", "DFS", "Brute Force"
        )
        dropdown.grid(row=1, column=0, columnspan=4, pady=5, sticky="ew")

    def _create_piece_previews(self):
        """
        Creates previews for each piece with corresponding color and name.
        """
        self.piece_frame = tk.Frame(self)
        self.piece_frame.pack(pady=10)
        for i, (name, shape) in enumerate(PIECES.items()):
            piece_color = PIECE_COLORS[i]
            self.draw_piece_preview(self.piece_frame, shape, piece_color, name)

    def bind_events(self):
        """
        Binds mouse events for preview interaction.
        """
        self.canvas.bind("<Motion>", self.show_piece_preview)
        self.canvas.bind("<Leave>", self.destroy_preview)

    def solve_puzzle(self):
        """
        Solves the puzzle using the selected algorithm.
        """
        selected_method = self.algorithm_var.get()
        solve_methods = {
            "Q-learning": self.solve_with_q_agent,
            "DFS": self.solve_with_dfs,
            "Brute Force": self.solve_with_brute_force,
        }
        solve_method = solve_methods.get(selected_method)
        
        if solve_method:
            self.solve_thread = threading.Thread(target=solve_method)
            self.solve_thread.start()
        else:
            print(f"Unknown method: {selected_method}")
            
    def _create_frame(self, parent, button_properties):
        """
        Creates and returns a frame for the provided buttons.
        """
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        for i, (text, command) in enumerate(button_properties):
            tk.Button(frame, text=text, command=command).grid(row=0, column=i, padx=5, pady=5)
        return frame
