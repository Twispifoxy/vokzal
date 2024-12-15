from PyQt6.QtWidgets import QApplication
from ui import App

if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec()
