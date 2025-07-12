import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QStackedWidget, QScrollArea, QFrame, QCheckBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

font_size = 14

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

def delete_layout_recursive(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                delete_layout_recursive(child.layout())
        layout.deleteLater()

class DropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:  # Ensure it's a local file
                    self.setText(file_path)
            event.acceptProposedAction()

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
        self.select_label.setFont(QFont("Arial", font_size))
        self.select_label.setStyleSheet("color: 'white'")
        self.select_label.setText("Select mode:")
        self.select_label.setAlignment(Qt.AlignCenter)
        self.select_label.hide()

        self.play_button = QPushButton(self.overlay)
        self.play_button.setFont(QFont("Arial", font_size))
        self.play_button.setStyleSheet("color: 'white'")
        self.play_button.setText("Play")
        self.play_button.hide()

        self.edit_button = QPushButton(self.overlay)
        self.edit_button.setFont(QFont("Arial", font_size))
        self.edit_button.setStyleSheet("color: 'white'")
        self.edit_button.setText("Edit")
        self.edit_button.hide()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Select a game:")
        label.setFont(QFont("Arial", font_size))
        layout.addWidget(label)

        games = find_games()
        for name, path in games.items():
            button = QPushButton(name)
            button.setFont(QFont("Arial", font_size))
            button.clicked.connect(lambda _, p=path: self.select_mode(p))
            layout.addWidget(button)

        layout.addStretch()
        self.setLayout(layout)
    
    def hide_overlay(self):
        self.select_label.hide()
        self.play_button.hide()
        self.edit_button.hide()
        self.overlay.hide()

    def select_mode(self, path):
        self.select_label.show()
        self.play_button.show()
        self.edit_button.show()
        self.play_button.clicked.connect(lambda _, p=path: self.load_game(p, False))
        self.edit_button.clicked.connect(lambda _, p=path: self.load_game(p, True))
        self.overlay.show()
        self.center_overlay_elements()

    def load_game(self, path, edit_mode):
        self.hide_overlay()
        self.play_button.clicked.disconnect()
        self.edit_button.clicked.disconnect()
        self.load_game_callback(path, edit_mode)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.center_overlay_elements()
    
    def center_overlay_elements(self):
        self.select_label.move(
            (self.width() - self.select_label.width()) // 2,
            (self.height() - self.select_label.height()) // 2
        )
        self.play_button.move(
            (self.width() - self.select_label.width()) // 3,
            ((self.height() - self.select_label.height()) // 3) * 2
        )
        self.edit_button.move(
            ((self.width() - self.select_label.width()) // 3) * 2,
            ((self.height() - self.select_label.height()) // 3) * 2
        )

class Player:
    def __init__(self, name="", points=0):
        super().__init__()
        self.name = name
        self.points = points

    def setPoints(self, points):
        self.points = points

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

        self.layout.addWidget(self.grid_widget, 2)

        # Overlay
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        self.overlay.hide()

        self.play_label = QLabel(self.overlay)
        self.play_label.setFont(QFont("Arial", font_size))
        self.play_label.setStyleSheet("color: 'white'")
        self.play_label.setText("")
        self.play_label.setAlignment(Qt.AlignCenter)
        self.play_label.hide()

        self.input_field = QLineEdit(self.overlay)
        self.input_field.setFont(QFont("Arial", font_size))
        self.input_field.setFixedWidth(300)
        self.input_field.setStyleSheet("color: 'white'")
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.hide()

        self.file_drop = DropLabel(self.overlay)
        self.file_drop.setFont(QFont("Arial", font_size))
        self.file_drop.setText('Drop a file here:')
        self.file_drop.setStyleSheet("QLabel { color: white; background-color: black; border: 2px dashed gray; }")
        self.file_drop.setAlignment(Qt.AlignCenter)
        self.file_drop.hide()

        self.edit_mode = False
        self.teams_layout = None

        self.auto_save = False

        self.current_question = None
        self.input_field.returnPressed.connect(self.save_edit)
        #self.play_label.keyPressEvent = self.keyPressEvent

    def keyPressEvent(self, event):
        if not self.edit_mode and not self.play_label.isHidden():
            if event.key() == 16777220 or event.key == Qt.Key.Key_Enter :
                self.finish_play_field()
                print('enter')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.center_overlay()

    def center_overlay(self):
        self.input_field.move(
            (self.width() - self.input_field.width()) // 2,
            (self.height() - self.input_field.height()) // 2
        )
        self.file_drop.move(
            (self.width() - self.file_drop.width()) // 2,
            ((self.height() - self.file_drop.height()) * 2) // 3
        )
        self.play_label.move(
            (self.width() - self.play_label.width()) // 2,
            (self.height() - self.play_label.height()) // 2
        )

    def switch_autosave(self):
        self.auto_save = not self.auto_save

    def load_game(self, path, edit_mode):
        self.path = path
        self.edit_mode = edit_mode
        # Clear previous widgets
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        delete_layout_recursive(self.teams_layout)

        with open(path, 'r', encoding='utf-8') as f:
            self.current_data = json.load(f)

        self.category_buttons = {}
        # Back button
        back_btn = QPushButton("✖")
        back_btn.setFixedSize(40, 40)
        back_btn.clicked.connect(self.save)
        back_btn.clicked.connect(self.return_to_menu_callback)
        self.grid.addWidget(back_btn, 0, 0)
        autosave_checkmark = QCheckBox()
        autosave_checkmark.setText("♲")
        autosave_checkmark.setFixedSize(40, 40)
        autosave_checkmark.clicked.connect(self.switch_autosave)
        self.grid.addWidget(autosave_checkmark, 1, 0)

        categories = self.current_data["categories"]
        i = 0
        for col, cat_id in enumerate(categories.keys(), start=1):
            cat_title = categories[cat_id][0]

            cat_button = QPushButton(cat_title)

            cat_button.setFont(QFont("Arial", font_size))
            #cat_button.setFixedWidth(120)
            cat_button.setStyleSheet('text-align: center; white-space: normal;')
            if (self.edit_mode):
                cat_button.clicked.connect(lambda _, b=cat_button: self.edit_field(b))
                
            self.grid.addWidget(cat_button, 0, col)

            self.category_buttons[cat_button] = (cat_id, 0)

            questions = self.current_data["categories"][cat_id][1:]
            for row, question in enumerate(questions, start=1):
                q_button = QPushButton(str(question[0]))
                q_button.setFont(QFont("Arial", font_size))
                if (self.edit_mode):
                    q_button.setText(str(question[0]) + '\n' + wrap_text(question[1]))
                    q_button.clicked.connect(lambda _, b=q_button: self.edit_field(b))
                else:
                    q_button.clicked.connect(lambda _, b=q_button: self.play_field(b))
                    if (self.current_data['saved_games']['save1']['board_state'][col-1][row-1]):
                        q_button.setStyleSheet("background-color: darkgrey")
                self.grid.addWidget(q_button, row, col)
                self.category_buttons[q_button] = (cat_id, row)
                i = row

        if not self.edit_mode:
            self.team_buttons = []
            self.teams_layout = QHBoxLayout()
            #team_grid.setContentsMargins(10, 10, 10, 10)
            #team_grid.setSpacing(10)
            for id, team in enumerate(self.current_data['saved_games']['save1']['teams'], start=0):
                team_layout = QVBoxLayout()
                team_addsub_layout = QHBoxLayout()

                team_button = QPushButton(team[0] + " \n " + str(team[1]))
                team_button.setFont(QFont('Arial', font_size))
                team_layout.addWidget(team_button)

                team_button_add = QPushButton('+')
                team_button_sub = QPushButton('-')
                team_button_add.setFont(QFont('Arial', font_size))
                team_button_sub.setFont(QFont('Arial', font_size))
                team_button_add.clicked.connect(lambda _, tb=team_button, id=id: self.modify_points(id, tb))
                team_button_sub.clicked.connect(lambda _, tb=team_button, id=id: self.modify_points(id, tb, -1))
                team_addsub_layout.addWidget(team_button_add)
                team_addsub_layout.addWidget(team_button_sub)
                team_button_add.hide()
                team_button_sub.hide()
                self.team_buttons.append(team_button_add)
                self.team_buttons.append(team_button_sub)
                team_layout.addLayout(team_addsub_layout)

                self.teams_layout.addLayout(team_layout)
            self.layout.addLayout(self.teams_layout)

    def save(self):
        data = json.dumps(self.current_data, indent=4)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)


    def play_field(self, button):
        index = self.category_buttons[button]
        button.setStyleSheet("background-color: darkgrey")
        self.current_data['saved_games']['save1']['board_state'][int(index[0]) - 1][index[1]-1] = True
        self.play_label.setText(self.current_data['categories'][index[0]][index[1]][1])
        self.current_question = self.current_data['categories'][index[0]][index[1]]
        # if question has a file
        if len(self.current_question[2]) > 0:
            path = self.current_question[2]
            print(path[-4:])
        for team_button in self.team_buttons:
            team_button.show()
        self.overlay.show()
        self.play_label.show()
        self.center_overlay()
    
    def modify_points(self, team_id, button, multiplier=1):
        points = self.current_question[0]
        print(self.current_data['saved_games']['save1']['teams'][team_id][1], points)
        self.current_data['saved_games']['save1']['teams'][team_id][1] += points * multiplier
        team = self.current_data['saved_games']['save1']['teams'][team_id]
        button.setText(team[0] + " \n " + str(team[1]))
    
    def finish_play_field(self):
        self.play_label.setText('')
        for team_button in self.team_buttons:
            team_button.hide()
        if self.auto_save:
            self.save()
        self.overlay.hide()
        self.play_label.hide()

    def edit_field(self, button):
        index = self.category_buttons[button]
        changeable = self.current_data['categories'][index[0]][index[1]]
        if isinstance(changeable, str):
            self.input_field.setText(changeable)
        else:
            self.input_field.setText(changeable[1])
            self.file_drop.show()
            if len(changeable[2]) > 0:
                self.file_drop.setText(changeable[2])
            else:
                self.file_drop.setText('Drop a file here:')
        self.input_field.show()
        self.overlay.show()
        self.input_field.setFocus()
        self.editing_button = button
        self.center_overlay()

    def save_edit(self):
        new_text = self.input_field.text()
        button = self.editing_button
        index = self.category_buttons[button]

        if isinstance(self.current_data["categories"][index[0]][index[1]], str):
            if not new_text or new_text == self.current_data["categories"][index[0]][index[1]]:
                self.input_field.hide()
                self.overlay.hide()
                return
            button.setText(wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]] = new_text
        else:
            if not new_text or new_text == self.current_data["categories"][index[0]][index[1]][1]:
                self.input_field.hide()
                self.overlay.hide()
                self.file_drop.hide()
                return
            self.file_drop.hide()
            if (len(self.file_drop.text()) > 0):
                self.current_data["categories"][index[0]][index[1]][2] = self.file_drop.text()
            #self.file_drop.setText('')
            button.setText(str(self.current_data["categories"][index[0]][index[1]][0]) + '\n' + wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]][1] = new_text

        if self.auto_save:
            self.save()
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

    def load_game(self, path, edit_mode):
        self.board.load_game(path, edit_mode)
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