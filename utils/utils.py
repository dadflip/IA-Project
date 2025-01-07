def transform_to_matrix(board_state):
    # Create an empty matrix to store the results
    matrix = []
    
    for row in board_state:
        matrix_row = []
        for cell in row:
            # If the cell is a piece, put 1, otherwise 0
            if isinstance(cell, dict) and 'piece' in cell:
                matrix_row.append(1)
            else:
                matrix_row.append(0)
        matrix.append(matrix_row)
    
    # Display the matrix in rectangular form
    for row in matrix:
        print(" ".join(map(str, row)))
    
    # Return the matrix
    return matrix
