import tkinter as tk
from tkinter import ttk
from typing import TypeVar, Generic

from c2d_components import Component, Attribute
from c2d_widgets import CustomEntry
from c2d_update import Observer


C = TypeVar('C', bound=Component)

class TwlTableEntryPopUp(CustomEntry):
    """Popup on top of a """

    def __init__(self, table, component: Component, attribute: Attribute, **kw):
        """Create an instance of TwlTableEntryPopup."""
        super().__init__(table, attribute.filter, **kw)
        self.component: Component = component
        self.attribute: Attribute = attribute

        current_value = attribute.get_value()
        self.insert(0, current_value)

        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<FocusOut>", lambda *ignore: self.destroy())

    def on_return(self, event):
        if self.attribute.filter(self.get())[0]:
            self.attribute.set_value(self.get())
            self.destroy()


class TwlTable(Observer, ttk.Treeview, Generic[C]):

    def __init__(self, master, component_list: list[C], component_type: type[C]):
        """Create an instance of TwlTable."""
        ttk.Treeview.__init__(self, master, show="headings")
        self.component_list: list[C] = component_list

        dummy = component_type.dummy()
        self.configure(columns=[attr.ID for attr in dummy.attributes])
        for attr in dummy.attributes: self.heading(attr.ID, text=attr.description)
        for attr in dummy.attributes: self.column(attr.ID, width=0, anchor=tk.CENTER)

        self.bind('<Double-1>', self.direct_edit_cell)

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        self.delete(*self.get_children())
        for c in self.component_list: self.insert("", tk.END, text=str(c.id), values=[attr.get_display_value() for attr in c.attributes])

    def direct_edit_cell(self, event):
        ''' Executed when a table entry is double-clicked. Opens popup on top of entry to enable editing its value.'''
        columnid = self.identify_column(event.x)
        rowid = self.identify_row(event.y)
        itemid = self.item(rowid, "text")

        if not itemid:
            return #return if the user double clicked on an empty cell

        component = next(component for component in self.component_list if component.id == itemid)
        attr_index = int(columnid[1:]) - 1 #remove the "#" from column id and convert to int
        attribute = component.attributes[attr_index]

        if not attribute.EDITABLE:
            return

        x, y, width, height = map(int, self.bbox(rowid, columnid))
        pady = height // 2

        self.entryPopup = TwlTableEntryPopUp(self, component, attribute)
        self.entryPopup.place( x=x, y=y+pady, anchor=tk.W, width=width)

    def hide_columns(self, *column_ids: str):
        columns = list(self["columns"])
        for column_id in column_ids:
            columns.remove(column_id)
        self["displaycolumns"] = columns