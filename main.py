import tkinter as tk
from tkinter import ttk
import pywinstyles
#import sv_ttk
import json
import sys
#from PIL import Image, ImageTk
import os

image = None

def stop_app(rect, dirs):
    # Close tkinter winder
    root.destroy()

class App:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.selection_menu()

    def selection_menu(self):
        self.clear_screen()
        #frame = tk.Frame(root)
        #frame.grid()
        #self.frame.pack_propagate(False)
        label = ttk.Label(self.root, padding=[0,10,0,10], text='Select a game:')
        label.pack(expand=True)#fill='both', expand=True)

        games = find_games()
        for game in games.keys():
            button = ttk.Button(self.root, text=game, command=lambda g=game: self.load_game(games[g]))
            button.pack(fill='both', expand=True)

    def load_game(self, path):
        game_data_raw = open(path, 'r', encoding='utf-8')
        game_data = json.load(game_data_raw)

        self.clear_screen()

        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, sticky='nsew')

        for i in range(0, 6):
            frame.rowconfigure(i, weight=2)
            frame.columnconfigure(i, weight=2)

        frame.columnconfigure(0, weight=1)
        
        back_button = ttk.Button(frame, text='✖', width=2, command=lambda: self.selection_menu())
        back_button.grid(column=0, row=0, sticky='nw')

        i = 1
        for category in game_data['categories'].keys():
            print(category)
            button = ttk.Button(frame, text=category)
            button.configure(command=lambda b=button: self.edit_field(b, game_data, frame))
            button.configure(style='question.TButton')
            
            button.grid(column=i, row=0, sticky='n')
            j = 1
            for question in game_data['categories'][category]:
                button = ttk.Button(frame, text=question)
                button.grid(column=i, row = j, sticky='n')
                j+=1
            i+=1

    def edit_field(self, button, game_data, frame):
        overlay = ttk.Frame(frame, style='overlay.TFrame')
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        pywinstyles.set_opacity(overlay, 0.5)

        overlay.lift()

        entry = ttk.Entry(frame)
        entry.insert(0, button.cget('text'))
        entry.place(relx=0.5, rely=0.5, anchor='center')
        entry.lift()
        entry.focus_set()

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
    style.configure('question.TButton', font=('Arial', 12), background="#1c1c1c", foreground="#fafafa", accent="#57c8ff")
    style.map('TButton',
              background=[
                  ('active', '#595959'),
                  ('pressed', '#ffffff')
              ])
    style.configure('TButton', font=('Arial', 10), background="#1c1c1c", foreground="#fafafa", accent="#57c8ff",
                    relief='groove',
                    borderwidth=2,
                    bordercolor='#57c8ff'
                    )
    style.configure('TLabel', font=('Arial', 10), background="#1c1c1c", foreground="#fafafa", accent="#57c8ff")
    style.layout('overlay.TFrame', style.layout('TFrame'))
    style.configure('overlay.TFrame', background='black', foreground='black')
    style.configure('TFrame', background='#1c1c1c', foreground='#1c1c1c')


if __name__ == '__main__':
    # Ignore first arg, since that is the name of the program
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    # Igale kuldvillakule eri nimi
    root = tk.Tk()
    root.iconbitmap('hakillak.ico')
    root.title('Hakillak')
    root.minsize(720, 480)
    pywinstyles.apply_style(root, 'mica')
    setup_styles()

    settings = {'dimensions': [1000, 500]}

    #sv_ttk.set_theme('dark')
    app = App(root, settings)
    root.mainloop()