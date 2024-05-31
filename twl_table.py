import tkinter as tk
from tkinter import ttk
from typing import final, TypeVar

from twl_components import *

C = TypeVar('C', bound=Component)


class TwlTableEntryPopUp(tk.Entry):

    def __init__(self, table, component: Component, attr_index: int, **kw):
        super().__init__(table, **kw)
        self.table = table
        self.component: Component = component
        self.attribute: str = ""

        current_value = self.component.attribute_values[attr_index]

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
        ttk.Treeview.__init__(self, master, show="headings")
        self.component_list: ComponentList[C] = component_list
        component_list.update_manager.widgets.append(self)

        dummy = component_list.component_class.dummy()
        self.configure(columns=[attr.ID for attr in dummy.attributes])
        for attr in dummy.attributes: self.heading(attr.ID, text=attr.description)
        for attr in dummy.attributes: self.column(attr.ID, width=0, anchor=tk.CENTER)

        self.bind('<Double-1>', self.direct_edit_cell)

    def update(self) -> None:
        self.delete(*self.get_children())
        for c in self.component_list: self.insert("", tk.END, text=str(c.id), values=[attr.get_value() for attr in c.attributes])

    def direct_edit_cell(self, event):
        ''' Executed when a table entry is double-clicked. Opens popup on top of entry to enable editing its value.'''
        columnid = self.identify_column(event.x)
        rowid = self.identify_row(event.y)
        itemid = self.item(rowid, "text")

        if not itemid:
            return #return if the user double clicked on an empty cell

        component = self.component_list.get_component(int(itemid))
        assert(component)

        attr_index = int(columnid[1:]) #remove the "#" from column id and convert to int

        x, y, width, height = map(int, self.bbox(rowid, columnid))
        pady = height // 2

        text = self.item(rowid, 'text')
        self.entryPopup = TwlTableEntryPopUp(self, component, attr_index)
        self.entryPopup.place( x=x, y=y+pady, anchor=tk.W, width=width)
    