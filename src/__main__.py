# This file allows the package to be run as a script
# python -m src

import sys
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except IOError as e:
        print(f"FATAL ERROR: {e}")
        print("Please ensure 'assets/haarcascade_frontalface_default.xml' exists.")
        print("Run the execute.sh script to download it.")
        sys.exit(1)

if __name__ == "__main__":
    main()
