import logging
import sys
import os
import json
import traceback

from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QtMsgType, qInstallMessageHandler
from PyQt5.QtMultimedia import QMediaPlayer

from game_board import GameBoard
from game_selector import GameSelector
from image_display import ImageDisplay
from style_selector import StyleSelector
from config import Config


# --------------------------------------------------------------------------
# Debug mode
# --------------------------------------------------------------------------

DEBUG = "--debug" in sys.argv or os.environ.get("HAKILLAK_DEBUG") == "1"

log = logging.getLogger("hakillak")


def app_dir():
    """Directory of the script, or of the .exe when frozen."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def attach_console():
    """Give a windowed Windows build a console to print to.

    Reuses the parent console if launched from a terminal, otherwise
    allocates a fresh one. No-op on other platforms.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        if not kernel32.AttachConsole(-1):   # -1 = ATTACH_PARENT_PROCESS
            kernel32.AllocConsole()
        sys.stdout = open("CONOUT$", "w", buffering=1, encoding="utf-8")
        sys.stderr = open("CONOUT$", "w", buffering=1, encoding="utf-8")
        sys.stdin = open("CONIN$", "r", encoding="utf-8")
    except Exception:
        pass  # never let console setup kill the app


def setup_logging(debug):
    handlers = []

    if sys.stderr is not None:
        handlers.append(logging.StreamHandler(sys.stderr))

    try:
        handlers.append(logging.FileHandler(
            os.path.join(app_dir(), "hakillak.log"), encoding="utf-8"
        ))
    except OSError:
        pass  # read-only install dir, etc.

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    # Route Qt's own warnings (layout complaints, missing plugins,
    # media backend errors) into the same log.
    qt_levels = {
        QtMsgType.QtDebugMsg:    logging.DEBUG,
        QtMsgType.QtInfoMsg:     logging.INFO,
        QtMsgType.QtWarningMsg:  logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg:    logging.CRITICAL,
    }

    def qt_message_handler(mode, context, message):
        logging.getLogger("qt").log(qt_levels.get(mode, logging.INFO), message)

    qInstallMessageHandler(qt_message_handler)

    # Unhandled exceptions: log them, and in debug mode also show them.
    def excepthook(exc_type, exc_value, exc_tb):
        logging.getLogger("hakillak").critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_tb)
        )
        if debug and QApplication.instance() is not None:
            text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            QMessageBox.critical(None, "Unhandled exception", text)

    sys.excepthook = excepthook

    log.debug("Debug mode on (python %s, cwd %s)", sys.version.split()[0], os.getcwd())


# --------------------------------------------------------------------------


class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("Hakillak")
        self.setMinimumSize(720, 480)
        self.setWindowIcon(QIcon("hakillak.ico"))
        self.player = QMediaPlayer()

        self.stack = QStackedWidget()

        try:
            Config.read('settings.json')
        except (OSError, json.JSONDecodeError):
            log.warning("Could not read settings.json, using defaults", exc_info=True)

        self.style_selector = StyleSelector(app, self.show_menu)
        self.selector = GameSelector(self.load_game, self.select_style)
        self.board = GameBoard(self.show_menu, self.show_image, self.player)
        self.image_display = ImageDisplay(self.go_to_game)

        self.stack.addWidget(self.selector)
        self.stack.addWidget(self.board)
        self.stack.addWidget(self.image_display)
        self.stack.addWidget(self.style_selector)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        log.debug("Applying style %r", Config.style)
        self.style_selector.select_style(Config.style)
        self.show_menu()

    def load_game(self, path, edit_mode):
        log.debug("Loading game %r (edit_mode=%s)", path, edit_mode)
        self.board.load_game(path, edit_mode)
        self.stack.setCurrentWidget(self.board)

    def go_to_game(self):
        self.stack.setCurrentWidget(self.board)
        self.board.resize_images()

    def show_menu(self):
        self.selector.update_games()
        self.stack.setCurrentWidget(self.selector)

    def show_image(self, pixmap):
        self.image_display.show_image(pixmap)
        self.stack.setCurrentWidget(self.image_display)

    def select_style(self):
        self.stack.setCurrentWidget(self.style_selector)


if __name__ == "__main__":
    if DEBUG:
        attach_console()
    setup_logging(DEBUG)

    # Don't pass our own flag on to Qt.
    app = QApplication([a for a in sys.argv if a != "--debug"])

    window = MainWindow(app)
    window.show()
    code = app.exec()

    log.debug("Exiting with code %s", code)
    if DEBUG and sys.stdin is not None:
        try:
            input("Press Enter to close the console...")
        except (EOFError, KeyboardInterrupt):
            pass

    sys.exit(code)