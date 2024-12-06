def transform_to_matrix(board_state):
    # Créez une matrice vide pour stocker les résultats
    matrix = []
    
    for row in board_state:
        matrix_row = []
        for cell in row:
            # Si la case est une pièce, on met 1, sinon 0
            if isinstance(cell, dict) and 'piece' in cell:
                matrix_row.append(1)
            else:
                matrix_row.append(0)
        matrix.append(matrix_row)
    
    # Affichage de la matrice sous forme rectangulaire
    for row in matrix:
        print(" ".join(map(str, row)))
    
    # Retourner la matrice
    return matrix
