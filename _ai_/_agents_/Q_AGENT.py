import random
from _ai_.ACTIONS import CHECK
from _ai_.MEMORY import MemoryManager
from constants import PIECES
import threading

"""
    1. Learning Rate: learning_rate=0.3
    Significance: Determines how much new information affects the agent's knowledge update.
    Effect on the agent:
    - High learning_rate: Quick adaptation but risk of instability.
    - Low learning_rate: Slow adaptation but more stable.

    2. Discount Factor: discount_factor=0.9
    Significance: Determines the importance of future rewards compared to immediate rewards.
    Effect on the agent:
    - High discount_factor: Optimizes long-term rewards.
    - Low discount_factor: Focuses on immediate rewards.

    3. Epsilon: epsilon=0.1
    Significance: Defines the exploration vs exploitation rate.
    Effect on the agent:
    - High epsilon: More exploration, discovering new strategies.
    - Low epsilon: More exploitation, focusing on known optimal actions.
"""

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.3, discount_factor=0.9, epsilon=0.9):
        self.check = CHECK()
        self.actions = actions  # List of possible actions (piece movements)
        self.learning_rate = learning_rate  # Learning rate
        self.discount_factor = discount_factor  # Discount factor
        self.epsilon = epsilon  # Exploration vs exploitation factor
        self.q_table = {}  # Q-table to store state-action values
        self.memory_manager = MemoryManager()
        self.memory_cache = {}  # In-memory cache for quick access
        self.lock = threading.Lock()  # Lock for thread-safe operations
        
        self.combo_counter = 0  # Combo counter
        self.previous_completed_lines = set()  # Track already completed lines or subgrids

    def get_q_value(self, state, action):
        state_tuple = tuple(
            tuple(
                tuple((k, v) for k, v in element.items()) if isinstance(element, dict) else element
                for element in row
            )
            for row in state
        )
        
        if isinstance(action, list):
            action = tuple(action)

        if not isinstance(action, tuple):
            raise ValueError(f"Expected action to be a tuple, got {type(action)}")

        with self.lock:
            if (state_tuple, action) not in self.q_table:
                self.q_table[(state_tuple, action)] = 0.0  # Initialize to 0 if unknown

        return self.q_table[(state_tuple, action)]

    def update_q_value(self, state, action, reward, next_state):
        state_tuple = tuple(
            tuple(
                tuple((k, v) for k, v in element.items()) if isinstance(element, dict) else element
                for element in row
            )
            for row in state
        )
                    
        next_state_tuple = tuple(
            tuple(
                tuple((k, v) for k, v in element.items()) if isinstance(element, dict) else element
                for element in row
            )
            for row in next_state
        )

        possible_actions = self.actions
        if not possible_actions:
            print("No possible actions available for next state.")
            return

        try:
            max_next_q = max([self.get_q_value(next_state_tuple, a) for a in possible_actions])
        except ValueError:
            print("Error calculating max Q-value. Possible actions are empty or invalid.")
            return

        new_q_value = self.get_q_value(state, action) + self.learning_rate * (reward + self.discount_factor * max_next_q - self.get_q_value(state, action))
        with self.lock:
            self.q_table[(state_tuple, action)] = new_q_value
        
    def choose_action_with_memory(self, agent, state, possible_actions):
        state_key = str(state)
        
        if state_key in self.memory_cache:
            known_actions = [entry["action"] for entry in self.memory_cache[state_key]]
            for action in possible_actions:
                if action not in known_actions:
                    return action
        
        return agent.choose_action(state, possible_actions)

    def choose_action(self, state, possible_actions):
        """
        Chooses an action based on the given state and possible actions,
        using memory if available, or following an exploration/exploitation strategy.
        """
        state = tuple(tuple(row) for row in state)

        state_key = str(state)
        if state_key in self.memory_cache:
            known_actions = [entry["action"] for entry in self.memory_cache[state_key]]
            for action in possible_actions:
                if action not in known_actions:
                    return action

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_actions)
        else:
            q_values = [self.get_q_value(state, action) for action in possible_actions]
            max_q_value = max(q_values)
            best_actions = [action for action, q in zip(possible_actions, q_values) if q == max_q_value]
            return random.choice(best_actions)
        
    def calculate_reward(self, state, action):
        """
        Calculates the reward for an action in a given state.

        Args:
            state (list): Representation of the current game board state.
            action (tuple): Action performed, which can be a piece movement.

        Returns:
            int: The reward for the action.
        """
        reward = 0
        act = action[0]  # Action type: 'place', 'move', 'remove'

        if act == 'place':
            _, row, col, piece_name, rotation, mirror = action
            if state[row][col] == 1:
                reward += 15
            else:
                reward -= 2

            if self.check.is_solution(state):
                reward += 150

            reward += self.reward_for_completing_lines_or_columns(state, row, col)
            reward += self.reward_for_filling_corners(state, row, col)
            reward += self.reward_for_filling_edges(state, row, col)
            reward += self.reward_for_reducing_gaps(state, row, col)
            reward += self.reward_for_completing_subgrid(state, row, col)
            reward += self.combo_bonus()
            reward += self.reward_for_optimal_placement(state, row, col, piece_name, rotation, mirror)

        elif act == 'move':
            _, old_row, old_col, new_row, new_col, piece_name, rotation, mirror = action
            if self.check.is_valid_move(state, piece_name, new_row, new_col):
                reward += 10
            else:
                reward -= 3

            if self.check.is_solution(state):
                reward += 150

        elif act == 'remove':
            _, row, col, piece_name = action
            if self.check.is_valid_remove(state, piece_name, row, col):
                reward -= 50
            else:
                reward -= 100

            if self.check.is_solution(state):
                reward += 20

            reward -= self.penalty_for_destroying_lines_or_columns(state, row, col)

        if self.check.is_invalid_action(state, action):
            reward -= 5

        return reward

    def reward_for_filling_corners(self, state, row, col):
        """
        Calculates a reward for placing a piece in a corner of the grid.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.

        Returns:
            int: The additional reward for filling a corner.
        """
        reward = 0
        corners = [(0, 0), (0, len(state) - 1), (len(state) - 1, 0), (len(state) - 1, len(state) - 1)]
        if (row, col) in corners:
            reward += 30

        return reward

    def reward_for_completing_subgrid(self, state, row, col):
        """
        Calculates a reward for placing a piece that completes a subgrid (2x2, 3x3, etc.).

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.

        Returns:
            int: The reward for completing a subgrid.
        """
        reward = 0
        grid_size = 2

        for size in range(grid_size, len(state) + 1):
            for r in range(max(0, row - size + 1), min(len(state) - size + 1, row + 1)):
                for c in range(max(0, col - size + 1), min(len(state[0]) - size + 1, col + 1)):
                    if all(state[r + i][c + j] == 1 for i in range(size) for j in range(size)):
                        reward += 50
                        return reward

        return reward

    def reward_for_completing_lines_or_columns(self, state, row, col):
        """
        Calculates an additional reward if placing a piece completes a row or column.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.

        Returns:
            int: The additional reward.
        """
        reward = 0
        
        if all(state[row][c] == 1 for c in range(len(state[row]))):
            reward += 50
            self.combo_counter += 1
            self.previous_completed_lines.add(row)

        if all(state[r][col] == 1 for r in range(len(state))):
            reward += 50
            self.combo_counter += 1
            self.previous_completed_lines.add(col)

        return reward
    
    def reward_for_filling_edges(self, state, row, col):
        """
        Calculates a reward for placing a piece on the edges of the grid.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.

        Returns:
            int: The reward for filling the edges of the grid.
        """
        reward = 0
        if row == 0 or row == len(state) - 1 or col == 0 or col == len(state[0]) - 1:
            reward += 50

        return reward

    def reward_for_reducing_gaps(self, state, row, col):
        """
        Calculates a reward for reducing empty spaces between pieces.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.

        Returns:
            int: The reward for reducing empty spaces.
        """
        reward = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(state) and 0 <= nc < len(state[0]):
                if state[nr][nc] == 0:
                    reward += 60

        return reward

    def combo_bonus(self):
        """
        Calculates a bonus for combos, based on the sequence of consecutive successes.
        
        Returns:
            int: The combo bonus reward.
        """
        bonus = 0
        if self.combo_counter > 1:
            bonus += 10 * self.combo_counter
        return bonus
    
    def penalty_for_destroying_lines_or_columns(self, state, row, col):
        """
        Applies a penalty if a row, column, or subgrid is destroyed by the action.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the action took place.
            col (int): The column where the action took place.

        Returns:
            int: The penalty for destroying a row, column, or subgrid.
        """
        penalty = 0
        if any(state[row][c] == 0 for c in range(len(state[row]))):
            penalty += 50

        if any(state[r][col] == 0 for r in range(len(state))):
            penalty += 50

        grid_size = 2
        for size in range(grid_size, len(state) + 1):
            for r in range(max(0, row - size + 1), min(len(state) - size + 1, row + 1)):
                for c in range(max(0, col - size + 1), min(len(state[0]) - size + 1, col + 1)):
                    if all(state[r + i][c + j] == 0 for i in range(size) for j in range(size)):
                        penalty += 100
        return penalty
    
    def reward_for_optimal_placement(self, state, row, col, piece_name, rotation, mirror):
        """
        Calculates a high reward if a piece is placed optimally, fitting perfectly in a surrounded space with rotation and mirror.

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.
            piece_name (str): The name of the piece to place.
            rotation (int): The rotation of the piece (in degrees).
            mirror (bool): Whether the piece is mirrored.

        Returns:
            int: The reward for optimal placement.
        """
        reward = 0

        if self.is_optimal_placement(state, row, col, piece_name, rotation, mirror):
            reward += 500

        return reward
    
    def is_optimal_placement(self, state, row, col, piece_name, rotation, mirror):
        """
        Checks if a piece, with rotation and mirror, can be placed perfectly
        in the available space (surrounded by pieces) at the position (row, col).

        Args:
            state (list): Representation of the current game board state.
            row (int): The row where the piece is placed.
            col (int): The column where the piece is placed.
            piece_name (str): The name of the piece to place.
            rotation (int): The rotation of the piece (in degrees).
            mirror (bool): Whether the piece is mirrored.

        Returns:
            bool: True if the piece can be placed optimally, otherwise False.
        """
        piece_shape = PIECES.get(piece_name)
        piece_shape = self.apply_transformation(piece_shape, rotation, mirror)

        return self.check_piece_fits(state, row, col, piece_shape)

    def apply_transformation(self, piece_shape, rotation, mirror):
        """
        Applies rotation and mirror to the piece shape.

        Args:
            piece_shape (list): The initial shape of the piece.
            rotation (int): The rotation angle (in degrees).
            mirror (bool): Whether the piece should be mirrored.

        Returns:
            list: The transformed shape of the piece.
        """
        if mirror:
            piece_shape = self.apply_mirror(piece_shape)

        for _ in range(rotation // 90):
            piece_shape = self.rotate_90(piece_shape)

        return piece_shape

    def apply_mirror(self, piece_shape):
        """
        Applies a horizontal mirror to the piece shape.

        Args:
            piece_shape (list): The initial shape of the piece.

        Returns:
            list: The shape of the piece after applying the mirror.
        """
        return [row[::-1] for row in piece_shape]

    def rotate_90(self, piece_shape):
        """
        Rotates the piece shape 90 degrees clockwise.

        Args:
            piece_shape (list): The initial shape of the piece.

        Returns:
            list: The shape of the piece after the 90-degree rotation.
        """
        return [list(row) for row in zip(*piece_shape[::-1])]

    def check_piece_fits(self, state, row, col, piece_shape):
        """
        Checks if the piece shape can be placed at the given position without exceeding the board
        and respecting the boundaries.

        Args:
            state (list): Representation of the current game board state.
            row (int): The starting row for the check.
            col (int): The starting column for the check.
            piece_shape (list): The shape of the piece to check.

        Returns:
            bool: True if the piece can be placed in the specified space, otherwise False.
        """
        piece_height = len(piece_shape)
        piece_width = len(piece_shape[0])

        if row + piece_height > len(state) or col + piece_width > len(state[0]):
            return False

        for i in range(piece_height):
            for j in range(piece_width):
                if piece_shape[i][j] == 1:
                    if state[row + i][col + j] != 0:
                        return False

        return True
