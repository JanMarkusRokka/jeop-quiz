import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout,
    QStackedWidget
)
from PyQt5.QtGui import QIcon
from game_board import GameBoard
from game_selector import GameSelector
from PyQt5.QtMultimedia import QMediaPlayer
from image_display import ImageDisplay
from style_selector import StyleSelector
from config import Config
import os
import json

class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("Hakillak")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QIcon("hakillak.ico"))
        self.player = QMediaPlayer()

        self.stack = QStackedWidget()

        self.style_selector = StyleSelector(app, self.show_menu)
        self.selector = GameSelector(self.load_game, self.select_style)
        self.board = GameBoard(self.show_menu, self.show_image, self.player)
        self.image_display = ImageDisplay(self.go_to_game)

        self.stack.addWidget(self.selector)
        self.stack.addWidget(self.board)
        self.stack.addWidget(self.image_display)
        self.stack.addWidget(self.style_selector)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        Config.read('settings.json')
        self.style_selector.select_style(Config.style)

        self.show_menu()

    def load_game(self, path, edit_mode):
        self.board.load_game(path, edit_mode)
        self.stack.setCurrentWidget(self.board)
    
    def go_to_game(self):
        self.stack.setCurrentWidget(self.board)
        self.board.resize_images()

    def show_menu(self):
        self.selector.update_games()
        self.stack.setCurrentWidget(self.selector)
    
    def show_image(self, pixmap):
        self.image_display.show_image(pixmap)
        self.stack.setCurrentWidget(self.image_display)
    
    def select_style(self):
        self.stack.setCurrentWidget(self.style_selector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    skin = False

    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())