from abc import abstractmethod
import tkinter as tk
from tkinter import ttk
from typing import Generic, TypeVar

from c2d_app import TwlApp
from c2d_style import Colors
from c2d_images import add_image_from_path
from c2d_widgets import BorderFrame, CustomEntry
from c2d_update import UpdateManager
from c2d_math import Point, Line
from c2d_help import f_range
from c2d_components import Attribute, Component, Model, Node, Beam, Support, Force
from c2d_diagram import Tool
from c2d_model_diagram import ModelDiagram, ComponentShape, NodeShape, BeamShape, SupportShape, ForceShape


class SelectTool(Tool):

    ID: int = 0
    NAME: str = "Select"
    DESCR: str = "Select objects in model."
    ICON: str = "img/select_icon.png"

    def __init__(self, diagram: 'DefinitionDiagram'):
        super().__init__(diagram)
        self.selection_rect: int | None = None

    def activate(self):
        self.diagram.bind("<Button-1>", self.action)
        self.diagram.bind("<B1-Motion>", self.continue_rect_selection)
        self.diagram.bind("<ButtonRelease-1>", self.end_rect_selection)
        self.diagram.bind("<Escape>", lambda *ignore: self.reset())
        self.diagram.bind("<Delete>", self.delete_selected)

    def deactivate(self):
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<B1-Motion>")
        self.diagram.unbind("<ButtonRelease-1>")
        self.diagram.unbind("<Escape>")
        self.diagram.unbind("<Delete>")

    def reset(self):
        super().reset()
        if self.selection_rect:
            self.diagram.delete(self.selection_rect)
            self.selection_rect = None
        [shape.deselect() for shape in self.diagram.selection.copy()]

    @property
    def selectable_shapes(self) -> list[ComponentShape]:
        return list(filter(lambda shape: isinstance(shape.component, (Beam, Support, Force)), self.diagram.component_shapes))

    def action(self, event) -> bool:
        self.correct_scrolling(event)
        self.diagram.focus_set()

        pos = Point(event.x, event.y)
        pos.scale(1 / (self.diagram.current_zoom.get() / 100))
        shape = self.diagram.find_shape_of_list_at(self.selectable_shapes, pos.x, pos.y)

        if shape == None:
            self.start_rect_selection(event)
        else:
            self.process_selection(event, shape)
        return True

    def start_rect_selection(self, event):
        self.selection_rect = self.diagram.create_rectangle(event.x, event.y, event.x, event.y, outline=ComponentShape.SELECTED_COLOR, width=2)

    def continue_rect_selection(self, event):
        self.correct_scrolling(event)
        if not self.selection_rect:
            return
        start_x, start_y, _, _ = self.diagram.coords(self.selection_rect)
        self.diagram.coords(self.selection_rect, start_x, start_y, event.x, event.y)
        #self.diagram.update_coords_label(event)

    def end_rect_selection(self, event):
        if not self.selection_rect:
            return
        x1, y1, x2, y2 = map(int, self.diagram.coords(self.selection_rect))
        p1 = Point(x1, y1)
        p2 = Point(x2, y2)
        p1.scale(1 / (self.diagram.current_zoom.get() / 100))
        p2.scale(1 / (self.diagram.current_zoom.get() / 100))
        print(f"Selected area: ({p1.x}, {p1.y}) to ({p2.x}, {p2.y})")
        selection = [shape for shape in self.selectable_shapes if all(polygon.in_bounds(p1, p2) for polygon in shape.tk_shapes.values())]
        self.process_selection(event, *selection)

    def process_selection(self, event, *selection: ComponentShape):
        if self.holding_shift_key(event):
            for shape in selection:
                if shape in self.diagram.selection:
                    shape.deselect()
                else:
                    shape.select()
            if self.selection_rect:
                self.diagram.delete(self.selection_rect)
                self.selection_rect = None
        else:
            self.reset()
            for shape in selection:
                shape.select()

    def delete_selected(self, event):
        TwlApp.update_manager().pause_observing()
        [shape.component.delete() for shape in self.diagram.selection]
        TwlApp.update_manager().resume_observing()
        self.reset()


class TempNodeShape(NodeShape):

    TAG: str = ComponentShape.TEMP
    COLOR: str = ComponentShape.TEMP_COLOR

    def __init__(self, node: Node, diagram: 'DefinitionDiagram') -> None:
        super().__init__(node, diagram)
        self.scale(self.diagram.current_zoom.get() / 100)
        self.set_label_visible(False)


class TempBeamShape(BeamShape):

    TAG: str = ComponentShape.TEMP
    COLOR: str = ComponentShape.TEMP_COLOR

    def __init__(self, beam: Beam, diagram: 'DefinitionDiagram') -> None:
        super().__init__(beam, diagram)
        self.scale(self.diagram.current_zoom.get() / 100)
        self.set_label_visible(False)


class TempSupportShape(SupportShape):

    TAG: str = ComponentShape.TEMP
    COLOR = ComponentShape.TEMP_COLOR

    def __init__(self, support: Support, diagram: 'DefinitionDiagram') -> None:
        super().__init__(support, diagram)
        self.scale(self.diagram.current_zoom.get() / 100)
        self.set_label_visible(False)


class TempForceShape(ForceShape):

    TAG: str = ComponentShape.TEMP
    COLOR = ComponentShape.TEMP_COLOR

    def __init__(self, force: Force, diagram: 'DefinitionDiagram') -> None:
        super().__init__(force, diagram)
        self.scale(self.diagram.current_zoom.get() / 100)
        self.set_label_visible(False)


C = TypeVar("C", bound='Component')

class ComponentTool(Generic[C], Tool):

    COMPONENT_TYPE: type[C]

    def __init__(self, diagram: 'DefinitionDiagram'):
        self.diagram: 'DefinitionDiagram' = diagram
        self.component = self.dummy_component()
        self.popup: ComponentToolPopup | None = None

    def reset(self):
        super().reset()
        self.component = self.dummy_component()
        if self.popup:
            self.diagram.unbind("<Tab>")
            self.popup.destroy()
            self.popup = None

    def dummy_component(self) -> C:
        component: C = self.COMPONENT_TYPE.dummy()
        component.model = TwlApp.model()
        component._id._value = TwlApp.model().next_unique_id_for(self.COMPONENT_TYPE)
        return component

    def activate(self):
        super().activate()
        self.component = self.dummy_component()
        self.diagram.bind("<Motion>", self._move)

    def deactivate(self):
        super().deactivate()
        self.diagram.unbind("<Motion>")
        self.diagram.bind("<Motion>", self.diagram.update_coords_label)

    def _snap_event_to_grid(self, event):
        if TwlApp.settings().show_grid.get():
            snap_point = self.diagram.grid_snap(event.x, event.y)
            event.x = snap_point[0]
            event.y = snap_point[1]

    def _action(self, event):
        self.diagram.focus_set()
        self.correct_event_pos(event)
        self._snap_event_to_grid(event)
        if self.action(event):
            self._create_component()

    def _create_component(self) -> C:
        TwlApp.update_manager().pause_observing()
        component = self.create_component()
        TwlApp.update_manager().resume_observing()
        self.reset()
        return component

    def _move(self, event):
        self.diagram.focus_set()
        self.diagram.delete_with_tag(ComponentShape.TEMP)
        self.correct_event_pos(event)
        self._snap_event_to_grid(event)
        if self.prepare(event):
            self._preview()
        self.diagram.update_coords_label(event)

    def _preview(self):
        """Preview of the action with temporary shape and popup once a temp component is ready to be displayed."""
        self.show_temp_shape()
        if self.popup:
            self.popup.has_focus.set(False)
            self.popup.refresh()
        else:
            self.popup = ComponentToolPopup(self)
            self.diagram.bind("<Tab>", self.popup.cycle_focus)

    @abstractmethod
    def prepare(self, event) -> bool:
        """Prepare the preview."""
        return False

    @abstractmethod
    def show_temp_shape(self):
        pass

    @abstractmethod
    def create_component(self) -> C:
        pass


class ComponentToolPopup(tk.Toplevel):

    BORDER = 1
    DIAGRAM_PADDING = 46
    BORDER_PADDING = 6
    CONTENT_PADDING = 2

    def __init__(self, tool: ComponentTool[C]):
        super().__init__(tool.diagram)
        self.wm_overrideredirect(True)
        self.attributes("-topmost", True)
        self.has_focus = tk.BooleanVar()
        self.has_focus.trace_add("write", lambda *ignore: self.style_focus())
        self.tool = tool
        self.component = tool.component
        self.diagram = tool.diagram
        self.background = tk.Frame(self)
        self.background.pack(padx=self.BORDER, pady=self.BORDER)
        self.content = tk.Frame(self.background)
        self.content.pack(padx=self.BORDER_PADDING, pady=self.BORDER_PADDING)
        self.entries: dict[Attribute, tk.Entry] = {}
        self.labels: list[tk.Label] = []
        self.bind("<FocusOut>", lambda *ignore: self.has_focus.set(False))

        self.create_label("[Tab] to edit:", 0, 0, 3)
        self.entries = {}
        for i, attr in enumerate(self.component.attributes):
            if attr.EDITABLE:
                self.create_label(f"{attr.NAME}:", 0, i + 1)
                entry = CustomEntry(self.content, attr.filter, width=6, justify=tk.LEFT, bd=0)
                entry.variable.trace_add("write", lambda *ignore: self.value_changed())
                entry.insert(0, attr.get_display_value())
                entry.grid(column=1, row=i + 1, pady=self.CONTENT_PADDING)
                entry.bind("<FocusIn>", lambda *ignore: self.has_focus.set(True))
                entry.bind("<Escape>", lambda *ignore: self.diagram.focus_set())
                entry.bind("<Return>", lambda *ignore: self.on_return())
                self.entries[attr] = entry
                self.create_label(f"{attr.UNIT}", 2, i + 1)

        self.update_idletasks()
        x_position = self.diagram.winfo_rootx() + self.diagram.winfo_width() - self.DIAGRAM_PADDING - self.winfo_width()
        y_position = self.diagram.winfo_rooty() + self.diagram.winfo_height() - self.DIAGRAM_PADDING - self.winfo_height()
        self.wm_geometry(f"+{x_position}+{y_position}")
        self.style_focus()
        self.bind("<Tab>", self.cycle_focus)

    def on_return(self):
        if all([attr.filter(entry.get())[0] for attr, entry in self.entries.items()]):
            self.update_component()
            self.tool._create_component()

    def value_changed(self):
        if self.has_focus.get():
            self.update_component()
            self.tool.show_temp_shape()

    def update_component(self):
        [attr.set_value(entry.get()) for attr, entry in self.entries.items()]

    def create_label(self, text: str, column: int, row: int, columnspan: int=1):
        label = tk.Label(self.content, text=text, anchor=tk.W)
        self.labels.append(label)
        label.grid(column=column, row=row, columnspan=columnspan, sticky=tk.W, padx=self.CONTENT_PADDING, pady=self.CONTENT_PADDING)

    def refresh(self):
        for attr, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, attr.get_display_value())

    def cycle_focus(self, event):
        entries = list(self.entries.values())
        current_focus = self.focus_get()
        next_index = (entries.index(current_focus) + 1) % len(entries) if current_focus in entries else 0
        entries[next_index].focus_set()
        entries[next_index].select_range(0, tk.END)
        return "break"

    def style_focus(self):
        bd_color = Colors.BLACK if self.has_focus.get() else Colors.VERY_LIGHT_GRAY
        fg_color = Colors.BLACK if self.has_focus.get() else Colors.VERY_DARK_GRAY
        bg_color = Colors.WHITE
        [entry.configure(bg=bg_color, fg=fg_color) for entry in self.entries.values()]
        [label.configure(bg=bg_color, fg=fg_color) for label in self.labels]
        self.configure(bg=bd_color)
        self.background.configure(bg=bg_color)
        self.content.configure(bg=bg_color)

    def destroy(self):
        self.unbind("<Tab>")
        super().destroy()


class BeamTool(ComponentTool[Beam]):

    COMPONENT_TYPE = Beam
    ID: int = 1
    NAME: str = "Beam Tool"
    DESCR: str = "Create beam between two nodes."
    ICON: str = "img/beam_icon.png"

    def __init__(self, diagram: 'DefinitionDiagram'):
        super().__init__(diagram)
        self.start_node: Node | None = None
        self.end_node: Node | None = None

    def reset(self):
        super().reset()
        self.start_node = None
        self.end_node = None

    def action(self, event):
        clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
        if self.start_node is None:
            self.start_node = clicked_node if clicked_node else Node.dummy(event.x, event.y)
            self.component._start_node._value = self.start_node
            return False
        else:
            if self.holding_shift_key(event):
                self.shift_snap_line(event)
            self.end_node = clicked_node if clicked_node else Node.dummy(event.x, event.y)
            self.component._end_node._value = self.end_node
            return True

    def create_component(self) -> Beam:
        if not self.component.start_node in TwlApp.model().nodes:
            self.component._start_node._value = Node(TwlApp.model(), self.component.start_node.x, self.component.start_node.y)
            TwlApp.model().nodes.append(self.component.start_node)
        if not self.component.end_node in TwlApp.model().nodes:
            self.component._end_node._value = Node(TwlApp.model(), self.component.end_node.x, self.component.end_node.y)
            TwlApp.model().nodes.append(self.component.end_node)
        beam = Beam(TwlApp.model(), self.component.start_node, self.component.end_node, self.component.id)
        TwlApp.model().beams.append(beam)
        return beam

    def _create_component(self) -> Beam:
        beam = super()._create_component()
        self.start_node = beam.end_node
        return beam

    def prepare(self, event) -> bool:
        existing_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
        if not self.start_node:
            if not existing_node:
                self.diagram.delete_with_tag(ComponentShape.TEMP)
                TempNodeShape(Node.dummy(event.x, event.y), self.diagram)
            return False
        else:
            if self.holding_shift_key(event):
                self.shift_snap_line(event)
            self.end_node = existing_node if existing_node else Node.dummy(event.x, event.y)
            self.component._start_node._value = self.start_node
            self.component._end_node._value  = self.end_node
            return True

    def shift_snap_line(self, event):
        assert(self.start_node)
        start_point = Point(self.start_node.x, self.start_node.y)
        inital_line = Line(start_point, Point(event.x, event.y))
        rounded_line = Line(start_point, Point(start_point.x, start_point.y + 10))
        rounded_line.rotate(start_point, inital_line.angle_rounded())
        new_point = rounded_line.closest_point_on_axis(Point(event.x, event.y))
        event.x = new_point.x
        event.y = new_point.y

    def show_temp_shape(self):
        self.diagram.delete_with_tag(ComponentShape.TEMP)
        assert(self.start_node)
        assert(self.end_node)
        if self.start_node not in TwlApp.model().nodes:
            TempNodeShape(self.start_node, self.diagram)
        if self.end_node not in TwlApp.model().nodes:
            TempNodeShape(self.end_node, self.diagram)
        TempBeamShape(self.component, self.diagram)


class SupportTool(ComponentTool[Support]):

    COMPONENT_TYPE = Support
    ID: int = 2
    NAME: str = "Support Tool"
    DESCR: str = "Create support on node."
    ICON: str = "img/support_icon.png"

    def __init__(self, diagram: 'DefinitionDiagram'):
        super().__init__(diagram)
        self.node: Node | None = None

    def reset(self):
        super().reset()
        self.node = None

    def action(self, event):
        if not self.node:
            clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if clicked_node and not clicked_node.supports:
                self.node = clicked_node
                self.component._node._value = self.node
            return False
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.component._angle._value = angle
            return True

    def create_component(self) -> Support:
        support = Support(TwlApp.model(), self.component.node, self.component.angle, self.component.constraints, self.component.id)
        TwlApp.model().supports.append(support)
        return support

    def prepare(self, event) -> bool:
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node and not hovering_node.supports:
                TempSupportShape(Support(Model(UpdateManager()), hovering_node), self.diagram)
            return False
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.component._angle._value = angle
            return True

    def show_temp_shape(self):
        self.diagram.delete_with_tag(ComponentShape.TEMP)
        TempSupportShape(self.component, self.diagram)


class ForceTool(ComponentTool[Force]):

    COMPONENT_TYPE = Force
    ID: int = 3
    NAME: str = "Force Tool"
    DESCR: str = "Create force on node."
    ICON: str = "img/force_icon.png"

    def __init__(self, diagram: 'DefinitionDiagram'):
        super().__init__(diagram)
        self.node: Node | None = None

    def reset(self):
        super().reset()
        self.node = None

    def action(self, event):
        if not self.node:
            clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if clicked_node:
                self.node = clicked_node
                self.component._node._value = self.node
            return False
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.component._angle._value = angle
            return True

    def create_component(self) -> Force:
        force = Force(TwlApp.model(), self.component.node, self.component.angle, self.component.strength, self.component.id)
        TwlApp.model().forces.append(force)
        return force

    def prepare(self, event) -> bool:
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node:
                TempForceShape(Force(Model(UpdateManager()), hovering_node), self.diagram)
            return False
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            self.component._angle._value = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            return True

    def show_temp_shape(self):
        self.diagram.delete_with_tag(ComponentShape.TEMP)
        TempForceShape(self.component, self.diagram)


class DefinitionDiagram(ModelDiagram):

    GRID_TAG = "grid"
    GRID_COLOR = "lightgrey"
    GRID_SNAP_RADIUS = 5
    MIN_GRID = 0.1
    MAX_GRID = 500

    ANGLE_GUIDE_TAG = "angle_guide"
    ANGLE_GUIDE_IMG = "img/angle_guide.png"
    ANGLE_GUIDE_SIZE = 120
    ANGLE_GUIDE_PADDING = 10

    SHOW_TOOLBAR: bool = True

    NO_UPDATE_TAGS = [GRID_TAG, ANGLE_GUIDE_TAG]

    def __init__(self, master):

        #toolbar
        toolbar: ttk.Frame = ttk.Frame(master, style="Diagram.TFrame")
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        #grid
        self.grid_step = tk.DoubleVar(value=20.0)
        self.grid_step.trace_add("write", lambda *ignore: self.refresh())
        TwlApp.settings().show_grid.trace_add("write", lambda *ignore: self.refresh())

        #diagram
        diagram_frame: ttk.Frame = ttk.Frame(master)
        diagram_frame.pack(fill=tk.BOTH, expand=True)
        super().__init__(diagram_frame)

        #statically determinate label
        self.stat_determ_label = ttk.Label(self, style= "Diagram.TLabel", text=self.stat_determ_text)
        self.stat_determ_label.place(x=self.UI_PADDING, y=self.UI_PADDING)

        #angle guide
        self.angle_guide_visible: bool = False
        angle_guide_img = add_image_from_path(self.ANGLE_GUIDE_IMG, self.ANGLE_GUIDE_SIZE, self.ANGLE_GUIDE_SIZE)
        self.angle_guide = self.create_image(self.winfo_width() - self.ANGLE_GUIDE_PADDING, 
                                             self.ANGLE_GUIDE_PADDING, 
                                             image=angle_guide_img, 
                                             anchor=tk.NE, 
                                             tags=self.ANGLE_GUIDE_TAG)
        TwlApp.settings().show_angle_guide.trace_add("write", lambda *ignore: self.refresh())

        #coords label
        self.coords_label = ttk.Label(self, foreground=Colors.GRAY)
        self.bind("<Motion>", self.update_coords_label)
        self.coords_label.place(x=self.winfo_width() - self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SE)

        #tools
        self.tools: list[Tool] = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool: Tool = self.tools[0]
        for tool in self.tools: 
            self.add_button(tool, toolbar)
        self.select_tool(SelectTool.ID)
        BorderFrame(toolbar).pack(fill="both", expand=True)

    def refresh(self, event=None):
        super().refresh(event)
        self.delete_grid()
        if TwlApp.settings().show_grid.get():
            self.draw_grid()

        self.update_angle_guide_position()
        self.coords_label.place(x=self.winfo_width() - self.UI_PADDING, y=self.winfo_height() - self.UI_PADDING, anchor=tk.SE)

        angle_guide_state = tk.NORMAL if TwlApp.settings().show_angle_guide.get() else tk.HIDDEN
        self.itemconfigure(self.angle_guide, state=angle_guide_state)

    def update_observer(self, component_id: str="", attribute_id: str=""):
        super().update_observer(component_id, attribute_id)

        self.stat_determ_label.configure(text=self.stat_determ_text)
        color = Colors.GREEN if self.stat_determ_text[:5] == "f = 0" else Colors.RED
        ttk.Style().configure("Diagram.TLabel", foreground=color)

        self.tag_lower(self.GRID_TAG)
        self.tag_raise(self.ANGLE_GUIDE_TAG)

    def create_bottom_bar(self) -> tk.Frame:
        bottom_bar = super().create_bottom_bar()
        show_grid_var = TwlApp.settings().show_grid
        grid_check = ttk.Checkbutton(bottom_bar, text="Grid ", style="Custom.TCheckbutton", takefocus=False, variable=show_grid_var)
        grid_check.pack(side=tk.LEFT, padx=(self.UI_PADDING, 0))
        grid_entry = ttk.Entry(bottom_bar, width=5, justify=tk.RIGHT)
        show_grid_var.trace_add("write", lambda *ignore: grid_entry.pack(side=tk.LEFT) if show_grid_var.get() else grid_entry.pack_forget())
        grid_entry.bind("<Return>", lambda *ignore: self.process_entry(grid_entry, self.MIN_GRID, self.MAX_GRID, self.grid_step))
        grid_entry.bind("<FocusOut>", lambda *ignore: self.set_entry_text(grid_entry, self.grid_step.get()))
        self.grid_step.trace_add("write", lambda *ignore: self.set_entry_text(grid_entry, self.grid_step.get()))
        self.set_entry_text(grid_entry, self.grid_step.get())
        grid_entry.pack(side=tk.LEFT, padx=(0, 0))
        cm_label = ttk.Label(bottom_bar, text="cm")
        show_grid_var.trace_add("write", lambda *ignore: cm_label.pack(side=tk.RIGHT) if show_grid_var.get() else cm_label.pack_forget())
        cm_label.pack(side=tk.LEFT)
        return bottom_bar

    def update_angle_guide_position(self):
        x_min, y_min, x_max, y_max = self.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        self.coords(self.angle_guide, self.winfo_width() + (self.xview()[0] * sr_width) - abs(x_min) - self.ANGLE_GUIDE_PADDING, 
                    self.ANGLE_GUIDE_PADDING + (self.yview()[0] * sr_height) - abs(y_min))

    def delete_grid(self):
        self.delete(self.GRID_TAG)

    def draw_grid(self):
        grid_spacing = self.grid_step.get() * self.current_zoom.get() / 100
        x_min, y_min, x_max, y_max = self.get_scrollregion()
        x_start = x_min - (x_min % grid_spacing) + grid_spacing
        y_start = y_min - (y_min % grid_spacing) + grid_spacing
        for i in f_range(x_start, x_max, grid_spacing):
            self.create_line((i, y_min), (i, y_max), fill=self.GRID_COLOR, tags=self.GRID_TAG)
        for i in f_range(y_start, y_max, grid_spacing):
            self.create_line((x_min, i), (x_max, i), fill=self.GRID_COLOR, tags=self.GRID_TAG)
        self.tag_lower(self.GRID_TAG)

    def grid_snap(self, x: float, y: float) -> tuple[float, float]:
        grid_spacing = self.grid_step.get()
        nearest_x = round(x / grid_spacing) * grid_spacing
        nearest_y = round(y / grid_spacing) * grid_spacing
        distance = Point(x, y).distance_to_point(Point(nearest_x, nearest_y))
        if distance < TwlApp.settings().grid_snap_radius.get():
            return nearest_x, nearest_y
        return x, y

    @property
    def stat_determ_text(self) -> str:
        """Get the explanation text about static determinacy."""
        nodes = len(TwlApp.model().nodes)
        equations = 2 * nodes
        constraints = sum(support.constraints for support in TwlApp.model().supports)
        beams = len(TwlApp.model().beams)
        unknowns = constraints + beams
        f = equations - unknowns
        return f"f = {f}, the model ist statically {"" if f == 0 else "in"}determinate.\n{equations} equations (2 * {nodes} nodes)\n{unknowns} unknowns ({constraints} for supports, {beams} for beams)"

    def update_coords_label(self, event):
        self.coords_label.config(text=f"x: {int(event.x)} y: {int(event.y)}")