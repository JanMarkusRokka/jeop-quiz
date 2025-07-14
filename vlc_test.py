import sys
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout

class VideoWindow(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.player = vlc.MediaPlayer(video_path)
        self.player.play()
        self.show()

    def closeEvent(self, event):
        self.player.stop()
        self.player.release()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        button = QPushButton("Play Video")
        button.clicked.connect(self.open_video)
        self.setCentralWidget(button)

    def open_video(self):
        self.video_window = VideoWindow(r"games\NewDocument\wing.mp4")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
