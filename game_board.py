import json
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit,
    QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from drop_label import DropLabel
from play_stop_button import PlayStopButton
from config import Config, wrap_text, clear_layout_recursive
from video_player_button import VideoPlayerButton
from image_display import ImageDisplay
from clickable_label import ClickableImage

class GameBoard(QWidget):
    def __init__(self, return_to_menu_callback, show_image_callback, player):
        super().__init__()
        self.return_to_menu_callback = return_to_menu_callback
        self.show_image_callback = show_image_callback
        self.current_data = None
        self.player = player
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

        self.overlay_layout = QVBoxLayout(self.overlay)

        self.edit_mode = False

        self.teams_layout = None

        self.auto_save = True

        self.current_question = None

    def keyPressEvent(self, event):
        if event.key() == 16777220 or event.key() == Qt.Key.Key_Enter:
            if not self.overlay.isHidden() and not self.edit_mode:
                if (self.answer_label.isHidden()):
                    self.answer_label.show()
                else:
                    self.finish_play_field()
                    

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        if not self.edit_mode:
            if self.teams_layout is not None:
                self.overlay_layout.setContentsMargins(0, 0, 0, self.teams_layout.geometry().height())
            if not self.overlay.isHidden():
                self.resizeImages()

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
        clear_layout_recursive(self.teams_layout)
        clear_layout_recursive(self.overlay_layout)

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
        autosave_checkmark.setText("♲\nauto")
        autosave_checkmark.setFont(QFont('Arial', Config.font_size))
        autosave_checkmark.setFixedSize(40, 40)
        autosave_checkmark.setChecked(True)
        autosave_checkmark.clicked.connect(self.switch_autosave)
        self.grid.addWidget(autosave_checkmark, 1, 0)

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
                        q_button.setStyleSheet("background-color: grey; color: black")
                self.grid.addWidget(q_button, row, col)
                self.category_buttons[q_button] = (cat_id, row)
                i = row

        self.input_field = QTextEdit()
        self.input_field.setFont(QFont("Arial", Config.font_size))
        self.input_field.setStyleSheet("color: 'white'")
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.hide()

        self.save_button = QPushButton()
        self.save_button.setFont(QFont("Arial", Config.font_size))
        self.save_button.setText('Save')
        self.save_button.setProperty('class', 'overlayButton')
        self.save_button.hide()

        if self.edit_mode:
            inputs_layout = QHBoxLayout()
            self.overlay_layout.addLayout(inputs_layout)

            inputs_layout.addWidget(self.input_field)

            self.input_field_answer = QTextEdit()
            self.input_field_answer.setFont(QFont("Arial", Config.font_size))
            self.input_field_answer.setStyleSheet("color: 'white'")
            self.input_field_answer.setAlignment(Qt.AlignCenter)
            self.input_field_answer.hide()
            inputs_layout.addWidget(self.input_field_answer)

            self.file_drop = DropLabel(self.window(), self.overlay)
            self.file_drop.setFont(QFont("Arial", Config.font_size))
            self.file_drop.setText('Drop a file here:')
            self.file_drop.setStyleSheet("QLabel { color: white; background-color: black; border: 2px dashed gray; }")
            self.file_drop.setAlignment(Qt.AlignCenter)
            self.file_drop.hide()
            self.overlay_layout.addWidget(self.file_drop)
            self.overlay_layout.addWidget(self.save_button)
            self.save_button.clicked.connect(self.save_edit)
            self.overlay_layout.setContentsMargins(0, 0, 0, 0)
        else:
            game_state_reset_button = QPushButton('Reset')
            game_state_reset_button.setFixedSize(60, 40)
            game_state_reset_button.setFont(QFont('Arial', Config.font_size))
            game_state_reset_button.clicked.connect(self.reset_game_state)
            self.grid.addWidget(game_state_reset_button, 2, 0)

            self.resizable_images = []

            self.play_label = QLabel()
            self.play_label.setFont(QFont("Arial", Config.font_size))
            self.play_label.setStyleSheet("color: 'white'")
            self.play_label.setText("")
            self.play_label.setAlignment(Qt.AlignCenter)
            self.play_label.hide()
            self.overlay_layout.addWidget(self.play_label)

            self.answer_label = QLabel()
            self.answer_label.setFont(QFont("Arial", Config.font_size))
            self.answer_label.setStyleSheet("color: 'white'")
            self.answer_label.setText("")
            self.answer_label.setAlignment(Qt.AlignCenter)
            self.answer_label.hide()
            self.overlay_layout.addWidget(self.answer_label)

            self.file_showcase = QHBoxLayout()
            self.overlay_layout.addLayout(self.file_showcase)

            self.team_buttons = []
            self.teams_layout = QHBoxLayout()

            self.overlay_layout.addWidget(self.input_field)

            self.remove_button = QPushButton()
            self.remove_button.setFont(QFont("Arial", Config.font_size))
            self.remove_button.setText('Remove')
            self.remove_button.setProperty('class', 'overlayButton')
            self.remove_button.hide()
            self.overlay_layout.addWidget(self.remove_button)
            self.overlay_layout.addWidget(self.save_button)

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
            self.overlay.show()
            self.input_field.setText(self.current_data['saved_games']['save1']['teams'][id][0])
            self.input_field.show()
            self.input_field.setFocus()
            self.editing_button = button
            self.remove_button.show()
            self.save_button.show()
            self.remove_button.clicked.connect(lambda _, t_id=id: self.remove_team(t_id))
            self.save_button.clicked.connect(lambda *_, t_id=id, t_button=button: self.finish_edit_team(t_id, t_button))
    
    def remove_team(self, id):

        del self.current_data['saved_games']['save1']['teams'][id]
        if self.auto_save:
            self.save()
        self.remove_button.clicked.disconnect()
        self.remove_button.hide()
        self.save_button.clicked.disconnect()
        self.save_button.hide()
        self.overlay.hide()
        self.input_field.setText('')
        self.input_field.hide()
        self.reload_teams()

    def finish_edit_team(self, id, button):
        button.setText(self.input_field.toPlainText() + '\n' + str(self.current_data['saved_games']['save1']['teams'][id][1]))
        self.current_data['saved_games']['save1']['teams'][id][0] = self.input_field.toPlainText()
        if (self.auto_save):
            self.save()
        self.remove_button.clicked.disconnect()
        self.remove_button.hide()
        self.save_button.clicked.disconnect()
        self.save_button.hide()
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
        clear_layout_recursive(self.teams_layout)
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
            button.setStyleSheet("")

    def save(self):
        data = json.dumps(self.current_data, indent=4)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)


    def play_field(self, button):
        index = self.category_buttons[button]
        button.setStyleSheet("background-color: grey; color: black")
        self.current_data['saved_games']['save1']['board_state'][int(index[0]) - 1][index[1]-1] = True
        self.play_label.setText(wrap_text(self.current_data['categories'][index[0]][index[1]][1], 40))
        self.current_question = self.current_data['categories'][index[0]][index[1]]
        self.answer_label.setText(wrap_text(self.current_data['categories'][index[0]][index[1]][3], 40))
        # if question has files
        if len(self.current_question[2]) > 0:
            for file in self.current_question[2]:
                path = file
                extension = path[-4:]
                # jpg or png image, the display it
                if extension in Config.file_extensions['image_file_extensions']:
                    image = QPixmap(path)
                    clickable_img = ClickableImage(image, self.overlay)
                    clickable_img.clicked.connect(lambda *_, pm=image: self.show_image_callback(pm))
                    clickable_img.setAlignment(Qt.AlignCenter)
                    self.file_showcase.addWidget(clickable_img)
                    self.resizable_images.append(clickable_img)
                elif extension in Config.file_extensions['sound_file_extensions']:
                    self.file_showcase.addWidget(PlayStopButton(path, self.player, parent=self.overlay))
                elif extension in Config.file_extensions['video_file_extensions']:
                    self.file_showcase.addWidget(VideoPlayerButton(path, self.overlay))
        self.add_button.hide()
        for team_button in self.team_buttons:
            team_button.show()
        self.overlay.show()
        self.play_label.show()
        self.overlay_layout.setContentsMargins(0, 0, 0, self.teams_layout.geometry().height())
        self.resizeImages()

    
    def resizeImages(self):
        for image in self.resizable_images:
            image.fitImage()

    def modify_points(self, team_id, button, multiplier=1):
        points = self.current_question[0]
        self.current_data['saved_games']['save1']['teams'][team_id][1] += points * multiplier
        team = self.current_data['saved_games']['save1']['teams'][team_id]
        button.setText(team[0] + " \n " + str(team[1]))
    
    def finish_play_field(self):
        self.play_label.setText('')

        if self.auto_save:
            self.save()
        for team_button in self.team_buttons:
            team_button.hide()
        for i in range(self.file_showcase.count()):
            print(i)
            widget = self.file_showcase.itemAt(i)
            if isinstance(widget, PlayStopButton):
                widget.stop()
            elif isinstance(self.file_showcase, VideoPlayerButton):
                if widget.video_player is not None:
                    widget.video_player.close()

        self.add_button.show()
        clear_layout_recursive(self.file_showcase)
        self.resizable_images = []

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
            if len(changeable[3]) > 0:
                self.input_field_answer.setText(changeable[3])
            else:
                self.input_field_answer.setText('Insert correct answer here')

        self.input_field.show()
        self.save_button.show()
        self.overlay.show()
        self.input_field.setFocus()
        self.editing_button = button

    def save_edit(self):
        new_text = self.input_field.toPlainText()
        button = self.editing_button
        index = self.category_buttons[button]

        self.input_field.hide()
        self.input_field_answer.hide()
        self.save_button.hide()

        self.overlay.hide()
        if isinstance(self.current_data["categories"][index[0]][index[1]], str): # Categories
            button.setText(wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]] = new_text
        else: # Questions
            self.file_drop.hide()
            # add file paths saving here
            button.setText(str(self.current_data["categories"][index[0]][index[1]][0]) + '\n' + wrap_text(new_text))
            self.current_data['categories'][index[0]][index[1]][1] = new_text
            if len(self.input_field_answer.toPlainText()) > 0 and self.input_field_answer.toPlainText() != 'Insert correct answer here':
                self.current_data['categories'][index[0]][index[1]][3] = self.input_field_answer.toPlainText()

        if self.auto_save:
            self.save()