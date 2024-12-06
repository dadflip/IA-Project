import random

from _ai_.ACTIONS import CHECK
from constants import PIECES

"""
    1. Learning Rate (Taux d'apprentissage) : learning_rate=0.3
Signification : Le learning_rate détermine dans quelle mesure les nouvelles informations reçues par l'agent vont affecter la mise à jour de ses connaissances (comme les valeurs Q dans le cas de Q-learning). Un taux d'apprentissage plus élevé signifie que l'agent va apprendre plus rapidement, mais risque de ne pas converger de manière optimale s'il est trop élevé.
Effet sur l'agent :
Un learning_rate élevé (proche de 1) amène l'agent à mettre rapidement à jour ses connaissances avec de nouvelles récompenses ou actions, ce qui peut entraîner une adaptation rapide, mais avec un risque d'instabilité ou de sur-apprentissage des nouvelles données.
Un learning_rate faible (proche de 0) signifie que l'agent prendra plus de temps pour s'ajuster et sera moins sensible aux nouvelles informations, ce qui peut rendre l'apprentissage plus lent, mais plus stable.


    2. Discount Factor (Facteur de réduction) : discount_factor=0.9
Signification : Le discount_factor, noté souvent par gamma (γ), est un paramètre qui détermine l'importance accordée aux récompenses futures par rapport aux récompenses immédiates. Plus gamma est élevé, plus l'agent valorise les récompenses futures dans ses décisions.
Effet sur l'agent :
Un discount_factor élevé (proche de 1) signifie que l'agent prend en compte les conséquences à long terme de ses actions. L'agent va essayer d'optimiser la récompense totale sur le long terme (en anticipant les récompenses futures).
Un discount_factor faible (proche de 0) signifie que l'agent privilégie les récompenses immédiates, sans se soucier des résultats à long terme. L'agent peut être plus impulsif et moins stratégique.


    3. Epsilon (Exploration vs Exploitation) : epsilon=0.1
Signification : epsilon est utilisé dans des algorithmes comme le Q-learning pour définir le taux d'exploration versus exploitation. Avec un certain taux d'exploration (epsilon), l'agent choisit des actions de manière aléatoire pour explorer l'environnement. Si epsilon est faible, l'agent privilégie l'exploitation des actions déjà connues pour maximiser les récompenses, tandis qu'avec un epsilon élevé, l'agent explore davantage de nouvelles actions.
Effet sur l'agent :
Un epsilon élevé (proche de 1) conduit l'agent à explorer plus fréquemment, ce qui permet de découvrir de nouvelles stratégies ou actions, mais cela peut aussi réduire l'efficacité de l'agent, car il choisit des actions qui ne sont pas toujours optimales.
Un epsilon faible (proche de 0) signifie que l'agent choisira principalement les actions qu'il considère comme les meilleures selon son expérience actuelle, ce qui peut le rendre plus efficace dans des environnements stables, mais limiter sa capacité à s'adapter si l'environnement change.
"""

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.3, discount_factor=0.9, epsilon=0.9):
        self.check = CHECK()
        self.actions = actions  # Liste des actions possibles (mouvements des pièces)
        self.learning_rate = learning_rate  # Taux d'apprentissage
        self.discount_factor = discount_factor  # Facteur de discount
        self.epsilon = epsilon  # Facteur d'exploration vs exploitation
        self.q_table = {}  # Table Q pour stocker les valeurs d'état-action
        
        self.combo_counter = 0  # Compteur de combos
        self.previous_completed_lines = set()  # Suivre les lignes ou sous-grilles déjà complétées

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

        # print("-------------------------")
        # print("S:", state_tuple, "A:", action, "S:", state)
        
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
        # Convert state and next_state to immutable tuples
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

        # Safeguard to avoid empty possible actions
        possible_actions = self.actions
        if not possible_actions:
            print("No possible actions available for next state.")
            return

        # Calculate the maximum Q-value for the next state
        try:
            max_next_q = max([self.get_q_value(next_state_tuple, a) for a in possible_actions])
        except ValueError:
            print("Error calculating max Q-value. Possible actions are empty or invalid.")
            return

        # Update Q-table using the Q-learning formula
        new_q_value = self.get_q_value(state, action) + self.learning_rate * (reward + self.discount_factor * max_next_q - self.get_q_value(state, action))
        self.q_table[(state_tuple, action)] = new_q_value

    def choose_action(self, state, possible_actions):
        """
        Choisit une action en fonction de l'état donné et des actions possibles,
        en suivant une stratégie d'exploration ou d'exploitation.
        """
        # Convertir l'état en tuple immuable pour éviter les problèmes de mutabilité
        state = tuple(tuple(row) for row in state)

        if random.uniform(0, 1) < self.epsilon:
            # Exploration : choisir une action aléatoire parmi les actions possibles
            return random.choice(possible_actions)
        else:
            # Exploitation : choisir l'action avec la valeur Q la plus élevée
            q_values = [self.get_q_value(state, action) for action in possible_actions]
            max_q_value = max(q_values)
            best_actions = [action for action, q in zip(possible_actions, q_values) if q == max_q_value]
            return random.choice(best_actions)
        
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
        act = action[0]  # Type d'action : 'place', 'move', 'remove'

        # Action "place"
        if act == 'place':
            _, row, col, piece_name, rotation, mirror = action
            if state[row][col] == 1:  # Si une pièce est bien placée
                reward += 15  # Récompense plus élevée pour un placement réussi
            else:
                reward -= 2  # Récompense négative si la pièce n'est pas bien placée

            # Bonus si le placement rapproche l'état de la solution
            if self.check.is_solution(state):
                reward += 150  # Récompense importante pour la résolution

            # Bonus pour compléter une ligne, colonne, ou sous-grille
            reward += self.reward_for_completing_lines_or_columns(state, row, col)

            # Bonus pour remplir un coin
            reward += self.reward_for_filling_corners(state, row, col)
            
            # Bonus pour remplir les bords de la grille
            reward += self.reward_for_filling_edges(state, row, col)

            # Bonus pour réduire les espaces vides
            reward += self.reward_for_reducing_gaps(state, row, col)

            # Bonus pour compléter une sous-grille
            reward += self.reward_for_completing_subgrid(state, row, col)

            # Bonus de combo pour des réussites successives
            reward += self.combo_bonus()
            
            # Bonus pour un placement optimal (pièce s'insérant parfaitement dans un espace entouré)
            reward += self.reward_for_optimal_placement(state, row, col, piece_name, rotation, mirror)

        # Action "move"
        elif act == 'move':
            _, old_row, old_col, new_row, new_col, piece_name, rotation, mirror = action
            if self.check.is_valid_move(state, piece_name, new_row, new_col):
                reward += 10  # Récompense plus élevée pour un mouvement valide
            else:
                reward -= 3  # Pénalité pour un mouvement invalide

            # Bonus si le mouvement rapproche l'état de la solution
            if self.check.is_solution(state):
                reward += 150  # Récompense importante pour la progression vers la solution

        # Action "remove"
        elif act == 'remove':
            _, row, col, piece_name = action
            if self.check.is_valid_remove(state, piece_name, row, col):
                reward -= 50   # Récompense faible pour une suppression valide
            else:
                reward -= 100  # Pénalité pour une suppression incorrecte

            # Faible bonus si cela rapproche l'état de la solution
            if self.check.is_solution(state):
                reward += 20  # Récompense moindre comparée au placement ou au déplacement
                
            # Malus pour la destruction d'une ligne ou colonne
            reward -= self.penalty_for_destroying_lines_or_columns(state, row, col)

        # Critère général : Pénaliser les actions invalides
        if self.check.is_invalid_action(state, action):
            reward -= 5  # Pénalité pour une action invalide
            
        

        print("REWARD:", reward)
        return reward

    def reward_for_filling_corners(self, state, row, col):
        """
        Calcule une récompense pour le placement d'une pièce dans un coin de la grille.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.

        Returns:
            int: La récompense supplémentaire pour remplir un coin.
        """
        reward = 0
        # Vérification des coins (top-left, top-right, bottom-left, bottom-right)
        corners = [(0, 0), (0, len(state) - 1), (len(state) - 1, 0), (len(state) - 1, len(state) - 1)]
        if (row, col) in corners:
            reward += 30  # Récompense pour placer une pièce dans un coin

        return reward

    def reward_for_completing_subgrid(self, state, row, col):
        """
        Calcule une récompense pour le placement d'une pièce qui complète un carré (2x2, 3x3, etc.).

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.

        Returns:
            int: La récompense pour compléter une sous-grille.
        """
        reward = 0
        grid_size = 2  # Taille minimale d'une sous-grille (2x2), ajustez en fonction de vos besoins

        # Vérifier si la sous-grille 2x2 (ou plus) est complète après le placement
        for size in range(grid_size, len(state) + 1):  # Tester les sous-grilles de taille 2x2, 3x3, etc.
            for r in range(max(0, row - size + 1), min(len(state) - size + 1, row + 1)):
                for c in range(max(0, col - size + 1), min(len(state[0]) - size + 1, col + 1)):
                    # Vérification d'un carré complet de taille 'size'
                    if all(state[r + i][c + j] == 1 for i in range(size) for j in range(size)):
                        reward += 50  # Récompense pour remplir une sous-grille complète
                        return reward

        return reward

    def reward_for_completing_lines_or_columns(self, state, row, col):
        """
        Calcule une récompense supplémentaire si le placement d'une pièce complète une ligne ou une colonne.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.

        Returns:
            int: La récompense supplémentaire.
        """
        reward = 0
        
        # Vérifier si la ligne est complète
        if all(state[row][c] == 1 for c in range(len(state[row]))):  # Vérifier si toute la ligne est remplie
            reward += 50  # Augmenter cette valeur pour une ligne ou colonne complète
            self.combo_counter += 1  # Augmenter le compteur de combos
            self.previous_completed_lines.add(row)  # Ajouter la ligne à l'ensemble des lignes complétées

        # Vérifier si la colonne est complète
        if all(state[r][col] == 1 for r in range(len(state))):  # Vérifier si toute la colonne est remplie
            reward += 50
            self.combo_counter += 1  # Augmenter le compteur de combos
            self.previous_completed_lines.add(col)  # Ajouter la colonne à l'ensemble des colonnes complétées

        return reward
    
    def reward_for_filling_edges(self, state, row, col):
        """
        Calcule une récompense pour le placement d'une pièce sur les bords de la grille.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.

        Returns:
            int: La récompense pour remplir les bords de la grille.
        """
        reward = 0
        # Vérifier si la pièce est placée sur un bord (ligne ou colonne externe)
        if row == 0 or row == len(state) - 1 or col == 0 or col == len(state[0]) - 1:
            reward += 50  # Récompense pour remplir un bord de la grille

        return reward

    def reward_for_reducing_gaps(self, state, row, col):
        """
        Calcule une récompense pour la réduction des espaces vides entre les pièces.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.

        Returns:
            int: La récompense pour la réduction des espaces vides.
        """
        reward = 0
        # Vérifier les cases voisines (haut, bas, gauche, droite)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(state) and 0 <= nc < len(state[0]):
                if state[nr][nc] == 0:  # Si la case voisine est vide
                    reward += 60  # Récompense pour réduire un espace vide

        return reward

    def combo_bonus(self):
        """
        Calcule un bonus pour les combos, basé sur la séquence de succès consécutifs.
        
        Returns:
            int: La récompense bonus de combo.
        """
        bonus = 0
        if self.combo_counter > 1:
            bonus += 10 * self.combo_counter  # Plus de combos successifs, plus de récompense
        return bonus
    
    def penalty_for_destroying_lines_or_columns(self, state, row, col):
        """
        Applique un malus si une ligne, une colonne, ou une sous-grille est détruite par l'action.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où l'action a eu lieu.
            col (int): La colonne où l'action a eu lieu.

        Returns:
            int: Le malus pour avoir détruit une ligne, une colonne ou une sous-grille.
        """
        penalty = 0
        # Pénalité pour la destruction d'une ligne
        if any(state[row][c] == 0 for c in range(len(state[row]))):  # Si la ligne est incompletée
            penalty += 50

        # Pénalité pour la destruction d'une colonne
        if any(state[r][col] == 0 for r in range(len(state))):  # Si la colonne est incompletée
            penalty += 50

        # Pénalité pour la destruction d'une sous-grille
        grid_size = 2  # Taille minimale d'une sous-grille (ajustez en fonction de vos besoins)
        for size in range(grid_size, len(state) + 1):
            for r in range(max(0, row - size + 1), min(len(state) - size + 1, row + 1)):
                for c in range(max(0, col - size + 1), min(len(state[0]) - size + 1, col + 1)):
                    if all(state[r + i][c + j] == 0 for i in range(size) for j in range(size)):  # Sous-grille détruite
                        penalty += 100
        return penalty
    
    def reward_for_optimal_placement(self, state, row, col, piece_name, rotation, mirror):
        """
        Calcule une récompense élevée si une pièce est placée de manière optimale, c'est-à-dire
        qu'elle s'insère parfaitement dans un emplacement entouré de pièces avec rotation et miroir.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.
            piece_name (str): Le nom de la pièce à placer.
            rotation (int): La rotation de la pièce (en degrés).
            mirror (bool): Si la pièce est en miroir.

        Returns:
            int: La récompense pour un placement optimal.
        """
        reward = 0

        # Vérification de l'emplacement autour de la pièce
        # Cela peut impliquer la vérification de l'état des cases adjacentes, en s'assurant que les pièces adjacentes
        # sont bien positionnées et que la forme de la pièce correspond à l'espace disponible.

        if self.is_optimal_placement(state, row, col, piece_name, rotation, mirror):
            reward += 500  # Récompense importante pour un placement optimal

        return reward
    
    
    def is_optimal_placement(self, state, row, col, piece_name, rotation, mirror):
        """
        Vérifie si une pièce, avec rotation et miroir, peut être placée parfaitement
        dans l'espace disponible (entourée de pièces) à la position (row, col).

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne où la pièce est placée.
            col (int): La colonne où la pièce est placée.
            piece_name (str): Le nom de la pièce à placer.
            rotation (int): La rotation de la pièce (en degrés).
            mirror (bool): Si la pièce est en miroir.

        Returns:
            bool: True si la pièce peut être placée de manière optimale, sinon False.
        """
        # Obtenez la forme de la pièce, en tenant compte de la rotation et du miroir
        piece_shape = PIECES.get(piece_name)
        piece_shape = self.apply_transformation(piece_shape, rotation, mirror)

        # Vérifiez si la pièce peut s'adapter dans l'espace disponible
        return self.check_piece_fits(state, row, col, piece_shape)


    def apply_transformation(self, piece_shape, rotation, mirror):
        """
        Applique une rotation et un miroir à la forme de la pièce.

        Args:
            piece_shape (list): La forme initiale de la pièce.
            rotation (int): L'angle de rotation (en degrés).
            mirror (bool): Si la pièce doit être retournée horizontalement ou verticalement.

        Returns:
            list: La forme transformée de la pièce.
        """
        # Appliquer le miroir si nécessaire
        if mirror:
            piece_shape = self.apply_mirror(piece_shape)

        # Appliquer la rotation si nécessaire
        for _ in range(rotation // 90):
            piece_shape = self.rotate_90(piece_shape)

        return piece_shape

    def apply_mirror(self, piece_shape):
        """
        Applique un miroir horizontal à la forme de la pièce.

        Args:
            piece_shape (list): La forme initiale de la pièce.

        Returns:
            list: La forme de la pièce après application du miroir.
        """
        return [row[::-1] for row in piece_shape]

    def rotate_90(self, piece_shape):
        """
        Fait une rotation de 90 degrés dans le sens horaire sur la forme de la pièce.

        Args:
            piece_shape (list): La forme initiale de la pièce.

        Returns:
            list: La forme de la pièce après la rotation de 90 degrés.
        """
        return [list(row) for row in zip(*piece_shape[::-1])]

    def check_piece_fits(self, state, row, col, piece_shape):
        """
        Vérifie si la forme de la pièce peut être placée à la position donnée sans dépasser du plateau
        et en respectant les limites.

        Args:
            state (list): Représentation de l'état actuel du plateau de jeu.
            row (int): La ligne de départ pour la vérification.
            col (int): La colonne de départ pour la vérification.
            piece_shape (list): La forme de la pièce à vérifier.

        Returns:
            bool: True si la pièce peut être placée dans l'espace spécifié, sinon False.
        """
        piece_height = len(piece_shape)
        piece_width = len(piece_shape[0])

        # Vérifier si la pièce dépasse du plateau
        if row + piece_height > len(state) or col + piece_width > len(state[0]):
            return False

        # Vérifier si l'espace est vide et entouré de pièces
        for i in range(piece_height):
            for j in range(piece_width):
                if piece_shape[i][j] == 1:  # La pièce occupe cette case
                    if state[row + i][col + j] != 0:  # Vérifier si l'espace est déjà occupé
                        return False

        return True
