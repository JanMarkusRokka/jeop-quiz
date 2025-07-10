import tkinter as tk
from tkinter import ttk
#import sv_ttk
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
        self.settings = settings

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        frame = tk.Frame(root, bg='#1c1c1c')
        frame.grid()
        #self.frame.pack_propagate(False)
        label = ttk.Label(frame, padding=[0,10,0,10], text='Select a game:')
        label.pack(fill='both', expand=True)

        games = find_games()
        for game in games.keys():
            button = ttk.Button(frame, text=game, command=lambda g=game: self.load_game(games[g]))
            button.pack(fill='both', expand=True)

    def load_game(self, path):
        game_data_raw = open(path, 'r', encoding='utf-8')
        game_data = json.load(game_data_raw)

        self.clear_screen()

        frame = tk.Canvas(root, bg='#1c1c1c')
        frame.grid(row=0, column=0, sticky='nsew')

        for i in range(0, 5):
            frame.rowconfigure(i, weight=1)
            frame.columnconfigure(i, weight=1)

        i = 0
        for category in game_data['categories'].keys():
            print(category)
            button = ttk.Button(frame, text=category)
            button.configure(style='question.TButton')
            button.grid(column=i, row=0, sticky='n')
            j = 1
            for question in game_data['categories'][category]:
                button = ttk.Button(frame, text=question)
                button.grid(column=i, row = j, sticky='n')
                j+=1
            i+=1

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

def find_games():
    games = {}
    for file in os.listdir('./games/'):
        if file.endswith('.json'):
            games[file[:-5]] = './games/' + file
    return games

def setup_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.layout('question.TButton', style.layout('Accent.TButton'))
    style.configure('question.TButton', font=('Arial', 12), background="#595959", foreground="#fafafa", accent="#57c8ff")
    style.map('TButton',
              background=[
                  ('active', '#2f60d8'),
                  ('pressed', '#ffffff')
              ])
    style.configure('TButton', font=('Arial', 10), background="#595959", foreground="#fafafa", accent="#57c8ff",
                    relief='solid',
                    borderwidth=20,
                    bordercolor='#57c8ff'
                    )
    style.configure('TLabel', font=('Arial', 10), background="#595959", foreground="#fafafa", accent="#57c8ff")

if __name__ == '__main__':
    # Ignore first arg, since that is the name of the program
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    root = tk.Tk()
    root.iconbitmap('hakillak.ico')
    root.title('Hakillak')
    setup_styles()

    settings = {'dimensions': [1000, 500]}

    #sv_ttk.set_theme('dark')
    app = App(root, settings)
    root.mainloop()