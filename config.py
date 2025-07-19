import os
from PyQt5.QtWidgets import QWidget

class Config:
    font_size = 14
    file_extensions = {
    'image_file_extensions': ['.jpg', '.png'],
    'sound_file_extensions': ['.mp3', '.wav'],
    'video_file_extensions': ['.mp4', '.webm', '.wmv', '.avi']
    }

def find_games():
    games = {}
    for file in os.listdir('./games/'):
        if file.endswith('.json'):
            games[file[:-5]] = os.path.join('./games/', file)
    return games

def is_int_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def wrap_text(text, max_line_length=15):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        if len(line + word) <= max_line_length:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    return "\n".join(lines)

def delete_layout_recursive(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().setParent(None)
                #child.widget().deleteLater()
            elif child.layout() is not None:
                delete_layout_recursive(child.layout())
        layout.setParent(None)

def clear_layout_recursive(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().setParent(None)
                #child.widget().deleteLater()
            elif child.layout() is not None:
                delete_layout_recursive(child.layout())
