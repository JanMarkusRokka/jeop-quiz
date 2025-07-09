import tkinter as tk
from tkinter import ttk
import sv_ttk
import json
import sys
#from PIL import Image, ImageTk
import os

image = None

def stop_app(rect, dirs):
    # Close tkinter winder
    root.destroy()

    input('Press enter to close')

class App:
    def __init__(self, root, settings):
        self.root = root
        self.frame = tk.Canvas(root, width=settings.get('dimensions')[0], height=settings.get('dimensions')[1], bg='#1c1c1c')
        self.frame.pack()
        self.frame.pack_propagate(False)

        label = ttk.Label(self.frame, padding=[0,10,0,10], text='Select a game:')
        label.pack()

        games = find_games()
        for game in games.keys():
            button = ttk.Button(self.frame, padding=[0,5,0,5], text=game, command=lambda g=game: load_game(games[g]))
            button.pack()

def find_games():
    games = {}
    for file in os.listdir('./games/'):
        if file.endswith('.json'):
            games[file[:-5]] = './games/' + file
    return games

def load_game(path):
    game_data_raw = open(path, 'r', encoding='utf-8')
    game_data = json.load(game_data_raw)
    print(path)
    print(game_data['categories'])

if __name__ == '__main__':
    # Ignore first arg, since that is the name of the program
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    root = tk.Tk()
    root.iconbitmap('hakillak.ico')
    root.title('Hakillak')

    settings = {'dimensions': [1000, 500]}

    sv_ttk.set_theme('dark')
    app = App(root, settings)
    root.mainloop()