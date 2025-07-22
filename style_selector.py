from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from config import Config
import json
import os

class StyleSelector(QWidget):
    def __init__(self, app, callback):
        super().__init__()
        self.boxlayout = QVBoxLayout(self)
        self.boxlayout.addStretch()
        self.boxlayout.setAlignment(Qt.AlignCenter)
        self.app = app
        self.callback = callback

        self.setLayout(self.boxlayout)

        label = QLabel('Select a style:')
        label.setFont(QFont('Arial', Config.font_size))
        label.setAlignment(Qt.AlignCenter)
        self.boxlayout.addWidget(label)

        blue_button = QPushButton('Blue')
        blue_button.setFont(QFont('Arial', Config.font_size))
        blue_button.clicked.connect(lambda _,style='blue': self.select_style(style))
        self.boxlayout.addWidget(blue_button)

        blue_button = QPushButton('Dark')
        blue_button.setFont(QFont('Arial', Config.font_size))
        blue_button.clicked.connect(lambda _,style='dark': self.select_style(style))
        self.boxlayout.addWidget(blue_button)

        blue_button = QPushButton('Light')
        blue_button.setFont(QFont('Arial', Config.font_size))
        blue_button.clicked.connect(lambda _,style='light': self.select_style(style))
        self.boxlayout.addWidget(blue_button)

        self.boxlayout.addStretch()
    
    def select_style(self, style, edit_settings_file=True):
        match style:
            case 'blue':
                self.app.setStyleSheet("""
                        QPushButton {
                            border : 5px solid;
                            border-color: #0D0B0F;
                            padding: 6px;
                        }
                        QPushButton:hover {
                            background-color: #030BA3;
                            border-radius: 12px;              
                        }
                                    
                        QPushButton:pressed {
                            background-color: #0602D6;
                            border-radius: 12px;              
                        }
                                    
                        QWidget {
                            background-color: #0609BD;
                            color: white;
                        }
                                    
                        QPushButton:checked {
                            background-color: #010D8C;
                            color: #0609BD;
                        }
                    """)
            case 'dark':
                self.app.setStyleSheet("""
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
                                
                        QWidget {
                            background-color: #302F32;
                            color: white;
                        }
                        QPushButton:checked {
                            background-color: #616161;
                            color: black;
                        }
                                    """)
            case 'light':
                self.app.setStyleSheet('')
        
        Config.style = style
        Config.save()
        self.callback()