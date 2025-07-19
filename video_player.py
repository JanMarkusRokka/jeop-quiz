from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import vlc
from config import Config

class VideoPlayer(QWidget):
    def __init__(self, video_path, open_button):
        super().__init__()
        self.setWindowTitle("Video player")
        self.player = vlc.MediaPlayer(video_path)
        self.player.set_fullscreen(True)
        self.player.play()
        self.open_button = open_button
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.7)
        self.setFixedSize(200, 80)
        self.move(10, 10)
        button = QPushButton(self)
        button.setFont(QFont('Arial', Config.font_size))
        button.setText('Stop')
        button.clicked.connect(self.close)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.adjustSize()
        self.show()
        self.activateWindow()
        self.setFocus()
        self.raise_()
    
    def closeEvent(self, event):
        if self.player:
            self.player.stop()
            QTimer.singleShot(300, self.player.release)
        self.open_button.video_player = None
        event.accept()

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()
    
    def keyPressEvent(self, event):
        print(event.key())
        if event.key() == Qt.Key.Key_Space :
            self.toggle_play()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()