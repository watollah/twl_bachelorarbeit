import tkinter as tk
from tkinter import ttk
from typing import final, TypeVar
from twl_components import *

C = TypeVar('C', bound=Component)

class TwlTable(ttk.Treeview, TwlWidget):

    def __init__(self, master, component_list: ComponentList[C]):
        ttk.Treeview.__init__(self, master)
        self.component_list: ComponentList[C] = component_list

    def update(self) -> None:
        self.delete(*self.get_children())
        [self.insert("", tk.END, text=str(c.id), values=c.attribute_values) for c in self.component_list]