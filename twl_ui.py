import tkinter as tk
from tkinter import ttk

from twl_components import *

class CremonaTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook, statical_system: StaticalSystem) -> None:
        ttk.Frame.__init__(self, notebook)
        self.statical_system = statical_system

        vertical_panes = ttk.Panedwindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)

        horizontal_panes = ttk.Panedwindow(vertical_panes, orient=tk.HORIZONTAL)
        self.create_statical_system_diagram(horizontal_panes)
        self.create_cremona_diagram(horizontal_panes)
        vertical_panes.add(horizontal_panes, weight=4)

        self.create_control_panel(vertical_panes)

        style = ttk.Style()
        style.configure("TPanedwindow", background="lightgrey")
        style.configure("Sash", sashthickness=5)

    def create_statical_system_diagram(self, master: tk.PanedWindow) -> tk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
            
        statical_system_diagram = tk.Canvas(frame)
        statical_system_diagram.configure(bg= "blue")
        statical_system_diagram.pack(fill=tk.BOTH, expand=True)
    
        title_label = ttk.Label(frame, text="Statical System", font=("Helvetica", 12))
        title_label.place(x=10, y=10)
    
        return statical_system_diagram

    def create_cremona_diagram(self, master: tk.PanedWindow) -> tk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
    
        cremona_diagram = tk.Canvas(frame)
        cremona_diagram.configure(bg= "red")
        cremona_diagram.pack(fill=tk.BOTH, expand=True)
    
        title_label = ttk.Label(frame, text="Cremona Plan", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return cremona_diagram
    
    def create_control_panel(self, master: tk.PanedWindow):
        frame = ttk.Frame(master)
        frame.pack_configure()
        master.add(frame, weight=1)

        inner_frame = ttk.Frame(frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = ttk.Frame(inner_frame)
        control_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            pane = ttk.Frame(control_panel, width=100, height=100, style=f"{i}.TFrame")
            ttk.Style().configure(f"{i}.TFrame", background=colors[i])
            pane.grid(row=0, column=i, padx=10, pady=10)
            control_panel.columnconfigure(i, weight=1)


        