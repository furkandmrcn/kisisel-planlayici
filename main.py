import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from database import DatabaseManager

def main():
    db_manager = DatabaseManager('planner.db')
    app = MainWindow(db_manager)
    app.mainloop()

if __name__ == "__main__":
    main()