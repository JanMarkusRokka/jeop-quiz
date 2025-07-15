from PyQt5.QtWidgets import QPushButton

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtMultimedia import QMediaContent
from config import Config

class PlayStopButton(QPushButton):
    def __init__(self, path, player, parent=None):
        super().__init__(parent)
        self.setText('►')
        self.setStyleSheet('color: white')
        self.setFont(QFont('Arial', Config.font_size + 4))
        self.path = path
        self.player = player
        self.clicked.connect(self.playStop)

    def playStop(self):
        if self.text() == '►':
            self.play()
        elif self.text() == '■':
            self.stop()
    
    def play(self):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(QFileInfo(self.path).absoluteFilePath())))
        self.player.play()
        self.setText('■')
    
    def stop(self):
        self.player.stop()
        self.setText('►')