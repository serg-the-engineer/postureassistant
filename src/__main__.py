# This file allows the package to be run as a script
# python -m src

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from .main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/vibestand.png"))
    app.setApplicationName("Vibestand")
    app.setApplicationVersion("1.0.0")
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
