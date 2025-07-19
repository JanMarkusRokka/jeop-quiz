from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class CustomTextEdit(QTextEdit):
    def __init__(self, func_callback, parent=None):
        super().__init__(parent)
        self.func_callback = func_callback

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key.Key_Enter or event.key() == 16777220) and not event.modifiers():
            self.func_callback()
        else:
            super().keyPressEvent(event)