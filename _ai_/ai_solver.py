import tkinter as tk
from tkinter import messagebox
from collections import deque
import random



from colorama import Fore, Style
from _io_.io import InputHandler
from constants import BOARD_COLS, BOARD_ROWS, PIECE_COLORS, PIECES
from _ui_.piece import PieceTransformation


class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.actions = actions  # Liste des actions possibles (mouvements des pièces)
        self.learning_rate = learning_rate  # Taux d'apprentissage
        self.discount_factor = discount_factor  # Facteur de discount
        self.epsilon = epsilon  # Facteur d'exploration vs exploitation
        self.q_table = {}  # Table Q pour stocker les valeurs d'état-action

    def get_q_value(self, state, action):
        
        state_tuple = tuple(
            tuple(
                tuple((k, v) for k, v in element.items()) if isinstance(element, dict) else element
                for element in row
            )
            for row in state
        )
        
        # Si l'action est une liste, la convertir en tuple (si nécessaire)
        if isinstance(action, list):
            action = tuple(action)

        print("-------------------------")
        print("S:", state_tuple, "A:", action, "S:", state)
        
        # Vérification pour s'assurer que l'action est bien un tuple
        if not isinstance(action, tuple):
            raise ValueError(f"Expected action to be a tuple, got {type(action)}")

        # Vérifier si la clé (state_tuple, action) existe dans la q_table
        if (state_tuple, action) not in self.q_table:
            self.q_table[(state_tuple, action)] = 0.0  # Initialiser à 0 si inconnu
            
        # print("-------------------------")
        # print("Q:", self.q_table)

        return self.q_table[(state_tuple, action)]

    def update_q_value(self, state, action, reward, next_state):
        # Convertir state et next_state en tuples immuables
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

        # Vérification pour debug
        print(f"Updating Q-value: state: {state_tuple}, action: {action}, reward: {reward}, next_state: {next_state_tuple}")

        # Calculer la valeur Q maximale pour le prochain état
        max_next_q = max([self.get_q_value(next_state_tuple, a) for a in self.actions])

        # Mettre à jour la Q-table selon la formule de Q-learning
        new_q_value = self.get_q_value(state, action) + self.learning_rate * (reward + self.discount_factor * max_next_q - self.get_q_value(state, action))
        self.q_table[(state_tuple, action)] = new_q_value

    def choose_action(self, state):
        # Convert state to a tuple if it isn't already (to avoid issues with mutability)
        print("STATE ---- ", state)
        state = tuple(tuple(row) for row in state)

        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random action
            return random.choice(self.actions)
        else:
            # Exploitation: choose the action with the highest Q-value
            q_values = [self.get_q_value(state, action) for action in self.actions]
            max_q_value = max(q_values)
            best_actions = [action for action, q in zip(self.actions, q_values) if q == max_q_value]
            return random.choice(best_actions)        

class IQSolver(PieceTransformation, QLearningAgent):
    """
    Class to handle the solving logic of the puzzle game.
    """
    def __init__(self):
        """
        Initializes the IQSolver class, inheriting from PieceTransformation.
        """
        super().__init__()
        self.print_game_state()

    def solve_game(self):
        """
        Solves the game by analyzing the board and the available pieces using Q-learning.
        
        - Uses Q-learning to decide which piece to place and where.
        - Keeps track of the board state and updates it as pieces are placed.
        - Displays a message when the puzzle is solved.
        
        Returns:
            bool: Returns True if the solution is found, False otherwise.
        """
        # Initial setup: create a grid representing the current state of the board
        grid = self.get_board_state()

        # List of available pieces
        available_pieces = self.get_available_pieces()

        # Actions: Possible moves for each piece
        actions = self.possible_moves(grid, available_pieces[0])

        # Instantiate QLearningAgent
        agent = QLearningAgent(actions)

        # Start the Q-learning loop
        for episode in range(1000):  # Limit the number of episodes to avoid infinite loops
            state = grid
            done = False
            while not done:
                # Choose an action based on Q-learning (explore or exploit)
                action = agent.choose_action(state)
                (row, col, piece_name) = action  # Décomposer l'action en 3 parties
                
                # Calculate reward for this action
                reward = self.calculate_reward(state, action)

                # Apply the action to the board (place the piece)
                next_state = self.apply_move(state, available_pieces, row, col)

                # Update the Q-value table based on the agent's experience
                agent.update_q_value(state, action, reward, next_state)

                # Check if the puzzle is solved
                if self.is_solution(next_state):
                    done = True
                    messagebox.showinfo("Solve", "Puzzle solved!")
                    return True  # Puzzle is solved, return True
                
                # Update the state for the next iteration
                state = next_state

        # If the loop ends without finding a solution, return False
        messagebox.showinfo("Solve", "Solution not found.")
        return False
    
    def get_board_state(self):
        """
        Returns the current state of the board as a grid.
        
        Returns:
            list: The 2D grid representing the current state of the board.
        """
        return self.board_state

    def get_available_pieces(self):
        """
        Renvoie une liste des pièces disponibles à placer (noms des pièces).
        
        Retourne:
            list: Liste des noms des pièces disponibles.
        """
        return [name for name, available in self.pieces_available.items() if available]
    
    def get_game_state(self):
        """
        Returns the current state of the board, pieces, and other necessary variables.
        This includes:
        - Board state
        - Piece states (rotation, symmetry)
        - Available pieces
        - Selected piece
        - Preview piece
        """
        state = {
            'board_state': self.board_state,
            'piece_states': self.piece_states,
            'pieces_available': self.pieces_available,
            'pieces_on_the_grid': self.pieces_on_the_grid,
            'selected_piece': self.selected_piece,
            'preview_piece': self.preview_piece,
        }
        return state

    def print_game_state(self):
        game_state = self.get_game_state()
        
        print(Fore.CYAN + "Board State:")
        for row in game_state['board_state']:
            row_str = ' '.join([str(cell) if cell else 'None' for cell in row])
            print(Fore.GREEN + row_str)
        
        print(Style.RESET_ALL + "\nPiece States:")
        for piece, state in game_state['piece_states'].items():
            rotation = state['rotation']
            symmetry = 'Yes' if state['symmetry'] else 'No'
            print(Fore.YELLOW + f"{piece}: Rotation = {rotation}, Symmetry = {symmetry}")
        
        print(Style.RESET_ALL + "\nAvailable Pieces:")
        for piece, available in game_state['pieces_available'].items():
            status = "Available" if available else "Not Available"
            print(Fore.MAGENTA + f"{piece}: {status}")
        
        print(Style.RESET_ALL + "\nSelected Piece:")
        selected_piece = game_state['selected_piece']
        print(Fore.BLUE + f"{selected_piece if selected_piece else 'None'}")
        
        print("\nPreview Piece:")
        preview_piece = game_state['preview_piece']
        print(Fore.GREEN + f"{preview_piece if preview_piece else 'None'}")

    # ---------------------------------------------------------------------------------------

    def dfs(self, board, pieces, current_state, path=[]):
        # Si l'état actuel est une solution, retourner le chemin
        if self.is_solution(current_state):
            return path
        
        for piece in pieces:
            for move in self.possible_moves(board, piece):
                new_state = self.apply_move(current_state, piece, move)
                if new_state not in path:  # éviter les boucles
                    result = self.dfs(board, pieces, new_state, path + [move])
                    if result:
                        return result
        return None  # Aucun chemin trouvé

    def possible_moves(self, board, piece_name):
        """
        Retourne tous les mouvements possibles pour une pièce sur le plateau,
        en tenant compte de ses rotations et miroir.
        
        Args:
            board (list): L'état actuel du plateau de jeu.
            piece_name (str): Le nom de la pièce pour laquelle on vérifie les mouvements possibles.
        
        Returns:
            list: Liste des positions (row, col) où la pièce peut être placée.
        """
        # Récupérer la matrice de la pièce en fonction de son nom
        piece = PIECES.get(piece_name)
        self.selected_piece = piece_name
        
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")
        
        # Liste des mouvements possibles
        moves = []

        # Tester la pièce dans sa forme originale
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.can_place_piece(piece, row, col):
                    moves.append((row, col, self.selected_piece))  # Ajouter la position et la transformation

        # Tester après avoir fait tourner la pièce de 90° (1 fois)
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.can_place_piece(self.selected_piece, row, col):
                    moves.append((row, col, self.selected_piece))

        # Tester après avoir fait tourner la pièce de 180° (2 fois)
        self.rotate_piece()
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.can_place_piece(self.selected_piece, row, col):
                    moves.append((row, col, self.selected_piece))

        # Tester après avoir fait tourner la pièce de 270° (3 fois)
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.can_place_piece(self.selected_piece, row, col):
                    moves.append((row, col, self.selected_piece))

        # Tester après avoir appliqué un miroir horizontal (flip)
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.can_place_piece(self.selected_piece, row, col):
                    moves.append((row, col, self.selected_piece))

        print("MOVES:", moves)
        return moves

    def apply_move(self, state, available_pieces, row, col):
        if not available_pieces:
            raise ValueError("Il n'y a pas de pièces disponibles à placer")

        # Récupérer le nom de la première pièce disponible
        piece_name = available_pieces[0]
        piece = PIECES.get(piece_name)
        print(piece_name, piece)

        # Vérifier si l'emplacement est valide
        if state[row][col] != 0:  # Si l'emplacement est déjà occupé
            raise ValueError("L'emplacement est déjà occupé")
        else:
            print("applying move...")
            # Appliquer la pièce au plateau à la position spécifiée
            self.place_piece(piece, row, col)

        # Mise à jour de l'état du jeu après avoir placé la pièce
        new_state = self.get_board_state()

        # Retirer la pièce de la liste des pièces disponibles
        self.pieces_available[piece_name] = False

        return new_state


    def is_solution(self, state):
        # Vérifie si l'état actuel est une solution
        print("Solution State:", state)
        return all(cell is not 0 for row in state for cell in row)

    def is_invalid_action(self, state, action):
        """
        Vérifie si l'action est invalide.

        Args:
            state (list): Représentation de l'état actuel du plateau.
            action (tuple): Action réalisée.

        Returns:
            bool: True si l'action est invalide, sinon False.
        """
        (row, col, piece_name) = action  # Décomposer l'action en 3 parties
        # Implémentez la logique pour vérifier si l'action est invalide
        if state[row][col] == 1:  # Si la cellule est déjà remplie
            return True
        return False

    # ---------------------------------------------------------------------------------------

    def bfs(self, board, pieces):
        queue = deque([(board, [])])  # File d'attente contenant l'état du plateau et le chemin jusqu'ici
        visited = set()  # Ensemble des états déjà visités
        
        while queue:
            current_state, path = queue.popleft()
            
            # Si l'état actuel est une solution
            if self.is_solution(current_state):
                return path
            
            for piece in pieces:
                for move in self.possible_moves(board, piece):
                    new_state = self.apply_move(current_state, piece, move)
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, path + [move]))
        return None  # Aucun chemin trouvé

    # ---------------------------------------------------------------------------------------
    
    def calculate_reward(self, state, action):
        """
        Calcule la récompense d'une action dans un état donné.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            action (tuple): Action réalisée, qui peut être un mouvement de pièce.

        Returns:
            int: La récompense de l'action.
        """
        reward = 0

        # Exemple de critère 1: Si une pièce est placée correctement
        (row, col, piece_name) = action  # Décomposer l'action en 3 parties
        
        # Vérification si l'action a bien placé une pièce
        if state[row][col] == 1:  # Si une pièce est bien placée
            reward += 10  # Récompense positive pour la pièce bien placée
        else:
            reward -= 1  # Récompense négative si la pièce n'est pas bien placée

        # Exemple de critère 2: Si l'action mène à un état proche de la solution
        # Par exemple, vous pouvez définir une fonction qui calcule la proximité de l'état actuel à la solution du puzzle.
        if self.is_solution(state):
            reward += 100  # Récompense importante si le puzzle est résolu

        # Exemple de critère 3: Si l'action ne modifie pas l'état (action invalide ou redondante)
        if self.is_invalid_action(state, action):
            reward -= 5  # Pénalité pour une action invalide

        return reward




class IQPuzzlerProXXL(IQSolver):
    """
    Inherits from IQSolver to extend functionality with user interface features.
    Handles interactions like hovering over pieces, resetting the board, etc.
    """
    def __init__(self):
        """
        Initializes the IQPuzzlerProXXL class, which is a specific implementation of the puzzle solver.
        Sets up the user interface and binds necessary events for piece interaction.
        """
        super().__init__()

        # Bind mouse hover and leave events to show/hide piece preview
        self.canvas.bind("<Motion>", self.show_piece_preview)
        self.canvas.bind("<Leave>", self.destroy_preview)

        # Frame for control buttons (reset, solve, mirror, rotate)
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        # List of button properties and their associated methods for better scalability
        button_properties = [
            ("Reset", self.reset_board),
            ("Solve", self.solve_game),
            ("Mirror", self.mirror_piece),
            ("Rotate", self.rotate_piece)
        ]

        # Dynamically create and place buttons using a loop
        for i, (text, command) in enumerate(button_properties):
            button = tk.Button(self.button_frame, text=text, command=command)
            button.grid(row=0, column=i, padx=5)
            
        # Dropdown for selecting algorithm
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("Q-learning")  # Default method

        self.algorithm_dropdown = tk.OptionMenu(
            self.button_frame, self.algorithm_var, "DFS", "BFS", "Q-learning"
        )
        self.algorithm_dropdown.grid(row=0, column=len(button_properties), padx=5)
        
        
        def solve_puzzle(self):
            """
            Solves the puzzle based on the selected method.
            """
            selected_method = self.algorithm_var.get()

            if selected_method == "DFS":
                # Use DFS to solve the puzzle
                self.solve_with_dfs()
            elif selected_method == "BFS":
                # Use BFS to solve the puzzle
                self.solve_with_bfs()
            elif selected_method == "Q-learning":
                # Use Q-learning to solve the puzzle
                self.solve_game()

        def solve_with_dfs(self):
            """
            Solves the puzzle using DFS.
            """
            board = self.get_board_state()
            pieces = self.get_available_pieces()
            solution = self.dfs(board, pieces, board)
            
            if solution:
                messagebox.showinfo("Solution", "Puzzle solved using DFS!")
            else:
                messagebox.showinfo("Solution", "No solution found using DFS.")

        def solve_with_bfs(self):
            """
            Solves the puzzle using BFS.
            """
            board = self.get_board_state()
            pieces = self.get_available_pieces()
            solution = self.bfs(board, pieces)
            
            if solution:
                messagebox.showinfo("Solution", "Puzzle solved using BFS!")
            else:
                messagebox.showinfo("Solution", "No solution found using BFS.")
        

        # Frame for piece selection and previews
        self.piece_frame = tk.Frame(self)
        self.piece_frame.pack(pady=10)

        # Draw each piece for selection with color and shape
        for i, (name, shape) in enumerate(PIECES.items()):
            piece_color = PIECE_COLORS[i]
            self.draw_piece_preview(self.piece_frame, shape, piece_color, name)

        # Initialize the board state by resetting it
        self.reset_board()
        
        # Instantiate the keyboard input handler
        self.keyboard_handler = InputHandler(self)

        # Enable input handling for the current instance
        self.keyboard_handler.enable_input(self)
