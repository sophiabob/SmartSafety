"""
Точка входа в приложение SafetyVision.
"""
import sys
from PyQt5.QtWidgets import QApplication

# Импортируем главное окно
from src.gui.main_window import MainWindow


def main():
    """Запускает приложение."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()