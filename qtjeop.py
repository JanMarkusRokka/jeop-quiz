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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hakillak")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QIcon("hakillak.ico"))
        self.player = QMediaPlayer()

        self.stack = QStackedWidget()
        self.selector = GameSelector(self.load_game)
        self.board = GameBoard(self.show_menu, self.show_image, self.player)
        self.image_display = ImageDisplay(self.go_to_game)

        self.stack.addWidget(self.selector)
        self.stack.addWidget(self.board)
        self.stack.addWidget(self.image_display)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    light_mode = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'light':
            light_mode = True

    if not light_mode:
        app.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    border : 2px solid;
                    border-color: #575862;
                    padding: 6px;
                    
                }
                QPushButton:hover {
                    background-color: #727173;
                    border-radius: 12px;              
                }
                            
                QPushButton:pressed {
                    background-color: #99989A;
                    border-radius: 12px;              
                }
                          
                QPushButton[class="overlayButton"] {
                    color: white;          
                }
                            
                QWidget {
                    background-color: #302F32;
                    color: white;
                }
                            """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())