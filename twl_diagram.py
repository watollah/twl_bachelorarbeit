import tkinter as tk
from typing import final, TypeVar, Generic
from tkinter import ttk

from twl_widget import *
from twl_components import *
from twl_help import *
from twl_settings import *


C = TypeVar('C', bound=Component)


class Shape(Generic[C]):
    """Represents the shape of a component in the TwlDiagram."""

    TAGS: List[str] = []
    TAG = "shape"
    TEMP = "temp"

    COLOR = "black"
    TEMP_COLOR = "lightgrey"
    BG_COLOR = "white"
    SELECTED_COLOR = "#0078D7"
    SELECTED_BG_COLOR = "#cce8ff"

    LABEL_TAG = "label"
    LABEL_BG_TAG = "label_background"
    LABEL_PREFIX = ""
    LABEL_SIZE = 12

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.TAGS = cls.TAGS.copy()
        cls.TAGS.append(cls.TAG)

    def __init__(self, component: C, diagram: 'TwlDiagram') -> None:
        self.component: C = component
        self.diagram: 'TwlDiagram' = diagram
        self.tk_id: int = -1

    def select(self):
        self.diagram.itemconfig(self.tk_id, self.selected_style)
        self.diagram.selection.append(self)
        print(f"selected: {self.component.id}")

    def deselect(self):
        self.diagram.itemconfig(self.tk_id, self.default_style)
        self.diagram.selection.remove(self)
        print(f"deselected: {self.component.id}")

    @abstractmethod
    def is_at(self, x: int, y: int) -> bool:
        return False

    @property
    @abstractmethod
    def default_style(self) -> dict[str, str]:
        """Style attributes when the shape is not selected."""
        pass

    @property
    @abstractmethod
    def selected_style(self) -> dict[str, str]:
        """Style attributes when the shape is selected."""
        pass

    @property
    @abstractmethod
    def label_position(self) -> Point:
        pass

    @property
    def label_text(self) -> str:
        return f"{self.LABEL_PREFIX}{self.component.id}"

    def draw_label(self):
        id = self.diagram.create_text(self.label_position.x, 
                                 self.label_position.y, 
                                 text=self.label_text, 
                                 anchor=tk.CENTER, 
                                 tags=self.LABEL_TAG,
                                 font=('Helvetica', self.LABEL_SIZE))
        bounds = self.diagram.bbox(id)
        self.diagram.create_rectangle(bounds[0], bounds[1], 
                                 bounds[2], bounds[3],
                                 width=0,
                                 fill=self.diagram["background"], 
                                 tags=self.LABEL_BG_TAG)
        self.diagram.tag_lower(self.LABEL_BG_TAG, self.LABEL_TAG)


class NodeShape(Shape[Node]):

    TAG: str = "node"

    RADIUS: int = 6
    BORDER: int = 2

    LABEL_OFFSET = 15

    def __init__(self, node: Node, diagram: 'TwlDiagram') -> None:
        super().__init__(node, diagram)
        self.tk_id = diagram.create_oval(node.x - self.RADIUS, 
                            node.y - self.RADIUS, 
                            node.x + self.RADIUS, 
                            node.y + self.RADIUS, 
                            fill=self.BG_COLOR, 
                            outline=self.COLOR, 
                            width = self.BORDER, 
                            tags=[*self.TAGS, str(node.id)])
        if (not self.TAG == Shape.TEMP) and diagram.settings.show_node_labels.get(): 
            self.draw_label()

    def is_at(self, x: int, y: int) -> bool:
        return True if abs(self.component.x - x) <= self.RADIUS and abs(self.component.y - y) <= self.RADIUS else False

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    @property
    def label_position(self) -> Point:
        return Point(self.component.x + self.LABEL_OFFSET, self.component.y - self.LABEL_OFFSET)

    @property
    def label_text(self) -> str:
        return f"{self.LABEL_PREFIX}{int_to_roman(self.component.id)}"

class TempNodeShape(NodeShape):

    TAG: str = Shape.TEMP
    COLOR: str = Shape.TEMP_COLOR


class BeamShape(Shape[Beam]):

    TAG: str = "beam"
    WIDTH: int = 4

    def __init__(self, beam: Beam, diagram: 'TwlDiagram') -> None:
        super().__init__(beam, diagram)
        self.tk_id = diagram.create_line(beam.start_node.x,
                            beam.start_node.y,
                            beam.end_node.x,
                            beam.end_node.y,
                            fill=self.COLOR,
                            width=self.WIDTH,
                            tags=[*self.TAGS, str(beam.id)])
        diagram.tag_lower(BeamShape.TAG, NodeShape.TAG)
        diagram.tag_lower(BeamShape.TAG, SupportShape.TAG)
        diagram.tag_lower(BeamShape.TAG, ForceShape.TAG)
        if (not self.TAG == Shape.TEMP) and diagram.settings.show_beam_labels.get(): 
            self.draw_label()

    def is_at(self, x: int, y: int) -> bool:
        beam = Line(Point(self.component.start_node.x, self.component.start_node.y), Point(self.component.end_node.x, self.component.end_node.y))
        return Point(x, y).distance(beam) < self.WIDTH/2

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        p1 = Point(self.component.start_node.x, self.component.start_node.y)
        p2 = Point(self.component.end_node.x, self.component.end_node.y)
        return Line(p1, p2).midpoint()

class TempBeamShape(BeamShape):

    TAG: str = Shape.TEMP
    COLOR: str = Shape.TEMP_COLOR


class SupportShape(Shape[Support]):

    TAG: str = "support"

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2
    LINE_SPACING: int = 5

    LABEL_OFFSET = 20

    def __init__(self, support: Support, diagram: 'TwlDiagram') -> None:
        super().__init__(support, diagram)
        triangle = self.triangle_coordinates
        self.tk_id = diagram.create_polygon(triangle.p1.x, 
                               triangle.p1.y, 
                               triangle.p2.x, 
                               triangle.p2.y, 
                               triangle.p3.x, 
                               triangle.p3.y, 
                               fill=self.BG_COLOR, 
                               outline=self.COLOR, 
                               width=self.BORDER, 
                               tags=[*self.TAGS, str(support.id)])
        if support.constraints == 1:
            line = self.line_coordinates
            diagram.create_line(line.start.x, 
                                line.start.y, 
                                line.end.x, 
                                line.end.y, 
                                fill=self.COLOR, 
                                width=self.BORDER, 
                                tags=[*self.TAGS, str(support.id)])
        diagram.tag_lower(SupportShape.TAG, NodeShape.TAG)
        if (not self.TAG == Shape.TEMP) and diagram.settings.show_support_labels.get(): 
            self.draw_label()

    def is_at(self, x: int, y: int) -> bool:
        return self.triangle_coordinates.inside_triangle(Point(x, y))

    @property
    def triangle_coordinates(self) -> Triangle:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT)
        triangle = Triangle(n_point, l_point, r_point)
        triangle.rotate(n_point, self.component.angle)
        return triangle

    @property
    def line_coordinates(self) -> Line:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT + self.LINE_SPACING)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT + self.LINE_SPACING)
        line = Line(l_point, r_point)
        line.rotate(n_point, self.component.angle)
        return line

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_BG_COLOR, "outline": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(self.component.node.x, self.component.node.y + self.HEIGHT + self.LABEL_OFFSET)
        point.rotate(n_point, self.component.angle)
        return point

    @property
    def label_text(self) -> str:
        return int_to_letter(self.component.id)

class TempSupportShape(SupportShape):

    TAG: str = Shape.TEMP
    COLOR = Shape.TEMP_COLOR


class ForceShape(Shape[Force]):

    TAG: str = "force"

    LENGTH = 40
    WIDTH = 6
    DISTANCE_FROM_NODE = 15
    ARROW_SHAPE = (15,14,10)

    LABEL_OFFSET = 20
    LABEL_PREFIX = "F"

    def __init__(self, force: Force, diagram: 'TwlDiagram') -> None:
        super().__init__(force, diagram)
        arrow: Line = self.arrow_coordinates
        self.tk_id = diagram.create_line(arrow.start.x, 
                            arrow.start.y, 
                            arrow.end.x, 
                            arrow.end.y, 
                            width=self.WIDTH, 
                            arrow=tk.FIRST, 
                            arrowshape=self.ARROW_SHAPE, 
                            fill=self.COLOR, 
                            tags=[*self.TAGS, str(force.id)])
        diagram.tag_lower(ForceShape.TAG, NodeShape.TAG)
        if (not self.TAG == Shape.TEMP) and diagram.settings.show_force_labels.get(): 
            self.draw_label()

    def is_at(self, x: int, y: int) -> bool:
        return Point(x, y).distance(self.arrow_coordinates) < self.WIDTH/2

    @property
    def arrow_coordinates(self) -> Line:
        n = Point(self.component.node.x, self.component.node.y)
        a1 = Point(n.x, n.y + self.DISTANCE_FROM_NODE)
        a2 = Point(a1.x, a1.y + self.LENGTH)
        a1.rotate(n, self.component.angle)
        a2.rotate(n, self.component.angle)
        return Line(a1, a2)

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(n_point.x - self.LABEL_OFFSET, n_point.y + self.DISTANCE_FROM_NODE + ((self.LENGTH + self.ARROW_SHAPE[0]) // 2))
        point.rotate(n_point, self.component.angle)
        return point

class TempForceShape(ForceShape):

    TAG: str = Shape.TEMP
    COLOR = Shape.TEMP_COLOR


class Tool:

    ID: int = -1
    NAME: str = "X"
    SYMBOL: str = "X"

    def __init__(self, diagram: 'TwlDiagram'):
        self.diagram: 'TwlDiagram' = diagram
        self.name = "TEST"

    @final
    def selected(self):
        """Perform tool change"""
        self.diagram.selected_tool.deactivate()
        self.activate()
        self.diagram.selected_tool = self

    def activate(self):
        self.diagram.bind("<Button-1>", self.action)
        self.diagram.bind("<Motion>", self.preview)
        self.diagram.bind("<Escape>", lambda *ignore: self.reset())
        self.diagram.bind("<Leave>", lambda *ignore: self.diagram.delete_with_tag(Shape.TEMP))

    def deactivate(self):
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<Motion>")
        self.diagram.unbind("<Escape>")
        self.diagram.unbind("<Leave>")
        self.reset()

    def reset(self):
        self.diagram.delete_with_tag(Shape.TEMP)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

    def preview(self, event):
        """Preview of the action when the user moves the mouse on the canvas while the tool is active"""
        pass

    def holding_shift_key(self, event) -> bool:
        return event.state & 0x1 #bitwise ANDing the event.state with the ShiftMask flag


class SelectTool(Tool):

    ID: int = 0
    NAME: str = 'Select'
    SYMBOL: str = '\u2d3d'

    def activate(self):
        super().activate()
        self.diagram.bind("<Delete>", self.delete_selected)

    def deactivate(self):
        super().deactivate()
        self.diagram.unbind("<Delete>")

    def reset(self):
        super().reset()
        [shape.deselect() for shape in self.diagram.selection.copy()]

    @property
    def selectable_shapes(self) -> list[Shape]:
        return list(filter(lambda s: isinstance(s.component, (Beam, Support, Force)), self.diagram.shapes))

    def action(self, event):
        self.diagram.focus_set()
        shape = self.diagram.find_shape_of_list_at(self.selectable_shapes, event.x, event.y)
        if self.holding_shift_key(event):
            if shape == None:
                print("not found")
            elif shape in self.diagram.selection:
                shape.deselect()
            else:
                shape.select()
        else:
            self.reset()
            if shape == None:
                print("not found")
            else:
                shape.select()

    def delete_selected(self, event):
        [shape.component.delete() for shape in self.diagram.selection]  
        self.reset()


class BeamTool(Tool):

    ID: int = 1
    NAME: str = 'Beam'
    SYMBOL: str = '\ua5ec'

    def __init__(self, editor):
        super().__init__(editor)
        self.start_node: Node | None = None

    def reset(self):
        super().reset()
        self.start_node = None

    def action(self, event):
        self.diagram.focus_set()
        clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
        if self.start_node is None:
            self.start_node = clicked_node if clicked_node else self.create_temp_node(event.x, event.y)
            return
        end_node = clicked_node if clicked_node else self.diagram.create_node(event.x, event.y)
        if not self.start_node in self.diagram.statical_system.nodes:
            self.start_node = self.diagram.create_node(self.start_node.x, self.start_node.y)
        self.diagram.create_beam(self.start_node, end_node)
        self.start_node = end_node

    def create_temp_node(self, x, y) -> Node:
        temp_node = Node(StaticalSystem(TwlUpdateManager()), x, y)
        TempNodeShape(temp_node, self.diagram)
        return temp_node

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        temp_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
        if not self.start_node:
            if not temp_node:
                temp_node = Node(StaticalSystem(TwlUpdateManager()), event.x, event.y)
                TempNodeShape(temp_node, self.diagram)
            return
        if not self.start_node in self.diagram.statical_system.nodes:
            TempNodeShape(self.start_node, self.diagram)
        if not temp_node:
            temp_node = Node(StaticalSystem(TwlUpdateManager()), event.x, event.y)
            TempNodeShape(temp_node, self.diagram)
        temp_beam = Beam(StaticalSystem(TwlUpdateManager()), self.start_node, temp_node)
        TempBeamShape(temp_beam, self.diagram)
        self.diagram.focus_set()


class SupportTool(Tool):

    ID: int = 2
    NAME: str = 'Support'
    SYMBOL: str = '\u29cb'

    def __init__(self, editor):
        super().__init__(editor)
        self.node: Node | None = None

    def reset(self):
        super().reset()
        self.node = None

    def action(self, event):
        self.diagram.focus_set()
        if not self.node:
            clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if clicked_node and not clicked_node.supports:
                self.node = clicked_node
        else:
            line = Line(Point(event.x, event.y), Point(self.node.x, self.node.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.diagram.create_support(self.node, angle)
            self.reset()

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node and not hovering_node.supports:
                TempSupportShape(Support(StaticalSystem(TwlUpdateManager()), hovering_node), self.diagram)
        else:
            line = Line(Point(event.x, event.y), Point(self.node.x, self.node.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            TempSupportShape(Support(StaticalSystem(TwlUpdateManager()), self.node, angle), self.diagram)
        self.diagram.focus_set()


class ForceTool(Tool):

    ID: int = 3
    NAME: str = 'Force'
    SYMBOL: str = '\u2b07'

    def __init__(self, editor):
        super().__init__(editor)
        self.node: Node | None = None

    def reset(self):
        super().reset()
        self.node = None

    def action(self, event):
        self.diagram.focus_set()
        if not self.node:
            clicked_node: Node | None = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if clicked_node:
                self.node = clicked_node
        else:
            line = Line(Point(event.x, event.y), Point(self.node.x, self.node.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.diagram.create_force(self.node, angle)
            self.reset()

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node:
                TempForceShape(Force(StaticalSystem(TwlUpdateManager()), hovering_node), self.diagram)
        else:
            line = Line(Point(event.x, event.y), Point(self.node.x, self.node.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            TempForceShape(Force(StaticalSystem(TwlUpdateManager()), self.node, angle), self.diagram)
        self.diagram.focus_set()


class TwlDiagram(tk.Canvas, TwlWidget):

    STAT_DETERM_LABEL_PADDING: int = 10
    TOOL_BUTTON_SIZE: int = 50

    def __init__(self, master, statical_system: StaticalSystem, settings: Settings):
        tk.Canvas.__init__(self, master)
        self.statical_system: StaticalSystem = statical_system
        self.settings: Settings = settings
        self.shapes: list[Shape] = []
        self.selection: list[Shape] = []
        
        #create toolbar
        self.tools = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool: Tool = self.tools[0]
        toolbar: ttk.Frame = ttk.Frame(master, style="Diagram.TFrame")
        toolbar.pack(fill="y", side= "left")
        ttk.Style().configure("Diagram.TFrame", background="lightgrey")

        for tool in self.tools: self.add_button(tool, toolbar)

        self.stat_determ_label = ttk.Label(self, style= "Diagram.TLabel", text=self.stat_determ_text)
        self.stat_determ_label.place(x=TwlDiagram.STAT_DETERM_LABEL_PADDING, y=TwlDiagram.STAT_DETERM_LABEL_PADDING)
        ttk.Style().configure("Diagram.TLabel", foreground="green")

    def add_button(self, tool: Tool, master: ttk.Frame) -> ttk.Radiobutton:
        frame = tk.Frame(master, width=TwlDiagram.TOOL_BUTTON_SIZE, height=TwlDiagram.TOOL_BUTTON_SIZE) #their units in pixels
        frame.grid_propagate(False) #disables resizing of frame
        frame.columnconfigure(0, weight=1) #enables button to fill frame
        frame.rowconfigure(0, weight=1) #any positive number would do the trick
        frame.grid(row=tool.ID, column=0) #put frame where the button should be

        button = ttk.Radiobutton(frame, text=tool.SYMBOL, variable=cast(tk.Variable, self.selected_tool), value=tool, command=tool.selected, style="Diagram.Toolbutton")
        button.grid(sticky="nsew") #makes the button expand
        ttk.Style().configure('Diagram.Toolbutton', font=('Helvetica', 14))
    
        return button

    def change_tool(self):
        """Code to be executed when the tool is changed"""

    def update(self) -> None:
        """Redraws the diagram completely from the statical system"""
        self.delete("all")
        self.shapes.clear()

        for node in self.statical_system.nodes: self.shapes.append(NodeShape(node, self))
        for beam in self.statical_system.beams: self.shapes.append(BeamShape(beam, self))
        for support in self.statical_system.supports: self.shapes.append(SupportShape(support, self))
        for force in self.statical_system.forces: self.shapes.append(ForceShape(force, self))

        self.stat_determ_label.configure(text=self.stat_determ_text)
        color = "green" if self.stat_determ_text[:5] == "f = 0" else "red"
        ttk.Style().configure("Diagram.TLabel", foreground=color)

        self.selected_tool.activate()

    @property
    def stat_determ_text(self) -> str:
        nodes = len(self.statical_system.nodes)
        equations = 2 * nodes
        constraints = sum(support.constraints for support in self.statical_system.supports)
        beams = len(self.statical_system.beams)
        unknowns = constraints + beams
        f = equations - unknowns
        return f"f = {f}, the system ist statically {"" if f == 0 else "in"}determinate.\n{equations} equations (2 * {nodes} nodes)\n{unknowns} unknowns ({constraints} for supports, {beams} for beams)"

    def create_node(self, x: int, y: int) -> Node:
        self.statical_system.update_manager.pause()
        node = Node(self.statical_system, x, y)
        self.statical_system.nodes.append(node)
        self.statical_system.update_manager.resume()
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        self.statical_system.update_manager.pause()
        beam = Beam(self.statical_system, start_node, end_node)
        self.statical_system.beams.append(beam)
        self.statical_system.update_manager.resume()
        return beam

    def create_support(self, node: Node, angle: float=0):
        self.statical_system.update_manager.pause()
        support = Support(self.statical_system, node, angle)
        self.statical_system.supports.append(support)
        self.statical_system.update_manager.resume()
        return support

    def create_force(self, node: Node, angle: float=180):
        self.statical_system.update_manager.pause()
        force = Force(self.statical_system, node, angle)
        self.statical_system.forces.append(force)
        self.statical_system.update_manager.resume()
        return force

    def find_shape_at(self, x: int, y: int) -> Shape | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: shape.is_at(x, y), self.shapes), None)

    def find_shape_of_list_at(self, shapes: list[Shape], x: int, y: int) -> Shape | None:
        return next(filter(lambda shape: shape.is_at(x, y), shapes), None)

    def find_shape_of_type_at(self, component_type: Type[C], x: int, y: int) -> Shape[C] | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: isinstance(shape.component, component_type) and shape.is_at(x, y), self.shapes), None)

    def find_component_of_type_at(self, component_type: Type[C], x: int, y: int) -> C | None:
        shape = self.find_shape_of_type_at(component_type, x, y)
        return shape.component if shape else None

    def shape_for(self, component: C) -> Shape[C]:
        return next(filter(lambda shape: shape.component == component, self.shapes))

    def find_withtag(self, tagOrId: str | int) -> tuple[int, ...]:
        return tuple(filter(lambda id: (id == tagOrId) or (tagOrId in self.gettags(id)), self.find_all()))

    def tag_lower(self, lower: str | int, upper: str | int | None = None) -> None:
        if self.find_withtag(lower) and (not upper or self.find_withtag(upper)):
            super().tag_lower(lower, upper)

    def delete_with_tag(self, tag: str):
        [self.delete(shape) for shape in self.find_withtag("temp")]