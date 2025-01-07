from _ai_.ai_solver import IQPuzzlerProXXL

class App(IQPuzzlerProXXL):
    """
    App class inherits from IQPuzzlerProXXL to create and run the puzzle game.
    This class initializes the game and runs the main event loop.
    """
    def __init__(self, update_ui=True):
        """
        Initializes the App class by calling the constructor of the parent class IQPuzzlerProXXL.
        This ensures that all functionality from IQPuzzlerProXXL is inherited by the App class.
        """
        super().__init__(update_ui=update_ui)  # Calling the parent class constructor to initialize the game
    
    # Additional functionality can be added here if needed, such as handling events, user interface, etc.

# Entry point of the application
if __name__ == "__main__":
    """
    This block checks if the script is being run directly (as the main program).
    If true, it creates an instance of the App class and starts the main event loop.
    """
    game = App(update_ui=False)  # Create an instance of the App class with UI updates disabled
    game.mainloop()  # Start the main event loop, keeping the game running
