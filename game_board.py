import json
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from drop_label import DropLabel
from play_stop_button import PlayStopButton
from config import Config, delete_layout_recursive, wrap_text
from video_player_button import VideoPlayerButton

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
        self.play_label.setFont(QFont("Arial", Config.font_size))
        self.play_label.setStyleSheet("color: 'white'")
        self.play_label.setText("")
        self.play_label.setAlignment(Qt.AlignCenter)
        self.play_label.hide()

        self.answer_label = QLabel(self.overlay)
        self.answer_label.setFont(QFont("Arial", Config.font_size))
        self.answer_label.setStyleSheet("color: 'white'")
        self.answer_label.setText("")
        self.answer_label.setAlignment(Qt.AlignCenter)
        self.answer_label.hide()

        self.input_field = QLineEdit(self.overlay)
        self.input_field.setFont(QFont("Arial", Config.font_size))
        self.input_field.setFixedWidth(300)
        self.input_field.setStyleSheet("color: 'white'")
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.hide()

        self.input_field_answer = QLineEdit(self.overlay)
        self.input_field_answer.setFont(QFont("Arial", Config.font_size))
        self.input_field_answer.setFixedWidth(300)
        self.input_field_answer.setStyleSheet("color: 'white'")
        self.input_field_answer.setAlignment(Qt.AlignCenter)
        self.input_field_answer.hide()

        self.file_drop = DropLabel(self.overlay)
        self.file_drop.setFont(QFont("Arial", Config.font_size))
        self.file_drop.setText('Drop a file here:')
        self.file_drop.setStyleSheet("QLabel { color: white; background-color: black; border: 2px dashed gray; }")
        self.file_drop.setAlignment(Qt.AlignCenter)
        self.file_drop.hide()

        self.remove_button = QPushButton(self.overlay)
        self.remove_button.setFont(QFont("Arial", Config.font_size))
        self.remove_button.setText('Remove')
        self.remove_button.setStyleSheet('color: white')
        self.remove_button.hide()
        
        self.font_update = [self.play_label, self.answer_label, self.input_field, self.file_drop, self.remove_button]

        self.file_showcase = None

        self.edit_mode = False
        self.teams_layout = None

        self.auto_save = True

        self.current_question = None
        self.current_image = None
        self.input_field.returnPressed.connect(self.save_edit)
        self.input_field_answer.returnPressed.connect(self.save_edit)

    def keyPressEvent(self, event):
        if not self.edit_mode and not self.play_label.isHidden():
            if event.key() == 16777220 or event.key == Qt.Key.Key_Enter :
                if (self.answer_label.isHidden()):
                    self.answer_label.show()
                else:
                    self.finish_play_field()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.center_overlay()

    def center_overlay(self): # Not very efficient, since most of this stuff is not visible half the time, but it works for now
        self.input_field.move(
            (self.width() - self.input_field.width()) // 2,
            (self.height() - self.input_field.height()) // 3
        )
        self.input_field_answer.move(
            (self.width() - self.input_field_answer.width()) // 2,
            (self.height() - self.input_field_answer.height()) // 2
        )
        self.file_drop.move(
            (self.width() - self.file_drop.width()) // 2,
            ((self.height() - self.file_drop.height()) * 2) // 3
        )
        self.remove_button.move(
            (self.width() - self.remove_button.width()) // 2,
            (self.height() + self.remove_button.height()) // 2
        )
        self.play_label.move(
            (self.width() - self.play_label.width()) // 2,
            (self.height() - self.play_label.height()) // 3
        )
        self.answer_label.move(
            (self.width() - self.answer_label.width()) // 2,
            self.play_label.y() + int(self.play_label.y() * 0.2)
        )
        if self.file_showcase is not None:
            if self.current_image is not None and isinstance(self.file_showcase, QLabel):
                    pixmap = self.current_image.scaledToHeight(self.height() // 3)
                    self.file_showcase.setPixmap(pixmap)
                    self.file_showcase.resize(pixmap.size())
            if isinstance(self.file_showcase, VideoPlayerButton):
                self.file_showcase.move(
                    (self.width() - self.file_showcase.width()) // 2,
                    (self.play_label.y() + int(self.file_showcase.height() * 3))
                )
            else:
                self.file_showcase.move(
                    (self.width() - self.file_showcase.width()) // 2,
                    ((self.height() - self.file_showcase.height()) * 2) // 3
                )

    def switch_autosave(self):
        self.auto_save = not self.auto_save

    def load_game(self, path, edit_mode):
        self.path = path
        self.edit_mode = edit_mode
        for widget in self.font_update:
            widget.setFont(QFont('Arial', Config.font_size + 2))
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
        autosave_checkmark.setText("♲\nautosave")
        autosave_checkmark.setFixedSize(40, 40)
        autosave_checkmark.setChecked(True)
        autosave_checkmark.clicked.connect(self.switch_autosave)
        self.grid.addWidget(autosave_checkmark, 1, 0)
        if not self.edit_mode:
            game_state_reset_button = QPushButton('Reset')
            game_state_reset_button.setFixedSize(60, 40)
            game_state_reset_button.clicked.connect(self.reset_game_state)
            self.grid.addWidget(game_state_reset_button, 2, 0)

        categories = self.current_data["categories"]
        i = 0
        for col, cat_id in enumerate(categories.keys(), start=1):
            cat_title = categories[cat_id][0]

            cat_button = QPushButton(cat_title)

            cat_button.setFont(QFont("Arial", Config.font_size))
            #cat_button.setFixedWidth(120)
            cat_button.setStyleSheet('text-align: center; white-space: normal;')
            if (self.edit_mode):
                cat_button.clicked.connect(lambda _, b=cat_button: self.edit_field(b))

            self.grid.addWidget(cat_button, 0, col)

            self.category_buttons[cat_button] = (cat_id, 0)

            questions = self.current_data["categories"][cat_id][1:]
            for row, question in enumerate(questions, start=1):
                q_button = QPushButton(str(question[0]))
                q_button.setFont(QFont("Arial", Config.font_size))
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
            self.populate_team_buttons()
            self.layout.addLayout(self.teams_layout)

    def populate_team_buttons(self):
        #self.team_edit_buttons = []
        for id, team in enumerate(self.current_data['saved_games']['save1']['teams'], start=0):
            team_layout = QVBoxLayout()
            team_addsub_layout = QHBoxLayout()

            team_button = QPushButton(team[0] + " \n " + str(team[1]))
            team_button.setFont(QFont('Arial', Config.font_size))
            team_button.clicked.connect(lambda _, index=id,button=team_button: self.edit_team(index, button))
            team_layout.addWidget(team_button)
            team_button_add = QPushButton('+')
            team_button_sub = QPushButton('-')
            team_button_add.setFont(QFont('Arial', Config.font_size))
            team_button_sub.setFont(QFont('Arial', Config.font_size))
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
        self.add_button = QPushButton('+')
        self.add_button.setFont(QFont('Arial', Config.font_size))
        self.add_button.clicked.connect(self.add_team)
        self.add_button.setFixedSize(40, 40)

        self.teams_layout.addWidget(self.add_button)

    def edit_team(self, id, button):
        if self.overlay.isHidden():
            self.input_field.returnPressed.disconnect()
            self.input_field.setText(self.current_data['saved_games']['save1']['teams'][id][0])
            self.input_field.show()
            self.overlay.show()
            self.input_field.setFocus()
            self.editing_button = button
            self.center_overlay()
            self.remove_button.show()
            self.remove_button.clicked.connect(lambda _, t_id=id: self.remove_team(t_id))
            self.input_field.returnPressed.connect(lambda *_, t_id=id, t_button=button: self.finish_edit_team(t_id, t_button))
    
    def remove_team(self, id):
        del self.current_data['saved_games']['save1']['teams'][id]
        if self.auto_save:
            self.save()
        self.remove_button.clicked.disconnect()
        self.remove_button.hide()
        self.input_field.returnPressed.disconnect()
        self.input_field.returnPressed.connect(self.save_edit)
        self.overlay.hide()
        self.input_field.setText('')
        self.input_field.hide()
        self.reload_teams()

    def finish_edit_team(self, id, button):
        button.setText(self.input_field.text() + '\n' + str(self.current_data['saved_games']['save1']['teams'][id][1]))
        self.current_data['saved_games']['save1']['teams'][id][0] = self.input_field.text()
        if (self.auto_save):
            self.save()
        self.remove_button.clicked.disconnect()
        self.remove_button.hide()
        self.input_field.returnPressed.disconnect()
        self.input_field.returnPressed.connect(self.save_edit)
        self.overlay.hide()
        self.input_field.setText('')
        self.input_field.hide()
    
    def add_team(self):
        if len(self.current_data['saved_games']['save1']['teams']) < 8:
            self.current_data['saved_games']['save1']['teams'].append(["Team " + str(len(self.current_data['saved_games']['save1']['teams']) + 1), 0])
            if (self.auto_save):
                self.save()
            self.reload_teams()

    def reload_teams(self):
        self.team_buttons = []
        delete_layout_recursive(self.teams_layout)
        self.populate_team_buttons()

    def reset_game_state(self):
        self.current_data['saved_games']['save1']['board_state'] = [
                [
                    False,
                    False,
                    False,
                    False,
                    False
                ],
                [
                    False,
                    False,
                    False,
                    False,
                    False
                ],
                [
                    False,
                    False,
                    False,
                    False,
                    False
                ],
                [
                    False,
                    False,
                    False,
                    False,
                    False
                ],
                [
                    False,
                    False,
                    False,
                    False,
                    False
                ]
            ]
        self.current_data['saved_games']['save1']['teams'] = [
                [
                    "Team 1",
                    0
                ]
            ]
        self.reload_teams()
        for button in self.category_buttons.keys():
            button.setStyleSheet("background-color: light gray")

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
        self.answer_label.setText(self.current_data['categories'][index[0]][index[1]][3])
        # if question has a file
        if len(self.current_question[2]) > 0:
            path = self.current_question[2]
            extension = path[-4:]
            # jpg or png image, the display it
            if extension in Config.file_extensions['image_file_extensions']:
                self.file_showcase = QLabel(self.overlay)
                self.current_image = QPixmap(path)
                pixmap = self.current_image.scaledToHeight(self.height() // 3)
                self.file_showcase.setPixmap(pixmap)
            elif extension in Config.file_extensions['sound_file_extensions']:
                self.file_showcase = PlayStopButton(path, player, parent=self.overlay)
            elif extension in Config.file_extensions['video_file_extensions']:
                self.file_showcase = VideoPlayerButton(path, self.overlay)
        self.add_button.hide()
        for team_button in self.team_buttons:
            team_button.show()
        self.overlay.show()
        self.play_label.show()
        self.center_overlay()
    
    def modify_points(self, team_id, button, multiplier=1):
        points = self.current_question[0]
        self.current_data['saved_games']['save1']['teams'][team_id][1] += points * multiplier
        team = self.current_data['saved_games']['save1']['teams'][team_id]
        button.setText(team[0] + " \n " + str(team[1]))
    
    def finish_play_field(self):
        self.play_label.setText('')

        if self.auto_save:
            self.save()
        self.current_image = None
        for team_button in self.team_buttons:
            team_button.hide()
        if self.file_showcase is not None:
            if isinstance(self.file_showcase, PlayStopButton):
                self.file_showcase.stop()
            elif isinstance(self.file_showcase, VideoPlayerButton):
                if self.file_showcase.video_player is not None:
                    self.file_showcase.video_player.close()
            self.file_showcase.hide()
            self.file_showcase.deleteLater()
            self.file_showcase = None
        self.add_button.show()
        self.current_image = None
        self.answer_label.hide()
        self.overlay.hide()
        self.play_label.hide()

    def edit_field(self, button):
        index = self.category_buttons[button]
        changeable = self.current_data['categories'][index[0]][index[1]]
        if isinstance(changeable, str): # Categories
            self.input_field.setText(changeable) 
        else: # Questions
            self.input_field.setText(changeable[1])
            self.file_drop.show()
            self.input_field_answer.show()
            if len(changeable[2]) > 0:
                self.file_drop.setText(changeable[2])
            else:
                self.file_drop.setText('Drop a file here:')
            if len(changeable[3]) > 0:
                self.input_field_answer.setText(changeable[3])
            else:
                self.input_field_answer.setText('Insert correct answer here')

        self.input_field.show()
        self.overlay.show()
        self.input_field.setFocus()
        self.editing_button = button
        self.center_overlay()

    def save_edit(self):
        new_text = self.input_field.text()
        button = self.editing_button
        index = self.category_buttons[button]

        self.input_field.hide()
        self.input_field_answer.hide()

        self.overlay.hide()
        if isinstance(self.current_data["categories"][index[0]][index[1]], str): # Categories
            button.setText(wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]] = new_text
        else: # Questions
            self.file_drop.hide()
            if len(self.file_drop.text()) > 0 and self.file_drop.text() != 'Drop a file here:':
                self.current_data["categories"][index[0]][index[1]][2] = self.file_drop.text()
            #self.file_drop.setText('')
            button.setText(str(self.current_data["categories"][index[0]][index[1]][0]) + '\n' + wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]][1] = new_text
            if len(self.input_field_answer.text()) > 0 and self.input_field_answer.text() != 'Insert correct answer here':
                self.current_data['categories'][index[0]][index[1]][3] = self.input_field_answer.text()

        if self.auto_save:
            self.save()