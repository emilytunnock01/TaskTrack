##################################################  UI  ##################################################
def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate the position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")
