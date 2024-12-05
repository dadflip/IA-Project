from _ai_.ai_solver import IQPuzzlerProXXL

class App(IQPuzzlerProXXL):
    """
    App class inherits from IQPuzzlerProXXL to create and run the puzzle game.
    This class initializes the game and runs the main event loop.
    """
    def __init__(self):
        """
        Initializes the App class by calling the constructor of the parent class IQPuzzlerProXXL.
        This ensures that all functionality from IQPuzzlerProXXL is inherited by the App class.
        """
        super().__init__()  # Calling the parent class constructor to initialize the game
    
    # Additional functionality can be added here if needed, such as handling events, user interface, etc.

# Entry point of the application
if __name__ == "__main__":
    """
    This block checks if the script is being run directly (as the main program).
    If true, it creates an instance of the App class and starts the main event loop.
    """
    game = App()  # Create an instance of the App class
    game.mainloop()  # Start the main event loop, keeping the game running


"""
TODO List:

1. Contrôles de rotation des pièces : [x]
    - Permettre de faire pivoter une pièce en utilisant :
        a) La molette de la souris.
        b) Un bouton dédié sur le côté de l'interface.

2. Contrôles de miroir des pièces : [x]
    - Permettre de faire miroiter une pièce en utilisant :
        a) Un clic droit de la souris.
        b) Un bouton dédié sur le côté de l'interface.

3. Gestion des éléments ronds : [x]
    - Placer les éléments de forme ronde à l'extérieur de la grille principale.
"""
