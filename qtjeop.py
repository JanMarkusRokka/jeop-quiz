import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QStackedWidget, QScrollArea, QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


def find_games():
    games = {}
    for file in os.listdir('./games/'):
        if file.endswith('.json'):
            games[file[:-5]] = os.path.join('./games/', file)
    return games

def wrap_text(text, max_line_length=15):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        if len(line + word) <= max_line_length:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    return "\n".join(lines)

class GameSelector(QWidget):
    def __init__(self, load_game_callback):
        super().__init__()
        self.load_game_callback = load_game_callback
        self.init_ui()
        # Overlay
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        self.overlay.hide()

        self.select_label = QLabel(self.overlay)
        self.select_label.setFont(QFont("Arial", 12))
        self.select_label.setStyleSheet("color: 'white'")
        self.select_label.setText("Select mode:")
        self.select_label.setAlignment(Qt.AlignCenter)
        self.select_label.hide()

        self.play_button = QPushButton(self.overlay)
        self.play_button.setFont(QFont("Arial", 12))
        self.play_button.setText("Play") # fix placement
        self.play_button.hide()

        self.edit_button = QPushButton(self.overlay)
        self.edit_button.setFont(QFont("Arial", 12))
        self.edit_button.setText("Edit") # fix placement
        self.edit_button.hide()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Select a game:")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)

        games = find_games()
        for name, path in games.items():
            button = QPushButton(name)
            button.setFont(QFont("Arial", 12))
            button.clicked.connect(lambda _, p=path: self.select_mode(p))
            layout.addWidget(button)

        layout.addStretch()
        self.setLayout(layout)
    
    def select_mode(self, path):
        self.select_label.show()
        self.play_button.show()
        self.edit_button.show()
        #button.clicked.connect(lambda _, p=path: self.load_game_callback(p))
        self.overlay.show()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.center_overlay_elements()
    
    def center_overlay_elements(self):
        self.select_label.move(
            (self.width() - self.select_label.width()) // 2,
            (self.height() - self.select_label.height()) // 2
        )

class GameBoard(QWidget):
    def __init__(self, return_to_menu_callback):
        super().__init__()
        self.return_to_menu_callback = return_to_menu_callback
        self.current_data = None

        # Main layout
        self.layout = QVBoxLayout(self)
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)

        self.layout.addWidget(self.grid_widget)

        # Overlay
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        self.overlay.hide()

        self.input_field = QLineEdit(self.overlay)
        self.input_field.setFont(QFont("Arial", 12))
        self.input_field.setFixedWidth(300)
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.hide()
        self.edit_mode = False

        self.input_field.returnPressed.connect(self.save_edit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.center_input()

    def center_input(self):
        self.input_field.move(
            (self.width() - self.input_field.width()) // 2,
            (self.height() - self.input_field.height()) // 2
        )

    def load_game(self, path):
        # Clear previous widgets
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        with open(path, 'r', encoding='utf-8') as f:
            self.current_data = json.load(f)

        self.category_buttons = {}
        # Back button
        back_btn = QPushButton("✖")
        back_btn.setFixedSize(40, 40)
        back_btn.clicked.connect(self.return_to_menu_callback)
        self.grid.addWidget(back_btn, 0, 0)

        categories = self.current_data["categories"]

        for col, cat_id in enumerate(categories.keys(), start=1):
            cat_title = categories[cat_id][0]

            cat_button = QPushButton(cat_title)
            cat_button.setFont(QFont("Arial", 11))
            #cat_button.setFixedWidth(120)
            cat_button.setStyleSheet('text-align: center; white-space: normal;')
            if (self.edit_mode):
                cat_button.clicked.connect(lambda _, b=cat_button: self.edit_field(b))
                
            self.grid.addWidget(cat_button, 0, col)

            self.category_buttons[cat_button] = (cat_id, 0)

            questions = self.current_data["categories"][cat_id][1:]
            for row, question in enumerate(questions, start=1):
                q_button = QPushButton(str(question[0]))
                q_button.setFont(QFont("Arial", 10))
                if (self.edit_mode):
                    q_button.clicked.connect(lambda _, b=q_button: self.edit_field(b))
                else:
                    q_button.clicked.connect(lambda _, b=q_button: self.play_field(b))
                    if (self.current_data['saved_games']['save1']['board_state'][col-1][row-1]):
                        q_button.setStyleSheet("background-color: darkgrey")
                self.grid.addWidget(q_button, row, col)
                self.category_buttons[q_button] = (cat_id, row)

    def play_field(self, button):
        print('play field')

    def edit_field(self, button):
        index = self.category_buttons[button]
        self.input_field.setText(self.current_data['categories'][index[0]][index[1]])
        self.input_field.show()
        self.overlay.show()
        self.input_field.setFocus()
        self.editing_button = button
        self.center_input()

    def save_edit(self):
        new_text = self.input_field.text()
        button = self.editing_button
        index = self.category_buttons[button]

        if not new_text or new_text == self.current_data["categories"][index[0]][index[1]]:
            self.input_field.hide()
            self.overlay.hide()
            return

        button.setText(wrap_text(new_text))
        self.current_data['categories'][index[0]][index[1]] = new_text

        self.input_field.hide()
        self.overlay.hide()
        print(self.current_data)


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

    def load_game(self, path):
        self.board.load_game(path)
        self.stack.setCurrentWidget(self.board)

    def show_menu(self):
        self.stack.setCurrentWidget(self.selector)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# Add this structure for money/points   "categories": {
#    "1": ["CategoryTitle1", [100, "Kas ja kuidas ja kas ja kuidas ja kas?"], [200, "Kes?"], [300, "Kus?"], [400, "Millal"], [500, "Milleks?"]],
# Make buttons scale better - for later, first focus on main mechanics