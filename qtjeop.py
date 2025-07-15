import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout,
    QStackedWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer

from game_board import GameBoard
from game_selector import GameSelector

class Player:
    def __init__(self, name="", points=0):
        super().__init__()
        self.name = name
        self.points = points

    def setPoints(self, points):
        self.points = points

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hakillak")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QIcon("hakillak.ico"))

        self.stack = QStackedWidget()
        self.selector = GameSelector(self.load_game)
        self.board = GameBoard(self.show_menu)

        self.stack.addWidget(self.selector)
        self.stack.addWidget(self.board)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.show_menu()

    def load_game(self, path, edit_mode):
        self.board.load_game(path, edit_mode)
        self.stack.setCurrentWidget(self.board)

    def show_menu(self):
        self.selector.update_games()
        self.stack.setCurrentWidget(self.selector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton {
            background-color: light gray
        }
                      """)
    player = QMediaPlayer()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())