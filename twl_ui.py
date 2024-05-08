import tkinter as tk
import ttkbootstrap as ttk

from twl_components import *

class CremonaTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook, statical_system: StaticalSystem) -> None:
        ttk.Frame.__init__(self, notebook)
        self.statical_system = statical_system

        vertical_panes = ttk.PanedWindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)
        
        horizontal_panes = ttk.PanedWindow(vertical_panes, orient=tk.HORIZONTAL)
        self.create_statical_system_diagram(horizontal_panes)
        self.create_cremona_diagram(horizontal_panes)
        vertical_panes.add(horizontal_panes, weight=4)

        control_panel = ttk.Frame(vertical_panes)
        vertical_panes.add(control_panel, weight=1)

    def create_statical_system_diagram(self, master: tk.PanedWindow) -> ttk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
    
        title_label = ttk.Label(frame, text="Statical System", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        statical_system_diagram = ttk.Canvas(frame)
        statical_system_diagram.pack()
    
        return statical_system_diagram

    def create_cremona_diagram(self, master: tk.PanedWindow) -> ttk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
    
        title_label = ttk.Label(frame, text="Cremona Plan", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        cremona_diagram = ttk.Canvas(frame)
        cremona_diagram.pack()
    
        return cremona_diagram


        