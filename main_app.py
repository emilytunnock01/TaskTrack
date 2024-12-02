from ui_functions import center_window  # Import UI functions
from db_functions import initialize_database, initialize_weekly_view  # Import DB functions
import tkinter as tk  # Main tkinter module

def main():
   db_connection = initialize_database()
   initialize_weekly_view()    
  

if __name__ == "__main__":
    main()
