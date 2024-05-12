import tkinter as tk
from tkinter import ttk
from typing import final, TypeVar

from twl_components import *

C = TypeVar('C', bound=Component)


class TwlTableEntryPopUp(tk.Entry):

    def __init__(self, table, component: Component, attribute: str, **kw):
        super().__init__(table, **kw)
        self.table = table
        self.component: Component = component
        self.attribute: str = attribute

        attribute_index = -1 if attribute == "id" else self.component.attribute_names.index(attribute.lower())
        current_value = str(component.id) if attribute == "id" else self.component.attribute_values[attribute_index]

        self.insert(0, current_value)
        self['exportselection'] = False #stop selected text from being copied to clipboard

        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<FocusOut>", lambda *ignore: self.destroy())

    def on_return(self, event):
        attribute_type = type(getattr(self.component, self.attribute.lower()))
        self.component.__setattr__(self.attribute.lower(), attribute_type(self.get()))
        self.destroy()


class TwlTable(ttk.Treeview, TwlWidget):

    def __init__(self, master, component_list: ComponentList[C]):
        ttk.Treeview.__init__(self, master)

        self.component_list: ComponentList[C] = component_list
        component_list.statical_system.widgets.append(self)

        columns: tuple = component_list.component_class.attribute_names
        self.configure(columns=columns)
        self.heading("#0", text="Id")
        for i in range(0, len(columns)): self.heading(columns[i], text=columns[i].capitalize())

        self.bind('<Double-1>', self.direct_edit_cell)

    def update(self) -> None:
        self.delete(*self.get_children())
        [self.insert("", tk.END, text=str(c.id), values=c.attribute_values) for c in self.component_list]

    def direct_edit_cell(self, event):
        ''' Executed when a table entry is double-clicked. Opens popup on top of entry to enable editing its value.'''
        rowid = self.identify_row(event.y)
        column = self.identify_column(event.x)
        itemid = self.item(rowid, "text")

        if not itemid:
            return #return if the user double clicked on an empty cell

        component = self.component_list.get_component(int(itemid))
        assert(component)
        attribute = self.heading(column, "text").lower()

        x, y, width, height = map(int, self.bbox(rowid, column))
        pady = height // 2

        text = self.item(rowid, 'text')
        self.entryPopup = TwlTableEntryPopUp(self, component, attribute)
        self.entryPopup.place( x=x, y=y+pady, anchor=tk.W, width=width)
    