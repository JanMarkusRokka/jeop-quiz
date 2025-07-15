from PyQt5.QtWidgets import (
    QPushButton,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from config import Config
from video_player import VideoPlayer

class VideoPlayerButton(QPushButton):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_player = None
        self.setText('Open video')
        self.setFont(QFont('Arial', Config.font_size + 4))
        self.setStyleSheet('color: white')
        self.clicked.connect(lambda _, p=video_path: self.OpenPlayer(p))
    
    def OpenPlayer(self, path):
        if self.video_player is not None:
            self.video_player.close()
            self.video_player = None
        self.video_player = VideoPlayer(path, self)
        self.video_player.show()