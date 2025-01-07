from copy import deepcopy
import tkinter as tk
from tkinter import messagebox
from matplotlib import colors


# Dimensions du plateau de jeu
BOARD_ROWS = 5
BOARD_COLS = 11
CELL_RADIUS = 30  # Rayon des cercles
CELL_PADDING = 10  # Espace entre les cercles
PIECE_COLORS = ["black", "green", "darkgrey", "lightblue", "blue", "brown", "orange", "red", "yellow", "pink", "turquoise", "olive"]
NOPE = []

PIECES = {
    'Bleu Noir': [[1, 1, 1], [1, 0, 0]],
    'Bleu Vert': [[1, 1, 1], [0, 1, 0]],
    'Noir': [[0, 1, 1], [1, 1, 0], [1, 0, 0]],
    'Bleu ciel': [[1, 1], [1, 0]],
    'Bleu foncé': [[1, 1, 1], [1, 0, 0], [1, 0, 0]],
    'Marron': [[0, 1, 1], [1, 1, 0]],
    'Orange': [[0, 0, 1], [1, 1, 1], [0, 1, 0]],
    'Rouge': [[1, 1, 1, 1], [1, 0, 0, 0]],
    'Jaune': [[1, 1, 1, 1], [0, 1, 0, 0]],
    'Rose': [[1, 1, 1, 0], [0, 0, 1, 1]],
    'Turquoise': [[1, 1, 1], [1, 1, 0]],
    'Kaki': [[1, 1, 1], [1, 0, 1]]
}

class IQPuzzlerProXXL(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IQ Puzzler Pro XXL")
        self.geometry(f"{BOARD_COLS * (CELL_RADIUS * 2 + CELL_PADDING)}x{(BOARD_ROWS + 2) * (CELL_RADIUS * 2 + CELL_PADDING)}")

        self.initial_colors = {}  # Nouveau dictionnaire pour stocker les couleurs initiales

        # Créer un canvas pour dessiner des cercles (plateau)
        self.canvas = tk.Canvas(self, width=BOARD_COLS * (CELL_RADIUS * 2 + CELL_PADDING),
                                height=BOARD_ROWS * (CELL_RADIUS * 2 + CELL_PADDING))
        self.canvas.pack(padx=10, pady=10)
        # Ajout d'un bind sur le survol de la souris
        self.canvas.bind("<Motion>", self.show_piece_preview)
        self.canvas.bind("<Leave>", self.destroy_preview)
        self.circles = []
        for row in range(BOARD_ROWS):
            row_circles = []
            for col in range(BOARD_COLS):
                x0 = col * (CELL_RADIUS * 2 + CELL_PADDING) + CELL_PADDING
                y0 = row * (CELL_RADIUS * 2 + CELL_PADDING) + CELL_PADDING
                x1 = x0 + CELL_RADIUS * 2
                y1 = y0 + CELL_RADIUS * 2
                circle = self.canvas.create_oval(x0, y0, x1, y1, fill="white", outline="black", width=2)
                self.canvas.tag_bind(circle, "<Button-1>", lambda e, r=row, c=col: self.cell_click(r, c))
                row_circles.append(circle)
            self.circles.append(row_circles)


        # Boutons pour contrôler le jeu
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)
        self.reset_button = tk.Button(self.button_frame, text="Réinitialiser", command=self.reset_board)
        self.reset_button.grid(row=0, column=0, padx=5)

        self.solve_button = tk.Button(self.button_frame, text="Résoudre", command=self.solve_game)
        self.solve_button.grid(row=0, column=1, padx=5)

        # Ajout des boutons Miroir et Pivoter
        self.mirror_button = tk.Button(self.button_frame, text="Miroir", command=self.mirror_piece)
        self.mirror_button.grid(row=0, column=2, padx=5)

        self.rotate_button = tk.Button(self.button_frame, text="Pivoter", command=self.rotate_piece)
        self.rotate_button.grid(row=0, column=3, padx=5)

        # Sélection des pièces en fonction de leur forme
        self.piece_frame = tk.Frame(self)
        self.piece_frame.pack(pady=10)
        self.pieces_available = {name: True for name in PIECES}  # Suivi des pièces déjà placées
        self.selected_piece = None
        self.preview_piece = None
        self.piece_canvases = {}  # Ajouter un dictionnaire pour les aperçus des pièces

        # Dessiner chaque pièce pour la sélection
        for i, (name, shape) in enumerate(PIECES.items()):
            piece_color = PIECE_COLORS[i]
            self.draw_piece_preview(self.piece_frame, shape, piece_color, name)

        self.reset_board()

    def show_piece_preview(self, event):
        """Affiche un aperçu de la pièce à l'emplacement de la souris."""
        if not self.selected_piece:
            return

        # Calcul des coordonnées de la cellule sous la souris
        col = (event.x - CELL_PADDING) // (CELL_RADIUS * 2 + CELL_PADDING)
        row = (event.y - CELL_PADDING) // (CELL_RADIUS * 2 + CELL_PADDING)

        # Vérifie si les coordonnées sont valides
        if row < 0 or row >= BOARD_ROWS or col < 0 or col >= BOARD_COLS:
            return

        # Efface les aperçus précédents
        self.hide_piece_preview(self.selected_piece, False)

        # Affiche l'aperçu de la pièce si elle peut être placée ici
        piece = PIECES[self.selected_piece]
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    if row + r >= BOARD_ROWS or col + c >= BOARD_COLS:
                        # en Dehors
                        print("dehors")
                    else:
                        current_color = self.canvas.itemcget(self.circles[row + r][col + c], "fill")
                        if current_color == "white":
                            self.canvas.itemconfig(self.circles[row + r][col + c], fill=self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5))
                        if current_color in PIECE_COLORS:
                            self.canvas.itemconfig(self.circles[row + r][col + c], fill=self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], self.canvas.itemcget(self.circles[row + r][col + c], "fill"), 0.5))
                            NOPE.append(self.canvas.create_text(40+70*(col+c), 40+70*(row+r), text="NOPE", fill="white", font=('Helvetica 12 bold')))

    def hide_piece_preview(self, piece_name, delete_all = True):
        for id_nope in NOPE:
            self.canvas.delete(id_nope)
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            if delete_all:
                piece_canvas.delete("all")  # Supprime tout le contenu graphique du canevas
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.canvas.itemcget(self.circles[r][c], "fill") == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                    self.canvas.itemconfig(self.circles[r][c], fill="white")
                for piece_color in PIECE_COLORS:
                    if self.canvas.itemcget(self.circles[r][c], "fill") == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], piece_color, 0.5):
                        self.canvas.itemconfig(self.circles[r][c], fill=piece_color)

    def destroy_preview(self, event):
        # Efface les aperçus précédents
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.selected_piece:
                    if self.canvas.itemcget(self.circles[r][c], "fill") == self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                        self.canvas.itemconfig(self.circles[r][c], fill="white")

    def name_to_rgb(self, color_name):
        try:
            rgb = colors.to_rgb(color_name)  # Retourne une valeur entre 0 et 1 pour chaque composant RGB
            return tuple(int(c * 255) for c in rgb)  # Conversion en valeurs entre 0 et 255
        except ValueError:
            print(f"Couleur '{color_name}' non reconnue.")
            return (0, 0, 0)  # Par défaut, renvoie noir en cas d'erreur

    def save_initial_colors(self):
        """Enregistre les couleurs initiales des cellules"""
        self.initial_colors = {}
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                current_color = self.canvas.itemcget(self.circles[row][col], "fill")
                self.initial_colors[(row, col)] = current_color

    def undo_color_blend(self):
        """Restaure les couleurs initiales du plateau"""
        if not self.initial_colors:
            messagebox.showwarning("Erreur", "Aucune modification à annuler.")
            return

        for (row, col), color in self.initial_colors.items():
            self.canvas.itemconfig(self.circles[row][col], fill=color)


    # Fonction pour calculer la couleur blendée, en utilisant des noms de couleur
    def blend_colors(self, color1_name, color2_name, alpha):
        self.save_initial_colors()
        color1 = self.name_to_rgb(color1_name)  # Convertir le premier nom de couleur en RGB
        color2 = self.name_to_rgb(color2_name)  # Convertir le deuxième nom de couleur en RGB

        r1, g1, b1 = color1
        r2, g2, b2 = color2

        # Calcul des nouvelles valeurs RGB après mélange
        r = int(r1 * (1 - alpha) + r2 * alpha)
        g = int(g1 * (1 - alpha) + g2 * alpha)
        b = int(b1 * (1 - alpha) + b2 * alpha)

        # Retourne la couleur mixée sous forme hexadécimale
        return f'#{r:02x}{g:02x}{b:02x}'



    def draw_piece_preview(self, parent, shape, color, piece_name):
        pieces_per_row = 6
        piece_index = list(PIECES.keys()).index(piece_name)
        row = piece_index // pieces_per_row
        col = piece_index % pieces_per_row

        piece_canvas = tk.Canvas(parent, width=40 * len(shape[0]), height=61 * len(shape),
                                  highlightthickness=0, bg=self.cget("background"))
        piece_canvas.grid(row=row, column=col, padx=5, pady=5)

        self.piece_canvases[piece_name] = piece_canvas

        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell == 1:
                    x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                    y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                    x1 = x0 + CELL_RADIUS
                    y1 = y0 + CELL_RADIUS
                    piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)

        piece_canvas.bind("<Button-1>", lambda e, n=piece_name: self.select_piece(n))




    def highlight_piece_preview(self, piece_name, highlight=True):
        # Change la couleur de la pièce pour la rendre plus claire lorsqu'elle est sélectionnée
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            color = PIECE_COLORS[list(PIECES.keys()).index(piece_name)]
            if highlight:
                lighter_color = self.blend_colors(color, 'grey', 0.5)  # Utilisation correcte de blend_colors
            else:
                lighter_color = color
            piece_canvas.delete("all")  # Efface le canevas pour redessiner
            shape = PIECES[piece_name]

            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=lighter_color, outline="black", width=2)



    def reset_board(self):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                self.canvas.itemconfig(self.circles[row][col], fill="white")  # Remet tout en blanc
        self.selected_piece = None
        self.preview_piece = None
        self.pieces_available = {name: True for name in PIECES}
        self.reset_piece_previews()


    def reset_piece_previews(self):
        for name in PIECES.keys():
            piece_canvas = self.piece_canvases[name]
            piece_canvas.delete("all")  # Effacer tout le contenu
            color = PIECE_COLORS[list(PIECES.keys()).index(name)]
            shape = PIECES[name]

            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)
            self.pieces_available[name] = True

    def cell_click(self, row, col):
        # Gestion du clic sur une cellule du plateau pour placer la pièce.
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            if self.can_place_piece(piece, row, col):
                self.place_piece(piece, row, col)
            else:
                self.hide_piece_preview(self.selected_piece, False)
                messagebox.showwarning("Erreur", "Impossible de placer la pièce ici.")
        else:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord une pièce.")

    def select_piece(self, piece_name):
        # Sélectionne une pièce pour la placer sur le plateau.
        if self.pieces_available[piece_name]:
            # Rendre la pièce précédemment sélectionnée opaque
            if self.selected_piece:
                self.highlight_piece_preview(self.selected_piece, highlight=False)


            # Mettre en surbrillance la pièce nouvellement sélectionnée
            self.selected_piece = piece_name
            self.highlight_piece_preview(piece_name, highlight=True)
            #print(f"Pièce sélectionnée: {self.selected_piece}")
        else:
            messagebox.showwarning("Erreur", "Cette pièce a déjà été placée.")


    def can_place_piece(self, piece, row, col):
        # Vérifie si une pièce peut être placée à la position spécifiée.
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    if row + r >= BOARD_ROWS or col + c >= BOARD_COLS:
                        return False
                    current_color = self.canvas.itemcget(self.circles[row + r][col + c], "fill")
                    if current_color != "white" and current_color != self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)], "white", 0.5):
                        return False
        return True

    def place_piece(self, piece, row, col):
        self.pieces_available[self.selected_piece] = False
        piece_color = PIECE_COLORS[list(PIECES.keys()).index(self.selected_piece)]
        for r, row_piece in enumerate(piece):
            for c, cell in enumerate(row_piece):
                if cell == 1:
                    self.canvas.itemconfig(self.circles[row + r][col + c], fill=piece_color)

        self.hide_piece_preview(self.selected_piece)  # Masquer la pièce après placement
        self.selected_piece = None

    def rotate_piece(self):
        """Pivote la pièce sélectionnée dans le sens horaire."""
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            # Rotation en pivotant la matrice
            rotated_piece = [list(row) for row in zip(*piece[::-1])]
            PIECES[self.selected_piece] = rotated_piece
            self.update_piece_preview(self.selected_piece)
        else:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord une pièce à pivoter.")

    def mirror_piece(self):
        """Applique une symétrie horizontale (miroir) à la pièce sélectionnée."""
        if self.selected_piece:
            piece = PIECES[self.selected_piece]
            # Miroir en inversant chaque ligne
            mirrored_piece = [row[::-1] for row in piece]
            PIECES[self.selected_piece] = mirrored_piece
            self.update_piece_preview(self.selected_piece)
        else:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord une pièce à miroiter.")

    def update_piece_preview(self, piece_name):
        """Met à jour l'aperçu d'une pièce après transformation."""
        if piece_name in self.piece_canvases:
            piece_canvas = self.piece_canvases[piece_name]
            piece_canvas.delete("all")  # Effacer tout le contenu
            color = self.blend_colors(PIECE_COLORS[list(PIECES.keys()).index(piece_name)], "grey", 0.5)
            shape = PIECES[piece_name]

            for r, row in enumerate(shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        x0 = c * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        y0 = r * (CELL_RADIUS + CELL_PADDING) + CELL_PADDING
                        x1 = x0 + CELL_RADIUS
                        y1 = y0 + CELL_RADIUS
                        piece_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)


    def different_piece(self, piece):
        # return les différent variation d'une piece rotation + miroire
        Piece_variation = []
        miror_piece = [row[::-1] for row in piece]
        var_piece = [piece, miror_piece]
        for k in range(4):
            for i in range(2):
                temp_piece = [list(row) for row in zip(*var_piece[i][::-1])]
                var_piece[i] = temp_piece
                if temp_piece not in Piece_variation:
                    Piece_variation.append(temp_piece)
        return Piece_variation

    def where_place(self, piece, id_piece):
        Where_piece = []
        Var_piece = self.different_piece(piece)
        for piece in Var_piece:
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if self.can_place_piece(piece, row, col):
                        Where_piece.append([piece, row, col, id_piece])
        return Where_piece

    def brute_force_init(self, Piece):
        #Récupère la grille
        Grille = []
        for r in range(BOARD_ROWS):
            Grille.append([])
            for c in range(BOARD_COLS):
                current_color = self.canvas.itemcget(self.circles[r][c], "fill")
                if current_color != "white":
                    Grille[-1].append(1)
                else:
                    Grille[-1].append(0)

        #on récupère toutes le différente possibilité de placement pour chaque piece avec leur différent orientation
        Where = []
        for piece in range(len(Piece)):
            Where += self.where_place(Piece[piece], piece)
        return Grille, Where

    def coabite(self, Piece1, Piece2):
        # permet de savoir si deux piece peuvent se géner (ne prend pas en compte les piece déjà placer sur la grille)
        if Piece1[3] == Piece2[3]:
            return False
        for row1 in range(len(Piece1[0])):
            for col1 in range(len(Piece1[0][row1])):
                for row2 in range(len(Piece2[0])):
                    for col2 in range(len(Piece2[0][row2])):
                        #si les deux se superpose en se point
                        if Piece1[1] + row1 == Piece2[1] + row2 and Piece1[2] + col1 == Piece2[2] + col2:
                            #si à ce point les deux pieces sont remplie
                            if Piece1[0][row1][col1] == Piece2[0][row2][col2] == 1:
                                return False
        return True

    def brute_force_recurs(self, Grille, Where):
        #test si on a déjà résolut la grille
        test = 0
        for k in range(len(Grille)):
            if 0 in Grille[k] :
                test = 1
        if test == 0:
            return [0] #on renvoie pas une liste vide car compris comme False


        #test si solution impossible
        if len(Where) == 0:
            return False

        #met la piece dans la grille
        new_Grille = deepcopy(Grille)
        for row in range(len(Where[0][0])):
            for col in range(len(Where[0][0][row])):
                new_Grille[row+Where[0][1]][col+Where[0][2]] += Where[0][0][row][col]

        #met à jour Where avec la piece placer
        new_Where = deepcopy(Where)
        for k in range(len(new_Where)-1, -1, -1):
            if not self.coabite(new_Where[0], new_Where[k]):
                del new_Where[k]

        #si on trouve la soluce on la retourne sinon on recommence sans utiliser la piece
        Test = self.brute_force_recurs(new_Grille, new_Where)
        if Test :
            Test.append(Where[0])
            return Test
        else:
            del Where[0]
            return self.brute_force_recurs(Grille, Where)

    def find_piece(self, Piece):
        id_piece = -1
        for name, available in self.pieces_available.items():
            piece = PIECES[name]
            id_piece += 1
            if available:
                #les piece ont la même taille de matrice
                if len(Piece) + len(Piece[0]) == len(piece) + len(piece[0]):
                    if Piece in self.different_piece(piece):
                        return name


    def brute_force_solving(self, Piece):
        Grille, Where = self.brute_force_init(Piece)

        #on priorise les pieces qui créer le moins de gène
        Soluce = self.brute_force_recurs(Grille, Where)
        if Soluce:
            del Soluce[0]#on suprime le zéro au début
            for k in range(len(Soluce)):
                self.select_piece(self.find_piece(Soluce[k][0]))
                self.place_piece(Soluce[k][0], Soluce[k][1], Soluce[k][2])
        return Soluce


    def solve_game(self):
        # Affiche un message pour dire que la solution sera implémentée.
        #messagebox.showinfo("Résoudre", "La solution n'est pas encore implémentée!")

        #on récupère les pièce qui reste à placer
        Piece = []
        for piece, available in self.pieces_available.items():
            if available:
                Piece.append(PIECES[piece])


        if self.brute_force_solving(Piece) :
            return True
        else:
            return False

if __name__ == "__main__":
    game = IQPuzzlerProXXL()
    game.mainloop()


