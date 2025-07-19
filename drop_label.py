from PyQt5.QtWidgets import QLabel

class DropLabel(QLabel):
    def __init__(self, window, func_callback, files_layout, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.func_callback = func_callback
        self.files_layout = files_layout
        self.parent_window = window

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:  # Ensure it's a local file
                    self.func_callback(file_path, self.files_layout)
                    self.parent_window.activateWindow()
                    self.parent_window.raise_()
            event.acceptProposedAction()