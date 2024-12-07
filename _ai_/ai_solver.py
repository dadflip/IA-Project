import tkinter as tk
from tkinter import messagebox
from _ai_.ACTIONS import CHECK, DISPLAY, Endpoint
from _ai_._agents_.Q_AGENT import QLearningAgent
from _io_.io import InputHandler
from _ui_.piece import PieceTransformation
from constants import PIECE_COLORS, PIECES
from utils.utils import transform_to_matrix


class IQSolver(Endpoint):
    """
    Handles the solving logic of the puzzle game using Q-learning with backtracking.
    """
    def __init__(self):
        super().__init__()
        self.check = CHECK()
        self.display = DISPLAY()
        
    def validate_pieces(self, available_pieces, placed_pieces):
        """
        Compare deux listes pour vérifier si elles contiennent les mêmes éléments, 
        indépendamment de l'ordre.

        Args:
            available_pieces (list): Liste des noms des pièces disponibles.
            placed_pieces (list): Liste des noms des pièces placées.

        Returns:
            bool: True si les deux listes contiennent les mêmes éléments, False sinon.
        """
        if set(available_pieces) == set(placed_pieces):
            print("Les deux listes contiennent les mêmes éléments.")
            return True
        else:
            print("Les deux listes ne contiennent pas les mêmes éléments.")
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
            
            for piece_name in available_pieces:
                
                placed_pieces = self.get_placed_pieces()            
                print(f"----- PIECE AVAILABLE: {available_pieces}   -------- PIECE PLACED: {placed_pieces}")
            
                if piece_name in placed_pieces:
                    print(f'--> in placed pieces {piece_name}')
                    continue

                self.select_piece(piece_name)
                possible_moves = self.get_possible_moves(piece_name, grid, state_history, excluded_moves)  # Pass state history here
                if not possible_moves:
                    print(f'--> no possible moves for piece {piece_name}')
                    # continue

                excluded_moves.clear()  # Réinitialiser excluded_moves avant de tester de nouvelles actions
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
        for episode in range(50): #on peut le mettre à 1000 également
            print("Tentative:", episode)
            if self._run_q_learning_episode(agent, grid, piece_name, placed_pieces, state_history, excluded_moves):
                # placed_pieces.append(piece_name)
                break  # Move to the next piece

    def _run_q_learning_episode(self, agent, initial_state, piece_name, placed_pieces, state_history, excluded_moves):
        """
        Exécute une seule épisode de Q-learning avec backtracking et exclusion des actions bloquées.
        """
        state = initial_state
        
        # Filtrer les actions exclues avant de choisir une action
        possible_actions = self.get_possible_moves(piece_name, state, state_history, excluded_moves)
        if not possible_actions:
            print("Aucune action possible restante. Tentative de remontée dans l'historique.")
            
            # Limiter la profondeur de remontée dans l'historique pour éviter de revenir trop loin
            state_history_cpy = state_history[-5:]  # Limiter à 10 états précédents
            
            while state_history_cpy:
                if len(state_history_cpy) > 0:
                    previous_state, previous_action, _ = state_history_cpy.pop()
                    print(f"previous action : {previous_action}")
                    excluded_moves.append((previous_state, previous_action))  # Ajouter à la liste des actions exclues

                    # Vérifier si on peut effectuer une nouvelle action à partir de cet état
                    possible_actions = self.get_possible_moves(piece_name, previous_state, state_history_cpy, excluded_moves)
                    print(f"possible actions : {possible_actions}")

                    if possible_actions:
                        print(f"Revenu à un état précédent. Actions possibles trouvées : {possible_actions}")
                        action = agent.choose_action(previous_state, possible_actions)  # Choisir avec epsilon-greedy
                        print(f'Action choisie à partir de l\'état précédent : {action}')
                        reward = agent.calculate_reward(previous_state, action)
                        next_state = self.set_move(previous_state, piece_name, action)
                        agent.update_q_value(previous_state, action, reward, next_state)
                        
                        # Sauvegarde du nouvel état dans l'historique réel
                        state_history.append((previous_state, action, reward))
                        return True
                    else:
                        print("Aucune action possible dans cet état précédent. On continue à remonter.")

                
                # Si aucune action possible, revisiter les pièces placées
                for placed_piece in placed_pieces:
                    excluded_moves.clear()  # Réinitialiser excluded_moves avant de tester de nouvelles actions
                    
                    print(f"Tentative de réappliquer une action sur la pièce placée : {placed_piece}")
                    possible_actions_for_placed = self.get_possible_moves(placed_piece, state, state_history_cpy, excluded_moves)
                    print(f"possible actions for placed: {possible_actions_for_placed}")
                    if possible_actions_for_placed:
                        action = agent.choose_action(state, possible_actions_for_placed)
                        print(f'Action choisie pour la pièce placée : {action}')
                        reward = agent.calculate_reward(state, action)
                        next_state = self.set_move(state, placed_piece, action)
                        agent.update_q_value(state, action, reward, next_state)
                        
                        # Sauvegarde du nouvel état dans l'historique réel
                        state_history.append((state, action, reward))
                        return True

            print("Impossible de trouver une action possible dans l'historique. Fin de l'épisode.")
            return False  # Aucune solution n'a été trouvée, fin de l'épisode

        else:
            print("Actions possibles : ", possible_actions)

        # Si des actions possibles existent, choisir une action et continuer
        action = agent.choose_action(state, possible_actions)  # Choisir avec epsilon-greedy
        print('ACTION:', action, "PIECE NAME:", piece_name)
        reward = agent.calculate_reward(state, action)
        next_state = self.set_move(state, piece_name, action)

        agent.update_q_value(state, action, reward, next_state)

        # Sauvegarde de l'état dans l'historique pour le backtracking
        state_history.append((state, action, reward))

        if self.is_piece_placed(piece_name):
            self.update_piece_preview(piece_name)
            self.update_visual_grid()
            self.canvas.update()
            return True

        # Backtracking: Si l'état mène à une configuration bloquée, revenir à l'état précédent
        if self.is_blocked(next_state):
            print(f"État bloqué atteint. Ajout de l'action {action} à la liste d'exclusion.")
            
            # Ajouter l'action bloquante à la liste d'exclusion
            excluded_moves.append((state, action))

            # Annuler la dernière action et revenir à l'état précédent
            if state_history:
                state_history.pop()  # Supprimer le dernier état-action
                if state_history:
                    previous_state, _, _ = state_history[-1]  # Récupérer l'état précédent
                    self.board_state = previous_state  # Revenir à l'état précédent
                else:
                    print("L'historique est vide, impossible de revenir à un état précédent.")
            
            return False  # Rechercher un autre mouvement à partir de cet état

    def _display_message(self, message):
        """
        Displays an informational message to the user.
        """
        messagebox.showinfo("Solve", message)
        
        
    def solve_with_dfs(self, verbose=True):
        """
        Résout le puzzle en utilisant DFS avec backtracking,
        en plaçant une pièce à la fois et en revenant en arrière si nécessaire.
        """
        initial_grid = self.get_board_state()  # État initial de la grille
        available_pieces = self.get_available_pieces()  # Liste des pièces disponibles
        visited_states = set()

        if verbose:
            print("Début de la résolution DFS...\n")
        # Trier les pièces par taille (les grandes pièces en premier)
        available_pieces.sort(key=lambda piece: -self.get_piece_size(PIECES.get(piece)))
        print(f"AVAILABLE :::: {available_pieces}")

        # Appeler la fonction récursive de backtracking
        if self.dfs_recursive(initial_grid, available_pieces, [], 0, visited_states, True):
            self._display_message("Puzzle résolu avec DFS et retour en arrière !")
            return True
        else:
            self._display_message("Aucune solution trouvée avec DFS.")
            return False

    def dfs_recursive(self, current_grid, remaining_pieces, path, depth, visited_states, verbose=True):
        """
        Fonction récursive pour résoudre le puzzle avec DFS et backtracking.
        Affiche l'arborescence de l'exploration pour le débogage si 'verbose' est activé.
        """
        grid_hash = self.grid_to_hashable(current_grid)
        if grid_hash in visited_states:
            return False  # Si cet état a déjà été exploré, on évite de revenir dessus.
        
        visited_states.add(grid_hash)
        
        indent = "  " * depth  # Indentation pour chaque niveau d'arbre
        if verbose:
            print(f"{indent}Exploration niveau {depth}:")
            print(f"{indent}Grille actuelle :")
            self.print_grid(current_grid)  # Affichage de la grille pour mieux visualiser l'état
            print(f"{indent}Pièces restantes : {remaining_pieces}")

        # Si toutes les pièces ont été placées et que la grille est correcte
        if not remaining_pieces:
            if self.check.is_solution(current_grid):
                if verbose:
                    print(f"{indent}Solution trouvée!")
                self.replay_solution(path)  # Rejouer la solution
                return True
            else:
                if verbose:
                    print(f"{indent}Solution incorrecte, retour en arrière.")
                return False  # Solution incorrecte

        # Prendre la prochaine pièce à placer
        piece = remaining_pieces[0]
        self.select_piece(piece)  # Sélectionner la pièce
        if verbose:
            print(f"{indent}Essayer de placer la pièce : {piece}")

        # Générer tous les mouvements possibles de placement pour cette pièce
        possible_moves = [move for move in self.get_possible_moves(piece, current_grid, [], [])
                        if move[0] == 'place']  # Filtrer pour ne garder que les mouvements de type 'place'
        
        # Trier les mouvements par heuristique (ex. : remplir le plus d'espace possible)
        # possible_moves.sort(key=lambda move: -self.evaluate_move(move, current_grid, piece))


        # Essayer chaque mouvement possible de placement pour cette pièce
        for move in possible_moves:
            # Affichage pour chaque tentative de mouvement
            if verbose:
                print(f"{indent}Essayer le mouvement : {move}")
            
            # Appliquer le mouvement
            new_grid = self.set_move(current_grid, piece, move)
            
            # Vérifier si la pièce est bien placée
            if self.is_piece_placed(piece):
                if verbose:
                    print(f"{indent}Pièce placée : {piece}")
                self.update_visual_grid()
                self.canvas.update()
                new_remaining_pieces = remaining_pieces[1:]  # Retirer la pièce de la liste
                new_path = path + [(piece, move)]  # Ajouter ce mouvement au chemin

                # Appel récursif pour explorer le prochain placement
                if self.dfs_recursive(new_grid, new_remaining_pieces, new_path, depth + 1, visited_states, verbose):
                    return True  # Solution trouvée, on termine la récursion

                # Si la solution n'a pas été trouvée, on revient en arrière
                if verbose:
                    print(f"{indent}Solution incorrecte, revenir en arrière.")
                self.remove_piece_by_name(piece)
                self.update_visual_grid()
                self.canvas.update()

        if verbose:
            print(f"{indent}Aucun mouvement valide, retour en arrière.")
        return False
    
    def get_piece_size(self, piece):
        """
        Calcule la taille d'une pièce en comptant le nombre total de cellules occupées (1).
        
        :param piece: Une matrice (liste de listes) représentant la pièce.
        :return: Un entier représentant le nombre de cellules occupées.
        """
        return sum(cell for row in piece for cell in row)
 
    def evaluate_move(self, move, grid, piece):
        """
        Évalue un mouvement pour prioriser ceux qui ont le plus de chances de réussir.
        Par exemple, maximiser l'espace couvert ou minimiser les zones vides.
        """
        # Implémenter une logique d'évaluation spécifique
        return self.calculate_filled_area_after_move(grid, move, piece)

    def calculate_filled_area_after_move(self, grid, move, piece):
        """
        Calcule l'aire totale remplie sur la grille après avoir appliqué un mouvement.
        Cela inclut l'ajout de la pièce et évalue l'espace occupé pour prioriser ce mouvement.
        
        :param grid: La grille actuelle.
        :param move: Le mouvement à évaluer (inclut la position et l'orientation).
        :param piece: La pièce à placer.
        :return: Une valeur numérique représentant l'aire remplie après le mouvement.
        """
        # Créer une copie de la grille pour simuler le mouvement
        simulated_grid = [row[:] for row in grid]

        # Appliquer le mouvement à la grille simulée
        simulated_grid = self.set_move(simulated_grid, piece, move)

        # Calculer l'aire remplie après le mouvement
        filled_area = sum(row.count(1) for row in simulated_grid)  # Supposons que 1 représente une cellule occupée

        # Éventuellement, pénaliser les trous ou les zones inaccessibles
        penalty = self.calculate_penalty_for_holes(simulated_grid)

        return filled_area - penalty
    
    def calculate_penalty_for_holes(self, grid):
        """
        Calcule une pénalité basée sur les trous ou espaces inutilisables dans la grille.
        
        :param grid: La grille actuelle après simulation.
        :return: Une pénalité numérique (plus élevée si la grille contient de nombreux trous).
        """
        # Identifier les cellules vides
        empty_cells = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == 0]

        # Trouver des groupes de cellules vides connectées
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
                # Vérifier les voisins adjacents
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                        stack.append((nx, ny))
            return connected

        for cell in empty_cells:
            if cell not in visited:
                hole = dfs(cell)
                penalty += len(hole)  # Ajouter une pénalité proportionnelle à la taille du trou

        return penalty

    def remove_piece_from_grid(self, grid, piece):
        """
        Retire la pièce de la grille. Cette méthode devra être adaptée selon la structure de votre grille.
        """
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                # Si la cellule contient la pièce, la retirer (ou réinitialiser)
                if grid[row][col] == piece:  # Adapté à votre logique de placement
                    grid[row][col] = None  # Ou réinitialisez à un état vide approprié
        print(f"Pièce {piece} retirée de la grille.")

    def print_grid(self, grid):
        """
        Affiche la grille de manière lisible pour le débogage.
        """
        for row in grid:
            print(" ".join(str(cell) for cell in row))
        print("\n")

    def grid_to_hashable(self, grid):
        """Convertir la grille en une structure hachable."""
        return tuple(
            tuple(
                frozenset(cell.items()) if isinstance(cell, dict) else cell
                for cell in row
            )
            for row in grid
        )

    def replay_solution(self, path):
        """
        Rejouer la solution étape par étape.
        """
        print("Rejouer la solution...")
        for piece, move in path:
            self.select_piece(piece)
            self.set_move(self.get_board_state(), piece, move)
            self.update_visual_grid()
            self.canvas.update()

class IQPuzzlerProXXL(IQSolver):
    """
    Extends IQSolver with user interface features like piece preview, reset, and solve.
    """
    def __init__(self):
        """
        Initializes the puzzle interface, events, and controls.
        """
        super().__init__()
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
            ("Mirror", self.mirror_piece),
            ("Rotate", self.rotate_piece)
        ]
        self.button_frame = self._create_frame(self, button_properties)

    def _create_algorithm_dropdown(self):
        """
        Creates a dropdown to select the solving algorithm.
        """
        self.algorithm_var = tk.StringVar(value="Q-learning")
        tk.OptionMenu(
            self.button_frame, self.algorithm_var, "Q-learning", "DFS"
        ).grid(row=0, column=4, padx=5)

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
        }
        solve_method = solve_methods.get(selected_method)
        
        if solve_method:
            solve_method()
        else:
            print(f"Unknown method: {selected_method}")

    def _create_frame(self, parent, button_properties):
        """
        Creates and returns a frame for the provided buttons.
        """
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        for i, (text, command) in enumerate(button_properties):
            tk.Button(frame, text=text, command=command).grid(row=0, column=i, padx=5)
        return frame
