from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class ImageDisplay(QLabel):
    def __init__(self, return_to_board_callback, parent=None):
        super().__init__(parent)
        self.return_to_board_callback = return_to_board_callback

    def show_image(self, pixmap):
        self.original_pixmap = pixmap
        self.update_pixmap()
        self.show()

    def keyPressEvent(self, event):
        if event.key() == 16777220 or event.key == Qt.Key.Key_Enter :
            self.return_to_board_callback()


    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

    def update_pixmap(self):
        scaled = self.original_pixmap.scaled(
            self.parent().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.resize(scaled.size())
        self.move(
            (self.parent().width() - self.width()) // 2,
            (self.parent().height() - self.height()) // 2
        )