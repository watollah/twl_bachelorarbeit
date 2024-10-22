import tkinter as tk
from tkinter import ttk
from typing import TypeVar, Generic, Type
from abc import abstractmethod

from c2d_update import Observer
from c2d_widgets import CustomRadioButton
from c2d_style import Colors
from c2d_images import add_png_by_name
from c2d_components import Component, IdAttribute
from c2d_math import Point, Polygon


class Shape():
    """Represents a generic Shape in the diagram."""

    TAGS: list[str] = []
    TAG = "shape"

    COLOR = "black"
    BG_COLOR = "white"

    def __init__(self, diagram: 'TwlDiagram') -> None:
        """Create an instance of Shape."""
        self.diagram: 'TwlDiagram' = diagram
        self.tk_shapes: dict[int, Polygon] = {} #all tk_ids related to this shape with their position in the diagram

    def scale(self, factor: float):
        """Scale the shape with a factor. Takes all tkinter shapes connected to this shape 
        and changes their coordinates by scaling the polygon connected to each id."""
        for tk_id, polygon in self.tk_shapes.items():
            coords = [coord * factor for point in polygon.points for coord in (point.x, point.y)]
            self.diagram.coords(tk_id, coords)

    def move(self, x: int, y: int):
        """Move the shape by the specified amount in the x and y direction 
        by moving them directly in the diagram and also moving the position of the stored polygons."""
        for tk_id, polygon in self.tk_shapes.items():
            self.diagram.move(tk_id, x, y)
            polygon.move(x, y)

    def set_visible(self, visible: bool):
        """Set the visibility state of all tkinter shapes connected to this shape."""
        state = tk.NORMAL if visible else tk.HIDDEN
        for tk_id in self.tk_shapes.keys():
            self.diagram.itemconfig(tk_id, state=state)

    @abstractmethod
    def is_at(self, x: float, y: float) -> bool:
        """Always returns False. Default implementation of check to see if the shape is at the specified position in the diagram."""
        return False


C = TypeVar('C', bound=Component)

class ComponentShape(Generic[C], Shape, Observer):
    """Represents the shape of a component in the diagram."""

    TEMP = "temp"
    TEMP_COLOR = "lightgrey"

    SELECTED_COLOR = Colors.DARK_SELECTED
    SELECTED_BG_COLOR = Colors.LIGHT_SELECTED

    LABEL_TAG = "label"
    LABEL_BG_TAG = "label_background"
    LABEL_PREFIX = ""
    LABEL_SIZE = 12

    def __init_subclass__(cls):
        """When initializing a subclass of ComponentShape, add the tag specified in the subclasses TAG to the subclasses TAGS."""
        super().__init_subclass__()
        cls.TAGS = cls.TAGS.copy()
        cls.TAGS.append(cls.TAG)

    def __init__(self, component: C, diagram: 'TwlDiagram'):
        """Create an instance of ComponentShape."""
        super().__init__(diagram)
        self.component: C = component
        if self.TEMP not in self.TAGS:
            self.component.model.update_manager.register_observer(self)
        self.draw_label()

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update the component shape. Updates the id label if the id attribute is changed."""
        if component_id == self.component.id and attribute_id == IdAttribute.ID:
            self.set_label_text(self.component.id)
            self.diagram.refresh()
        super().update_observer(component_id, attribute_id)

    def remove(self):
        """Remove all tkinter shapes connected to this shape from the diagram and remove the shape itself from the diagrams shape list."""
        for tk_id in self.tk_shapes.keys():
            self.diagram.delete(tk_id)
        self.diagram.shapes.remove(self)

    def select(self):
        """Append this shape to the selection of the diagram and style all of it's tkinter shapes with the shape's selected style."""
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=self.SELECTED_COLOR)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, self.selected_style(*tags))
        self.diagram.selection.append(self)
        print(f"selected: {self.component.id}")

    def deselect(self):
        """Remove this shape from the selection of the diagram and style all of it's tkinter shapes with the shape's default style."""
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
        self.diagram.itemconfig(self.label_tk_id, font=('Helvetica', int(self.LABEL_SIZE * factor)))

    def draw_label(self):
        """Draw the label at the position specified in the shapes label position and with the value of the shape's component's id."""
        label_pos = self.label_position
        self.label_tk_id, self.label_bg_tk_id = self.diagram.create_text_with_bg(label_pos.x, label_pos.y, 
                                 text=self.component.id, 
                                 tags=[*self.TAGS, str(self.component.id)],
                                 label_tag=self.LABEL_TAG,
                                 bg_tag=self.LABEL_BG_TAG,
                                 font=('Helvetica', self.LABEL_SIZE))
        self.tk_shapes[self.label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
        x1, x2, y1, y2 = self.diagram.bbox(self.label_tk_id)
        self.tk_shapes[self.label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

    @property
    @abstractmethod
    def label_position(self) -> Point:
        """Get the position of the label of this shape in the diagram. Returns point at the top right corner of diagram for Shapes that don't use labels."""
        return Point(TwlDiagram.SCROLL_EXTEND + TwlDiagram.UI_PADDING, TwlDiagram.SCROLL_EXTEND + TwlDiagram.UI_PADDING)

    def set_label_text(self, text: str):
        """Change the text of this shape's label and reset it's size and position accordingly."""
        self.diagram.itemconfig(self.label_tk_id, text=text)
        self.update_label_pos()

    def set_label_visible(self, visible: bool):
        """Change the state of visibilty of this shape's label."""
        state = tk.NORMAL if visible else tk.HIDDEN
        self.diagram.itemconfig(self.label_tk_id, state=state)
        self.diagram.itemconfig(self.label_bg_tk_id, state=state)

    def update_label_pos(self):
        """Reset this shape's label position, for example after the shape is moved."""
        label_pos = self.label_position
        self.tk_shapes[self.label_tk_id] = Polygon(label_pos)
        self.diagram.coords(self.label_tk_id, label_pos.x, label_pos.y)
        self.diagram.update_idletasks()
        if self.diagram.bbox(self.label_tk_id):
            x1, x2, y1, y2 = self.diagram.bbox(self.label_tk_id)
            self.tk_shapes[self.label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))
        else:
            print(f"Warning: Label not found for {self.component.id}")


class Tool:
    """Base class for all tools in diagrams. Handles binding of actions used by all tools 
    and correction of event positions for scrolling and zooming."""

    ID: int = -1
    NAME: str = "X"
    DESCR: str = "X"
    ICON: str = "X"

    def __init__(self, diagram: 'TwlDiagram'):
        """Create an instance of Tool."""
        self.diagram: 'TwlDiagram' = diagram

    def activate(self):
        """Activate the tool by binding events."""
        self.diagram.bind("<Button-1>", self._action)
        self.diagram.bind("<Escape>", lambda *ignore: self.reset())
        self.diagram.bind("<Leave>", lambda *ignore: self.diagram.delete_temp_shapes())

    def deactivate(self):
        """Deactivate the tool by unbinding events."""
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<Escape>")
        self.diagram.unbind("<Leave>")
        self.reset()

    def reset(self):
        """Reset the tool by deleting all temporary component shapes."""
        self.diagram.delete_temp_shapes()

    def correct_event_pos(self, event):
        """Correct the coordinates of the mouse pointer to account for scrolling and scaling of the diagram."""
        self.correct_scrolling(event)
        self.correct_scaling(event)

    def correct_scrolling(self, event):
        """Correct the event position to account for scrolling in the diagram."""
        x_min, y_min, x_max, y_max = self.diagram.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        event.x = event.x + self.diagram.xview()[0] * sr_width - abs(x_min)
        event.y = event.y + self.diagram.yview()[0] * sr_height - abs(y_min)

    def correct_scaling(self, event):
        """Correct the event position to account for scaling in the diagram."""
        event.x = event.x * (1 / (self.diagram.current_zoom.get() / 100))
        event.y = event.y * (1 / (self.diagram.current_zoom.get() / 100))

    def _action(self, event):
        """Correct event position and execute action."""
        self.correct_event_pos(event)
        self.action(event)

    def action(self, event) -> bool:
        """Code to be executed when the user clicks on the canvas while the tool is active."""
        return True

    def holding_shift_key(self, event) -> bool:
        """Returns True if the user is holding the shift-key. Used for snapping and in selection."""
        return event.state & 0x1 #bitwise ANDing the event.state with the ShiftMask flag


class TwlDiagram(Observer, tk.Canvas):
    """Base class of the application's diagrams."""

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
        """Create an instance of TwlDiagram."""
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

        self.tools: list[Tool] = []
        self._selected_tool_id: tk.IntVar = tk.IntVar(value=0)
        self.selected_tool: Tool | None = None

        #bottom elements
        self.bottom_bar = self.create_bottom_bar()
        self.bottom_bar.place(x=self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SW)

        self.bind("<Configure>", lambda *ignore: self.refresh())
        self.bind("<Control-MouseWheel>", self.zoom)
        self.bind("<Shift-MouseWheel>", lambda event: self.scroll(tk.HORIZONTAL, "scroll", self.SCROLL_STEP if event.delta < 0 else -self.SCROLL_STEP))
        self.bind("<MouseWheel>", lambda event: self.scroll(tk.VERTICAL, "scroll", self.SCROLL_STEP if event.delta < 0 else -self.SCROLL_STEP))
        self.bind("<Button-2>", self.start_pan)
        self.bind("<B2-Motion>", self.pan)  
        self.bind("<ButtonRelease-2>", self.end_pan)  

        self.update_scrollregion()

    def refresh(self):
        """Configures diagram navigation and ui layout. Configures shape scale and visibility."""
        self.bottom_bar.place(x=self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SW)
        [shape.scale(self.current_zoom.get() / 100) for shape in self.shapes]
        self.update_scrollregion()

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update the diagram. Performs refresh."""
        self.refresh()

    def clear(self):
        """Removes all shapes from the diagram."""
        for shape in self.find_all():
            tags = set(self.gettags(shape))
            if not tags.intersection(self.NO_UPDATE_TAGS):
                self.delete(shape)
        self.shapes.clear()

    def create_bottom_bar(self) -> tk.Frame:
        """Create frame on bottom of the diagram that holds zoom control."""
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
        """Create the scrollbars around the diagram."""
        v_scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=lambda scrolltype, amount: self.scroll(tk.VERTICAL, scrolltype, amount))
        v_scrollbar.grid(column=1, row=0, sticky=tk.NS)

        h_scrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=lambda scrolltype, amount: self.scroll(tk.HORIZONTAL, scrolltype, amount))
        h_scrollbar.grid(column=0, row=1, sticky=tk.EW)

        corner = tk.Frame(master, background=Colors.LIGHT_GRAY)
        corner.grid(column=1, row=1, sticky=tk.NSEW)

        self.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

    def scroll(self, orientation: str, scroll_type: str, amount):
        """Scroll the diagram by a specific amount in a specific direction."""
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
        """Update the scrollable area of the canvas. Calculated with the bounds of all the shapes plus a margin."""
        shapes = [tk_id for shape in self.shapes for tk_id in shape.tk_shapes.keys() if self.itemcget(tk_id, "state") in (tk.NORMAL, "")]
        if shapes:
            bbox = self.bbox(*shapes)
            self.configure(scrollregion=(min(0, bbox[0] - self.SCROLL_EXTEND), 
                                     min(0, bbox[1] - self.SCROLL_EXTEND), 
                                     max(self.winfo_width(), bbox[2] + self.SCROLL_EXTEND), 
                                     max(self.winfo_height(), bbox[3] + self.SCROLL_EXTEND)))
        else:
            self.configure(scrollregion=(0, 0, self.winfo_width(), self.winfo_height()))

    def get_scrollregion(self) -> tuple[int, int, int, int]:
        """Get the dimensions of the currently configured scrollregion."""
        sr_str = self.cget("scrollregion") or "0 0 0 0"
        sr_int = tuple([int(num) for num in sr_str.split()])
        assert len(sr_int) == 4
        return sr_int

    def zoom(self, event):
        """Zoom the diagram one increment in or out depending on the direction the mousewheel was turned."""
        if event.delta < 0:
            self.current_zoom.set(max(self.MIN_ZOOM, self.current_zoom.get() - self.ZOOM_STEP))
        else:
            self.current_zoom.set(min(self.MAX_ZOOM, self.current_zoom.get() + self.ZOOM_STEP))
        self.refresh()

    def start_pan(self, event):
        """Start panning the diagram. Change cursor to cross arrows and store panning start position."""
        self.pan_start_pos = Point(event.x, event.y)
        self.pan_xview_start = self.xview()[0]
        self.pan_yview_start = self.yview()[0]
        self.config(cursor="fleur")

    def pan(self, event):
        """Pan the diagram."""
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
        """End panning the diagram. Restore default cursor."""
        self.config(cursor="")

    def add_tool_button(self, tool: Tool, toolbar: ttk.Frame):
        """Add a button for the tool to the diagrams toolbar."""
        image = add_png_by_name(tool.ICON, self.TOOL_BUTTON_SIZE, self.TOOL_BUTTON_SIZE)
        button = CustomRadioButton(toolbar, image=image, variable=self._selected_tool_id, value=tool.ID, command=self.handle_tool_change, outlinewidth=1)
        button.pack()

    def select_tool(self, tool_id: int):
        """Select the tool with the specified id."""
        self._selected_tool_id.set(tool_id)
        self.handle_tool_change()

    def handle_tool_change(self):
        """Perform tool change. Deactivate the previously selected tool and activate the new one."""
        if self.selected_tool:
            self.selected_tool.deactivate()
        self.selected_tool = self.tools[self._selected_tool_id.get()]
        self.selected_tool.activate()

    def create_text_with_bg(self, *args, **kw) -> tuple[int, int]:
        """Creates a label with a specific bg color to ensure readability. Used for ComponentShape labels."""
        tags = kw.pop("tags", [])
        label_tag = kw.pop("label_tag", self.TEXT_TAG)
        bg_tag = kw.pop("bg_tag", self.TEXT_BG_TAG)

        bg_color = kw.pop("bg_color", self["background"])
        kw.setdefault("anchor", tk.CENTER)
        kw.setdefault("font", ('Helvetica', self.TEXT_SIZE))
    
        text_id = super().create_text(*args, tags=[*tags, label_tag], **kw)
        bounds = self.bbox(text_id)
    
        bg_id = self.create_rectangle(bounds[0], bounds[1], 
                                 bounds[2], bounds[3],
                                 width=0,
                                 fill=bg_color, 
                                 tags=[*tags, bg_tag])
        self.tag_raise(bg_id)
        self.tag_raise(text_id)
        return text_id, bg_id

    def label_visibility(self):
        """Refresh the visibility of all ComponentShape labels."""
        [shape.set_label_visible(self.label_visible(shape)) for shape in self.component_shapes]

    def label_visible(self, shape: Shape) -> bool:
        """Returns weather the label for the specified shape should be visible in the diagram. Default is False."""
        return False

    @property
    def component_shapes(self):
        """Get all ComponentShapes from diagrams shapes."""
        return [shape for shape in self.shapes if isinstance(shape, ComponentShape)]

    def find_shape_at(self, x: float, y: float) -> Shape | None:
        """Returns shape in the diagram at the specified coordinate if it exists."""
        return next(filter(lambda shape: shape.is_at(x, y), self.shapes), None)

    S = TypeVar("S", bound=ComponentShape)
    def find_shape_of_list_at(self, shapes: list[S], x: float, y: float) -> S | None:
        """Returns shape that is included in the list in the diagram at the specified coordinate if it exists."""
        return next(filter(lambda shape: shape.is_at(x, y), shapes), None)

    def find_shape_of_type_at(self, component_type: Type[C], x: float, y: float) -> ComponentShape[C] | None:
        """Returns component shape of the specified type in the diagram at the specified coordinate if it exists."""
        return next(filter(lambda shape: isinstance(shape.component, component_type) and shape.is_at(x, y), self.component_shapes), None)

    def find_component_of_type_at(self, component_type: Type[C], x: float, y: float) -> C | None:
        """Returns a component of the specified type in the diagram that is at the specified coordinate if it exists."""
        shape = self.find_shape_of_type_at(component_type, x, y)
        return shape.component if shape else None

    def shapes_for(self, component: C) -> list[ComponentShape[C]]:
        """Returns all ComponentShapes in the diagram for the component."""
        return [shape for shape in self.component_shapes if shape.component == component]

    S = TypeVar('S', bound=Shape)
    def shapes_of_type_for(self, shape_type: Type[S], component: Component) -> list[S]:
        """Returns all shapes of a specified type for a component in the diagram."""
        return [shape for shape in self.shapes_for(component) if isinstance(shape, shape_type)]

    def find_withtag(self, tagOrId: str | int) -> tuple[int, ...]:
        """Returns tkinter shape ids for all shapes in the diagram that have this tag."""
        return tuple(filter(lambda id: (id == tagOrId) or (tagOrId in self.gettags(id)), self.find_all()))

    def find_withtags(self, *tags: str) -> int | None:
        """Returns tkinter shape ids for all shapes in the diagram that have all of these tags."""
        return next((id for id in self.find_all() if set(tags).issubset(set(self.gettags(id)))), None)

    def find_except_withtags(self, *tagOrIds: str | int) -> tuple[int, ...]:
        """Returns tkinter shape ids for all shapes in the diagram that don't have any of these tags."""
        return tuple([id for id in self.find_all() if all(id != tagOrId and tagOrId not in self.gettags(id) for tagOrId in tagOrIds)])

    def tag_lower(self, lower: str | int, upper: str | int | None = None) -> None:
        """Lower all shapes with lower tag under shapes with upper tag if specified, otherwise under all shapes.
        This method doesn't raise exception if there are no shapes with this tag in the diagram, unlike tkinter build-in method."""
        if self.find_withtag(lower) and (not upper or self.find_withtag(upper)):
            super().tag_lower(lower, upper)

    def delete_temp_shapes(self):
        """Delete all temporary shapes in the diagram. Temporary shapes are identified with temp tag."""
        [self.delete(shape) for shape in self.find_withtag(ComponentShape.TEMP)]

    def process_entry(self, entry: ttk.Entry, min: float, max: float, variable: tk.DoubleVar):
        """Process the value of an entry in the diagrams bottom bar. Check if the value is valid and within the specified min and max."""
        try:
            value = float(entry.get())
        except ValueError:
            self.set_entry_text(entry, variable.get())
            return
        if min <= value <= max:
            variable.set(value)

    def set_entry_text(self, entry: ttk.Entry, text):
        """Set the text in an entry. Clears the previous text."""
        entry.delete(0, tk.END)
        entry.insert(0, str(text))