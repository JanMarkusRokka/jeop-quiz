from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal

class ClickableImage(QLabel):
    clicked = pyqtSignal()
    def __init__(self, original_image, parent=None):
        super().__init__(parent)
        self.original_image = original_image

    def fitImage(self):
        resized_image = self.original_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.setPixmap(resized_image)

    def mousePressEvent(self, event):
        self.clicked.emit()