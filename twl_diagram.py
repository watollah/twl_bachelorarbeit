import tkinter as tk
from tkinter import ttk
from typing import TypeVar, Generic, Type
from abc import abstractmethod

from twl_update import TwlWidget
from twl_widgets import CustomRadioButton
from twl_style import Colors
from twl_images import add_image_from_path
from twl_components import Component
from twl_math import Point, Polygon


class Shape():
    """Represents a generic Shape in the diagram."""

    TAGS: list[str] = []
    TAG = "shape"

    COLOR = "black"
    BG_COLOR = "white"

    def __init__(self, diagram: 'TwlDiagram') -> None: #todo: always draw labels here, configure visibility in update
        self.diagram: 'TwlDiagram' = diagram
        self.tk_shapes: dict[int, Polygon] = {} #all tk_ids related to this shape with their position in the diagram

    def scale(self, factor: float):
        for tk_id, polygon in self.tk_shapes.items():
            coords = [coord * factor for point in polygon.points for coord in (point.x, point.y)]
            self.diagram.coords(tk_id, coords)

    @abstractmethod
    def is_at(self, x: int, y: int) -> bool:
        return False


C = TypeVar('C', bound=Component)

class ComponentShape(Generic[C], Shape):
    """Represents the shape of a component in the diagram."""

    TEMP = "temp"
    TEMP_COLOR = "lightgrey"

    SELECTED_COLOR = Colors.DARK_SELECTED
    SELECTED_BG_COLOR = Colors.LIGHT_SELECTED

    LABEL_TAG = "label"
    LABEL_BG_TAG = "label_background"
    LABEL_PREFIX = ""
    LABEL_SIZE = 12

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.TAGS = cls.TAGS.copy()
        cls.TAGS.append(cls.TAG)

    def __init__(self, component: C, diagram: 'TwlDiagram') -> None: #todo: always draw labels here, configure visibility in update
        super().__init__(diagram)
        self.component: C = component

        if (not self.TAG == ComponentShape.TEMP) and self.label_visible(): 
            self.label_tk_id, self.label_bg_tk_id = self.draw_label()
            self.tk_shapes[self.label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
            x1, x2, y1, y2 = self.diagram.bbox(self.label_tk_id)
            self.tk_shapes[self.label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

    def select(self):
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=self.SELECTED_COLOR)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, self.selected_style(*tags))
        self.diagram.selection.append(self)
        print(f"selected: {self.component.id}")

    def deselect(self):
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=Colors.BLACK)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, self.default_style(*tags))
        self.diagram.selection.remove(self)
        print(f"deselected: {self.component.id}")

    @abstractmethod
    def default_style(self, *tags: str) -> dict[str, str]:
        """Style attributes when the shape is not selected."""
        pass

    @abstractmethod
    def selected_style(self, *tags: str) -> dict[str, str]:
        """Style attributes when the shape is selected."""
        pass

    def scale(self, factor: float):
        """Scale the label."""
        super().scale(factor)
        if (not self.TAG == ComponentShape.TEMP) and self.label_visible(): 
            self.diagram.itemconfig(self.label_tk_id, font=('Helvetica', int(self.LABEL_SIZE * factor)))

    @property
    @abstractmethod
    def label_position(self) -> Point:
        pass

    @abstractmethod
    def label_visible(self) -> bool:
        return False

    def draw_label(self) -> tuple[int, int]:
        return self.diagram.create_text_with_bg(self.label_position.x, 
                                 self.label_position.y, 
                                 text=self.component.id, 
                                 tags=self.LABEL_TAG,
                                 bg_tag=self.LABEL_BG_TAG,
                                 font=('Helvetica', self.LABEL_SIZE))


class Tool:

    ID: int = -1
    NAME: str = "X"
    DESCR: str = "X"
    ICON: str = "X"

    def __init__(self, diagram: 'TwlDiagram'):
        self.diagram: 'TwlDiagram' = diagram

    def activate(self):
        self.diagram.bind("<Button-1>", self._action)
        self.diagram.bind("<Motion>", self._preview)
        self.diagram.bind("<Escape>", lambda *ignore: self.reset())
        self.diagram.bind("<Leave>", lambda *ignore: self.diagram.delete_with_tag(ComponentShape.TEMP))

    def deactivate(self):
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<Motion>")
        self.diagram.unbind("<Escape>")
        self.diagram.unbind("<Leave>")
        self.reset()

    def reset(self):
        self.diagram.delete_with_tag(ComponentShape.TEMP)

    def correct_event_pos(self, event):
        """Correct the coordinates of the mouse pointer to account for scrolling and scaling of the diagram."""
        self.correct_scrolling(event)
        self.correct_scaling(event)

    def correct_scrolling(self, event):
        x_min, y_min, x_max, y_max = self.diagram.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        event.x = event.x + self.diagram.xview()[0] * sr_width - abs(x_min)
        event.y = event.y + self.diagram.yview()[0] * sr_height - abs(y_min)

    def correct_scaling(self, event):
        event.x = event.x * (1 / (self.diagram.current_zoom.get() / 100))
        event.y = event.y * (1 / (self.diagram.current_zoom.get() / 100))

    def _action(self, event):
        self.correct_event_pos(event)
        self.action(event)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

    def _preview(self, event):
        self.correct_event_pos(event)
        self.preview(event)

    def preview(self, event):
        """Preview of the action when the user moves the mouse on the canvas while the tool is active"""
        pass

    def holding_shift_key(self, event) -> bool:
        return event.state & 0x1 #bitwise ANDing the event.state with the ShiftMask flag


class TwlDiagram(tk.Canvas, TwlWidget):

    ZOOM_STEP: float = 5
    MIN_ZOOM: float = 10
    MAX_ZOOM: float = 300

    SCROLL_EXTEND: int = 100
    SCROLL_STEP: int = 1

    UI_PADDING: int = 10

    TEXT_TAG = "text"
    TEXT_BG_TAG = "text_bg"
    TEXT_SIZE = 10

    SHOW_TOOLBAR: bool = False
    TOOL_BUTTON_SIZE: int = 50

    NO_UPDATE_TAGS = []

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)
        self.grid(column=0, row=0, sticky=tk.NSEW)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.shapes: list[Shape] = []
        self.selection: list[ComponentShape] = []

        self.current_zoom = tk.DoubleVar(value=100.0)
        self.current_zoom.trace_add("write", lambda *ignore: self.refresh())

        self.pan_start_pos = Point(0, 0)
        self.pan_xview_start = 0
        self.pan_yview_start = 0

        self.create_scrollbars(master)

        self.tools: list[Tool]
        self._selected_tool_id: tk.IntVar = tk.IntVar(value=0)
        self.selected_tool: Tool

        #bottom elements
        self.bottom_bar = self.create_bottom_bar()
        self.bottom_bar.place(x=self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SW)

        self.bind("<Configure>", self.refresh)
        self.bind("<Control-MouseWheel>", self.zoom)
        self.bind("<Shift-MouseWheel>", lambda event: self.scroll(tk.HORIZONTAL, "scroll", self.SCROLL_STEP if event.delta < 0 else -self.SCROLL_STEP))
        self.bind("<MouseWheel>", lambda event: self.scroll(tk.VERTICAL, "scroll", self.SCROLL_STEP if event.delta < 0 else -self.SCROLL_STEP))
        self.bind("<Button-2>", self.start_pan)
        self.bind("<B2-Motion>", self.pan)  
        self.bind("<ButtonRelease-2>", self.end_pan)  

        self.update_scrollregion()

    def refresh(self, event=None):
        self.update_scrollregion()
        self.bottom_bar.place(x=self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SW)

        for shape in self.shapes:
            shape.scale(self.current_zoom.get() / 100)

    def update(self) -> None:
        """Redraws the diagram completely from the model."""
        pass

    def clear(self):
        """Removes all shapes from the diagram."""
        for shape in self.find_all():
            tags = set(self.gettags(shape))
            if not tags.intersection(self.NO_UPDATE_TAGS):
                self.delete(shape)
        self.shapes.clear()

    def create_bottom_bar(self) -> tk.Frame:
        bottom_bar = tk.Frame(self, background=Colors.WHITE)
        zoom_label = ttk.Label(bottom_bar, text=f"Zoom ")
        zoom_label.pack(side=tk.LEFT, padx=(0, 0))
        zoom_entry = ttk.Entry(bottom_bar, width=5, justify=tk.RIGHT)
        zoom_entry.bind("<Return>", lambda *ignore: self.process_entry(zoom_entry, self.MIN_ZOOM, self.MAX_ZOOM, self.current_zoom))
        zoom_entry.bind("<FocusOut>", lambda *ignore: self.set_entry_text(zoom_entry, self.current_zoom.get()))
        self.current_zoom.trace_add("write", lambda *ignore: self.set_entry_text(zoom_entry, self.current_zoom.get()))
        self.set_entry_text(zoom_entry, self.current_zoom.get())
        zoom_entry.pack(side=tk.LEFT, padx=(0, 0))
        percent_label = ttk.Label(bottom_bar, text="%")
        percent_label.pack(side=tk.LEFT, padx=(0, self.UI_PADDING))
        return bottom_bar

    def create_scrollbars(self, master):
        v_scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=lambda scrolltype, amount: self.scroll(tk.VERTICAL, scrolltype, amount))
        v_scrollbar.grid(column=1, row=0, sticky=tk.NS)

        h_scrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=lambda scrolltype, amount: self.scroll(tk.HORIZONTAL, scrolltype, amount))
        h_scrollbar.grid(column=0, row=1, sticky=tk.EW)

        corner = tk.Frame(master, background=Colors.LIGHT_GRAY)
        corner.grid(column=1, row=1, sticky=tk.NSEW)

        self.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

    def scroll(self, orientation: str, scroll_type: str, amount):
        if orientation == tk.HORIZONTAL:
            if scroll_type == tk.MOVETO:
                self.xview_moveto(amount)
            elif scroll_type == tk.SCROLL:
                self.xview_scroll(amount, tk.UNITS)
        elif orientation == tk.VERTICAL:
            if scroll_type == tk.MOVETO:
                self.yview_moveto(amount)
            elif scroll_type == tk.SCROLL:
                self.yview_scroll(amount, tk.UNITS)
        self.refresh()

    def update_scrollregion(self):
        shapes = [tk_id for shape in self.shapes for tk_id in shape.tk_shapes.keys()]
        if shapes:
            bbox = self.bbox(*shapes)
            self.configure(scrollregion=(min(0, bbox[0] - self.SCROLL_EXTEND), 
                                     min(0, bbox[1] - self.SCROLL_EXTEND), 
                                     max(self.winfo_width(), bbox[2] + self.SCROLL_EXTEND), 
                                     max(self.winfo_height(), bbox[3] + self.SCROLL_EXTEND)))
        else:
            self.configure(scrollregion=(0, 0, self.winfo_width(), self.winfo_height()))

    def get_scrollregion(self) -> tuple[int, int, int, int]:
        sr_str = self.cget("scrollregion") or "0 0 0 0"
        sr_int = tuple([int(num) for num in sr_str.split()])
        assert len(sr_int) == 4
        return sr_int

    def zoom(self, event): #todo: scroll to previous position in diagram
        if event.delta < 0:
            self.current_zoom.set(max(self.MIN_ZOOM, self.current_zoom.get() - self.ZOOM_STEP))
        else:
            self.current_zoom.set(min(self.MAX_ZOOM, self.current_zoom.get() + self.ZOOM_STEP))
        self.refresh()

    def start_pan(self, event):
        self.pan_start_pos = Point(event.x, event.y)
        self.pan_xview_start = self.xview()[0]
        self.pan_yview_start = self.yview()[0]
        self.config(cursor="fleur")

    def pan(self, event):
        delta_x = event.x - self.pan_start_pos.x
        delta_y = event.y - self.pan_start_pos.y
        x_min, y_min, x_max, y_max = self.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        frac_x = delta_x / sr_width
        frac_y = delta_y / sr_height
        self.xview_moveto(self.pan_xview_start - frac_x)
        self.yview_moveto(self.pan_yview_start - frac_y)
        self.refresh()

    def end_pan(self, event):
        self.config(cursor="arrow")

    def add_button(self, tool: Tool, toolbar: ttk.Frame):
        image = add_image_from_path(tool.ICON, self.TOOL_BUTTON_SIZE, self.TOOL_BUTTON_SIZE)
        button = CustomRadioButton(toolbar, image=image, variable=self._selected_tool_id, value=tool.ID, command=self.handle_tool_change, outlinewidth=1)
        button.pack()

    def select_tool(self, tool_id: int):
        self._selected_tool_id.set(tool_id)
        self.handle_tool_change()

    def handle_tool_change(self):
        """Perform tool change."""
        self.selected_tool.deactivate()
        self.selected_tool = self.tools[self._selected_tool_id.get()]
        self.selected_tool.activate()

    def create_text_with_bg(self, *args, **kw) -> tuple[int, int]:
        """Creates a label with a specific bg color to ensure readability. Used for model component labels."""
        bg_tag = kw.pop("bg_tag", self.TEXT_BG_TAG)
        bg_color = kw.pop("bg_color", self["background"])
        kw.setdefault("anchor", tk.CENTER)
        kw.setdefault("font", ('Helvetica', self.TEXT_SIZE))
    
        text_id = super().create_text(*args, **kw)
        bounds = self.bbox(text_id)
    
        bg_id = self.create_rectangle(bounds[0], bounds[1], 
                                 bounds[2], bounds[3],
                                 width=0,
                                 fill=bg_color, 
                                 tags=bg_tag)
        self.tag_raise(bg_id)
        self.tag_raise(text_id)
        return text_id, bg_id

    def get_component_shapes(self):
        return [shape for shape in self.shapes if isinstance(shape, ComponentShape)]

    def find_shape_at(self, x: int, y: int) -> Shape | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: shape.is_at(x, y), self.shapes), None)

    def find_shape_of_list_at(self, shapes: list[ComponentShape], x: int, y: int) -> ComponentShape | None:
        """Check if there is a shape that is included in the list in the diagram at the specified coordinate."""
        return next(filter(lambda shape: shape.is_at(x, y), shapes), None)

    def find_shape_of_type_at(self, component_type: Type[C], x: int, y: int) -> ComponentShape[C] | None:
        """Check if there is a component shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: isinstance(shape.component, component_type) and shape.is_at(x, y), self.get_component_shapes()), None)

    def find_component_of_type_at(self, component_type: Type[C], x: int, y: int) -> C | None:
        shape = self.find_shape_of_type_at(component_type, x, y)
        return shape.component if shape else None

    def shape_for(self, component: C) -> ComponentShape[C]:
        return next(filter(lambda shape: shape.component == component, self.get_component_shapes()))

    def find_withtag(self, tagOrId: str | int) -> tuple[int, ...]:
        return tuple(filter(lambda id: (id == tagOrId) or (tagOrId in self.gettags(id)), self.find_all()))

    def find_except_withtags(self, *tagOrIds: str | int) -> tuple[int, ...]:
        return tuple([id for id in self.find_all() if all(id != tagOrId and tagOrId not in self.gettags(id) for tagOrId in tagOrIds)])

    def tag_lower(self, lower: str | int, upper: str | int | None = None) -> None:
        if self.find_withtag(lower) and (not upper or self.find_withtag(upper)):
            super().tag_lower(lower, upper)

    def delete_with_tag(self, tag: str):
        [self.delete(shape) for shape in self.find_withtag("temp")]

    def process_entry(self, entry: ttk.Entry, min: float, max: float, variable: tk.DoubleVar):
        try:
            value = float(entry.get())
        except ValueError:
            self.set_entry_text(entry, variable.get())
            return
        if min <= value <= max:
            variable.set(value)

    def set_entry_text(self, entry: ttk.Entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, str(text))