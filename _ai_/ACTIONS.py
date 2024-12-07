from colorama import Fore, Style
from _ui_.piece import PieceTransformation
from constants import BOARD_COLS, BOARD_ROWS, PIECES

# Classe de base pour Endpoint qui hérite de PieceTransformation
class Entry(PieceTransformation):
    def __init__(self):
        super().__init__()

# Classe READ qui gère l'accès aux états du jeu
class READ(Entry):
    def __init__(self):
        super().__init__()
        
    def get_board_state(self):
        return self.board_state

    def get_available_pieces(self):
        return [name for name, available in self.pieces_available.items() if available]
    
    def get_placed_pieces(self):
        return [name for name, placed in self.pieces_on_the_grid.items() if placed]
    
    def get_game_state(self):
        state = {
            'board_state': self.board_state,
            'piece_states': self.piece_states,
            'pieces_available': self.pieces_available,
            'pieces_on_the_grid': self.pieces_on_the_grid,
            'selected_piece': self.selected_piece,
            'preview_piece': self.preview_piece,
        }
        return state

    def get_possible_moves(self, piece_name, board_state, state_history, excluded_moves):
        """
        Returns the possible moves (placement, move, remove) for a given piece,
        considering transformations and excluding blocked moves.
        """
        piece = PIECES.get(piece_name)
        self.selected_piece = piece_name
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")

        transformations = [lambda: None]  # Original form (no transformation)
        transformations += [self.rotate_piece for _ in range(3)]  # 90°, 180°, 270°

        moves = []

        # ---- Part 1: Generate possible placements ----
        for rotation_index, rotate in enumerate(transformations):
            if rotate != transformations[0]:
                rotate()

            for mirrored in [False, True]:
                if mirrored:
                    self.mirror_piece()

                for row in range(BOARD_ROWS):
                    for col in range(BOARD_COLS):
                        if self.can_place_piece_depending_board(piece_name, row, col, board_state):
                            if not self.is_space_occupied(piece_name, row, col, board_state):
                                move = ('place', row, col, piece_name,
                                        self.get_piece_rotation(piece_name),
                                        "mirrored" if mirrored else "original")
                                if (board_state, move) not in excluded_moves:
                                    moves.append(move)

                if mirrored:
                    self.mirror_piece()

        # ---- Part 2: Generate possible removals ----
        for prev_state, prev_move, reward in state_history:
            if prev_move[0] == 'place':  # Only remove placed pieces
                row, col, prev_piece, _, _ = prev_move[1:]
                remove_move = ('remove', row, col, prev_piece)
                if (board_state, remove_move) not in excluded_moves:
                    moves.append(remove_move)

        # ---- Part 3: Generate possible moves (displacements) ----
        for prev_state, prev_move, reward in state_history:
            if prev_move[0] == 'place':  # Only move placed pieces
                prev_row, prev_col, prev_piece, _, prev_mirror = prev_move[1:]
                for row in range(BOARD_ROWS):
                    for col in range(BOARD_COLS):
                        if self.can_place_piece_depending_board(prev_piece, row, col, board_state):
                            if not self.is_space_occupied(prev_piece, row, col, board_state):
                                move_move = ('move', prev_row, prev_col, row, col, prev_piece,
                                            self.get_piece_rotation(prev_piece),
                                            prev_mirror)
                                if (board_state, move_move) not in excluded_moves:
                                    moves.append(move_move)

        return moves

    def is_space_occupied(self, piece_name, row, col, board_state):
        """
        Vérifie si l'espace spécifié sur le plateau est déjà occupé par une pièce.
        """
        piece = PIECES.get(piece_name)
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")
        
        piece_height = len(piece)
        piece_width = len(piece[0])

        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:
                    board_row = row + i
                    board_col = col + j
                    if 0 <= board_row < BOARD_ROWS and 0 <= board_col < BOARD_COLS:
                        if board_state[board_row][board_col] != 0:  # Si une autre pièce est déjà là
                            return True
                    else:
                        return True  # Hors des limites du plateau
        return False

# Classe WRITE qui applique les mouvements sur le plateau
class WRITE(READ):
    def __init__(self):
        super().__init__()
        
    def move_piece(self, piece_name, new_position):
        """
        Déplace une pièce existante vers une nouvelle position.
        """
        self.select_piece(piece_name)
        # self.remove_piece_by_name(piece_name)
        # Supprime d'abord la pièce de son emplacement actuel
        for r in range(len(self.board_state)):
            for c in range(len(self.board_state[r])):
                if self.board_state[r][c] and self.board_state[r][c]['piece'] == piece_name:
                    self.canvas.itemconfig(self.circles[r][c], fill='white')
                    self.board_state[r][c] = 0

        # Place la pièce à la nouvelle position
        piece_shape = PIECES[piece_name]
        self.place_piece(piece_shape, new_position[0], new_position[1])
        print(f"Pièce '{piece_name}' déplacée à la position {new_position}.")
        self.update_visual_grid()
        self.canvas.update()

        
    def set_move(self, state, piece_name, action):
        # Extraction des informations de l'action
        action_type = action[0]  # 'place', 'move' ou 'remove'
        
        # Récupérer la pièce correspondante
        self.select_piece(piece_name)
        piece = PIECES.get(piece_name)
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")
        
        print(f"Action reçue: {action_type} - {action}")
        print(f"Piece actuelle: {piece_name}")

        # Si l'action est 'remove' (suppression d'une pièce)
        if action_type == 'remove':
            row, col, removed_piece = action[1], action[2], action[3]
            print(f"Tentative de suppression de la pièce '{removed_piece}' à ({row}, {col})")
            
            # Vérification de la validité de la suppression
            if self.can_remove_piece_by_name(removed_piece):
                print("Suppression de la pièce...")
                self.remove_piece_by_name(removed_piece)
                new_state = self.get_board_state()
                self.pieces_available[removed_piece] = True
            else:
                print(f"Impossible de supprimer la pièce à ({row}, {col})")
                new_state = state

        # Si l'action est 'place' (placement d'une pièce)
        elif action_type == 'place':
            row, col = action[1], action[2]
            print(f"Tentative de placement de la pièce '{piece_name}' à ({row}, {col})")
            
            # Vérification de la validité du placement
            if not self.can_place_piece(piece, row, col):
                print("L'emplacement est déjà occupé ou la pièce est hors grille")
                new_state = state
            else:
                print("Placement de la pièce...")
                self.place_piece(piece, row, col)
                new_state = self.get_board_state()
                self.pieces_available[piece_name] = False

        # Si l'action est 'move' (déplacement d'une pièce)
        elif action_type == 'move':
            prev_row, prev_col, new_row, new_col, moved_piece, rotation, mirror = action[1:]
            print(f"Tentative de déplacement de la pièce '{moved_piece}' de ({prev_row}, {prev_col}) à ({new_row}, {new_col})")
            
            # Vérification de la validité du déplacement
            if not self.can_move_piece(moved_piece, new_row, new_col, state):
                print("Le déplacement est invalide")
                new_state = state
            else:
                print("Déplacement de la pièce...")
                new_pos = (new_row, new_col)
                self.move_piece(moved_piece, new_pos)
                new_state = self.get_board_state()

        else:
            raise ValueError(f"Action '{action_type}' non reconnue.")
        
        return new_state


# Classe DISPLAY qui gère l'affichage du jeu
class DISPLAY():
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

# Classe CHECK qui vérifie les actions
class CHECK():
    def is_solution(self, state):
        # print("Solution State:", state)
        return all(cell != 0 for row in state for cell in row)

    def is_invalid_action(self, state, action):
        # Détermine le type d'action à partir du premier élément
        act = action[0]

        # Vérifiez l'action "place"
        if act == 'place':
            if len(action) != 6:
                raise ValueError(f"Action 'place' doit contenir 6 éléments, mais trouvé {len(action)} : {action}")
            _, row, col, piece_name, rotation, mirror = action
            if state[row][col] == 1:
                return True

        # Vérifiez l'action "move"
        elif act == 'move':
            if len(action) != 8:
                raise ValueError(f"Action 'move' doit contenir 8 éléments, mais trouvé {len(action)} : {action}")
            _, old_row, old_col, new_row, new_col, piece_name, rotation, mirror = action
            if state[new_row][new_col] == 1:  # Vérifiez si la nouvelle position est valide
                return True

        # Vérifiez l'action "remove"
        elif act == 'remove':
            if len(action) != 4:
                raise ValueError(f"Action 'remove' doit contenir 4 éléments, mais trouvé {len(action)} : {action}")
            _, row, col, piece_name = action
            if state[row][col] == 0:  # Vérifiez si la case est vide avant de retirer une pièce
                return True

        # Si l'action est inconnue ou n'est pas valide
        return False
    
    def is_valid_move(self, state, piece_name, row, col):
        """
        Vérifie si un déplacement est valide.

        Args:
            state (list): État actuel du plateau de jeu.
            piece_name (str): Nom de la pièce à déplacer.
            row (int): Ligne cible du déplacement.
            col (int): Colonne cible du déplacement.

        Returns:
            bool: True si le déplacement est valide, False sinon.
        """
        piece = PIECES.get(piece_name)
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")

        piece_height = len(piece)  # Hauteur de la pièce (nombre de lignes)
        piece_width = len(piece[0])  # Largeur de la pièce (nombre de colonnes)

        # Vérifiez que la pièce reste dans les limites du plateau après le déplacement
        if row + piece_height > len(state) or col + piece_width > len(state[0]):
            return False

        # Vérifiez si les cellules cibles sur le plateau sont libres
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:  # Si la cellule de la pièce est occupée
                    if state[row + i][col + j] != 0:  # Vérifiez que la cellule sur le plateau est libre
                        return False

        return True
    
    def is_valid_remove(self, state, piece_name, row, col):
        """
        Vérifie si une action de suppression est valide.

        Args:
            state (list): État actuel du plateau.
            piece_name (str): Nom de la pièce à retirer.
            row (int): Position en ligne de la pièce sur le plateau.
            col (int): Position en colonne de la pièce sur le plateau.

        Returns:
            bool: True si la suppression est valide, sinon False.
        """
        piece = PIECES.get(piece_name)
        if not piece:
            raise ValueError(f"La pièce '{piece_name}' n'existe pas.")

        # Vérifiez si la pièce existe dans l'état actuel
        for row_offset in range(len(piece)):  # Itère sur les lignes
            for col_offset in range(len(piece[row_offset])):  # Itère sur les colonnes de chaque ligne
                if piece[row_offset][col_offset] == 1:  # Si la case de la pièce est occupée
                    board_row = row + row_offset
                    board_col = col + col_offset

                    # Vérifiez si les coordonnées sont valides
                    if not (0 <= board_row < len(state) and 0 <= board_col < len(state[0])):
                        return False  # Une partie de la pièce est en dehors des limites

                    # Vérifiez si la position correspond à la pièce à supprimer
                    if state[board_row][board_col] != 1:  # Supposons que 1 représente une cellule occupée par une pièce
                        return False

        # Vérifiez qu'il n'y a pas d'autres dépendances qui rendent la suppression invalide
        # Exemple : une suppression ne doit pas casser des contraintes (à personnaliser selon le jeu)
        if not self.can_remove_without_breaking(state, piece_name, row, col):
            return False

        return True

    def can_remove_without_breaking(self, state, piece_name, row, col):
        """
        Vérifie si la suppression de la pièce ne casse pas une règle ou une contrainte.

        Args:
            state (list): État actuel du plateau.
            piece_name (str): Nom de la pièce.
            row (int): Position en ligne de la pièce.
            col (int): Position en colonne de la pièce.

        Returns:
            bool: True si la suppression est valide, sinon False.
        """
        # Implémentation par défaut : pas de contraintes supplémentaires
        # Ajoutez ici des règles spécifiques si nécessaire, par exemple :
        # - Vérifier qu'une suppression ne divise pas une solution en plusieurs parties non connectées
        # - Vérifier qu'une suppression ne bloque pas d'autres pièces

        return True  # Suppression par défaut valide




class Endpoint(WRITE):
    def __init__(self):
        super().__init__()
        
    def is_blocked(self, state):
        """
        Vérifie si un état de jeu est bloqué (c'est-à-dire si un mouvement ou une configuration
        du plateau est invalide, par exemple si une pièce chevauche une autre ou dépasse les limites).
        """
        for row in range(len(state)):  # Parcours chaque ligne de l'état
            for col in range(len(state[row])):  # Parcours chaque colonne de la ligne
                if state[row][col] != 0:  # Si une case est occupée (par une pièce)
                    # Vérifiez si cette case entre en collision avec une autre pièce ou dépasse les limites
                    if self.board_state[row][col] != 0:  # Collision avec une autre pièce
                        return True  # Si collision, état bloqué

        # Si on ne trouve pas de collisions, le mouvement est valide
        return False

