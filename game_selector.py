import os
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from config import Config, find_games, clear_layout_recursive
import json

class GameSelector(QWidget):
    def __init__(self, load_game_callback, style_selector_callback):
        super().__init__()
        self.load_game_callback = load_game_callback
        self.style_selector_callback = style_selector_callback
        self.games_layout = QVBoxLayout()
        self.init_ui()
        # Overlay
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        self.overlay.hide()
        
        self.select_label = QLabel(self.overlay)
        self.select_label.setFont(QFont("Arial", Config.font_size))
        self.select_label.setStyleSheet("color: 'white'")
        self.select_label.setText("Select mode:")
        self.select_label.setAlignment(Qt.AlignCenter)
        self.select_label.hide()

        self.play_button = QPushButton(self.overlay)
        self.play_button.setFont(QFont("Arial", Config.font_size))
        self.play_button.setStyleSheet("color: 'white'")
        self.play_button.setText("Play")
        self.play_button.hide()

        self.edit_button = QPushButton(self.overlay)
        self.edit_button.setFont(QFont("Arial", Config.font_size))
        self.edit_button.setStyleSheet("color: 'white'")
        self.edit_button.setText("Edit")
        self.edit_button.hide()

        self.new_file_name_input = QLineEdit(self.overlay)
        self.new_file_name_input.setFont(QFont("Arial", Config.font_size))
        self.new_file_name_input.setStyleSheet("color: 'white'")
        self.new_file_name_input.setText("Game name")
        self.new_file_name_input.returnPressed.connect(self.new_game)
        self.new_file_name_input.hide()

    def init_ui(self):
        self.boxlayout = QVBoxLayout()
        label = QLabel("Select a game:")
        label.setFont(QFont("Arial", Config.font_size))
        self.boxlayout.addWidget(label)

        self.games_layout = QVBoxLayout()

        self.boxlayout.addLayout(self.games_layout)
        new_game_button = QPushButton('New game')
        new_game_button.setFont(QFont('Arial', Config.font_size))
        new_game_button.setStyleSheet('background-color: #575862; color: white')
        new_game_button.clicked.connect(self.openNewGameOverlay)
        self.boxlayout.addWidget(new_game_button)

        self.boxlayout.addStretch()
        self.setLayout(self.boxlayout)

        style_button = QPushButton('Set style')
        style_button.setFont(QFont('Arial', Config.font_size))
        style_button.clicked.connect(self.style_selector_callback)
        self.boxlayout.addWidget(style_button)

        layout_font_size = QHBoxLayout()
        font_size_add = QPushButton()
        font_size_add.setText('+ Font size')
        font_size_add.setFont(QFont('Arial', Config.font_size))
        font_size_add.clicked.connect(self.addFontSize)

        font_size_sub = QPushButton()
        font_size_sub.setText('- Font size')
        font_size_sub.setFont(QFont('Arial', Config.font_size))
        font_size_sub.clicked.connect(self.subFontSize)

        layout_font_size.addWidget(font_size_add)
        layout_font_size.addWidget(font_size_sub)
        self.font_size_example = QLabel('Font size example')
        self.font_size_example.setFont(QFont('Arial', Config.font_size))
        layout_font_size.addWidget(self.font_size_example)
        self.boxlayout.addLayout(layout_font_size)

    def update_games(self):
        clear_layout_recursive(self.games_layout)
        games = find_games()
        for name, path in games.items():
            button = QPushButton(name)
            button.setFont(QFont("Arial", Config.font_size))
            button.clicked.connect(lambda _, p=path: self.select_mode(p))
            self.games_layout.addWidget(button)
        self.overlay.raise_()

    def openNewGameOverlay(self):
        self.new_file_name_input.show()
        self.overlay.show()
    
    def new_game(self):
        if len(self.new_file_name_input.text()) > 0:
            template = open('game_template.json', 'r', encoding='utf-8')
            path = 'games/' + self.new_file_name_input.text() + '.json'
            self.new_file_name_input.setText("Game name")
            if (os.path.exists(os.path.abspath(path))):
                return

            new_game = open(path, 'w', encoding='utf-8')
            new_game.write(template.read())
            new_game.close()
            template.close()
            self.hide_overlay()
            self.load_game_callback(path, True)

    def addFontSize(self):
        self.modifyFontSize(2)
    
    def subFontSize(self):
        self.modifyFontSize(-2)

    def modifyFontSize(self, amount):
        if self.font_size_example is not None:
            Config.font_size = Config.font_size + amount
            self.font_size_example.setFont(QFont('Arial', Config.font_size))
            Config.save()

    def hide_overlay(self):
        self.select_label.hide()
        self.play_button.hide()
        self.edit_button.hide()
        self.new_file_name_input.hide()
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
        self.new_file_name_input.move(
            (self.width() - self.new_file_name_input.width()) // 2,
            (self.height() - self.new_file_name_input.height()) // 2
        )