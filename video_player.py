from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
import vlc

class VideoPlayer(QWidget):
    def __init__(self, video_path, open_button):
        super().__init__()
        self.setWindowTitle("Video player")
        self.setMinimumSize(800, 600)

        self.player = vlc.MediaPlayer(video_path)
        self.hide()
        self.player.play()
        self.open_button = open_button
    
    def closeEvent(self, event):
        self.player.stop()
        self.player.release()
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