import tkinter as tk
from typing import final, TypeVar, Generic
from tkinter import ttk

from twl_widget import *
from twl_components import *
from twl_help import *


C = TypeVar('C', bound=Component)


class Shape(Generic[C]):
    """Represents the shape of a component in the TwlDiagram."""

    SELECTION_COLOR = "#0078D7"

    FILL_COLOR: str = "pink"
    SELECTED_FILL_COLOR: str = "pink"
    BORDER_COLOR: str = "pink"
    SELECTED_BORDER_COLOR: str = "pink"

    LABEL_TAG = "label"
    LABEL_BG_TAG = "label_background"
    LABEL_PREFIX = ""
    LABEL_SIZE = 12

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

    FILL_COLOR: str = "white"
    SELECTED_FILL_COLOR: str = "white"
    BORDER_COLOR: str = "black"
    SELECTED_BORDER_COLOR: str = Shape.SELECTION_COLOR

    RADIUS: int = 6
    BORDER: int = 2

    LABEL_OFFSET = 15

    def __init__(self, node: Node, diagram: 'TwlDiagram') -> None:
        super().__init__(node, diagram)
        self.tk_id = diagram.create_oval(node.x - NodeShape.RADIUS, 
                            node.y - NodeShape.RADIUS, 
                            node.x + NodeShape.RADIUS, 
                            node.y + NodeShape.RADIUS, 
                            fill=NodeShape.FILL_COLOR, 
                            outline=NodeShape.BORDER_COLOR, 
                            width = NodeShape.BORDER, 
                            tags=(Node.TAG, str(node.id)))

    def is_at(self, x: int, y: int) -> bool:
        return True if abs(self.component.x - x) <= self.RADIUS and abs(self.component.y - y) <= self.RADIUS else False

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.FILL_COLOR, "outline": self.BORDER_COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_FILL_COLOR, "outline": self.SELECTED_BORDER_COLOR}

    @property
    def label_position(self) -> Point:
        return Point(self.component.x + self.LABEL_OFFSET, self.component.y - self.LABEL_OFFSET)

    @property
    def label_text(self) -> str:
        return f"{self.LABEL_PREFIX}{int_to_roman(self.component.id)}"

class BeamShape(Shape[Beam]):

    FILL_COLOR: str = "black"
    SELECTED_FILL_COLOR: str = Shape.SELECTION_COLOR

    WIDTH: int = 4

    def __init__(self, beam: Beam, diagram: 'TwlDiagram') -> None:
        super().__init__(beam, diagram)
        self.tk_id = diagram.create_line(beam.start_node.x,
                            beam.start_node.y,
                            beam.end_node.x,
                            beam.end_node.y,
                            fill=BeamShape.FILL_COLOR,
                            width=BeamShape.WIDTH,
                            tags=(Beam.TAG, str(beam.id)))
        diagram.tag_lower(Beam.TAG, Node.TAG)

    def is_at(self, x: int, y: int) -> bool:
        beam = Line(Point(self.component.start_node.x, self.component.start_node.y), Point(self.component.end_node.x, self.component.end_node.y))
        return Point(x, y).distance(beam) < self.WIDTH/2

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.FILL_COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_FILL_COLOR}

    @property
    def label_position(self) -> Point:
        p1 = Point(self.component.start_node.x, self.component.start_node.y)
        p2 = Point(self.component.end_node.x, self.component.end_node.y)
        return Line(p1, p2).midpoint()


class SupportShape(Shape[Support]):

    FILL_COLOR: str = "white"
    SELECTED_FILL_COLOR: str = "white"
    BORDER_COLOR: str = "black"
    SELECTED_BORDER_COLOR: str = Shape.SELECTION_COLOR

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
                               fill=SupportShape.FILL_COLOR, 
                               outline=SupportShape.BORDER_COLOR, 
                               width=SupportShape.BORDER, 
                               tags=(Support.TAG, str(support.id)))
        if support.constraints == 1:
            line = self.line_coordinates
            diagram.create_line(line.start.x, 
                                line.start.y, 
                                line.end.x, 
                                line.end.y, 
                                fill=SupportShape.BORDER_COLOR, 
                                width=SupportShape.BORDER, 
                                tags=(Support.TAG, str(support.id)))
        diagram.tag_lower(Support.TAG, Node.TAG)

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
        return {"fill": self.FILL_COLOR, "outline": self.BORDER_COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_FILL_COLOR, "outline": self.SELECTED_BORDER_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(self.component.node.x, self.component.node.y + self.HEIGHT + self.LABEL_OFFSET)
        point.rotate(n_point, self.component.angle)
        return point

    @property
    def label_text(self) -> str:
        return int_to_letter(self.component.id)


class ForceShape(Shape[Force]):

    FILL_COLOR: str = "black"
    SELECTED_FILL_COLOR: str = Shape.SELECTION_COLOR

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
                            width=ForceShape.WIDTH, 
                            arrow=tk.FIRST, 
                            arrowshape=ForceShape.ARROW_SHAPE, 
                            fill=ForceShape.FILL_COLOR, 
                            tags=(Force.TAG, str(force.id)))
        diagram.tag_lower(Force.TAG, Node.TAG)

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
        return {"fill": self.FILL_COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_FILL_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(n_point.x - self.LABEL_OFFSET, n_point.y + self.DISTANCE_FROM_NODE + ((self.LENGTH + self.ARROW_SHAPE[0]) // 2))
        point.rotate(n_point, self.component.angle)
        return point


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
        """Code to be executed when the tool is selected"""
        print('now selected: ', self.ID)
    
    def deactivate(self):
        """Code to be executed when the tool is deselected"""
        print('now deselected: ', self.NAME)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass


class SelectTool(Tool):

    ID: int = 0
    NAME: str = 'Select'
    SYMBOL: str = '\u2d3d'

    def activate(self):
        self.diagram.bind("<Button-1>", self.handle_selection)
        self.diagram.bind("<Shift-Button-1>", self.handle_shift_selection)
        self.diagram.bind("<Delete>", self.delete_selected_components)

    def deactivate(self):
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<Shift-Button-1>")
        self.diagram.unbind("<Delete>")

    @property
    def selectable_shapes(self) -> list[Shape]:
        return list(filter(lambda s: isinstance(s.component, (Beam, Support, Force)), self.diagram.shapes))

    def clear_selection(self):
        [shape.deselect() for shape in self.diagram.selection]

    def handle_selection(self, event):
        self.diagram.focus_set()
        self.clear_selection()
        shape = self.diagram.find_shape_of_list_at(self.selectable_shapes, event.x, event.y)
        if shape == None:
            print("not found")
            return
        shape.select()

    def handle_shift_selection(self, event):
        shape = self.diagram.find_shape_of_list_at(self.selectable_shapes, event.x, event.y)
        if shape == None:
            print("not found")
            return
        elif shape in self.diagram.selection:
            shape.deselect()
            return
        shape.select()

    def delete_selected_components(self, event):
        [shape.component.delete() for shape in self.diagram.selection]  
        self.clear_selection()


class BeamTool(Tool):

    ID: int = 1
    NAME: str = 'Beam'
    SYMBOL: str = '\ua5ec'

    def __init__(self, editor):
        super().__init__(editor)
        self.start_node: Node | None = None

    def activate(self):
        self.diagram.bind("<Button-1>", self.action)

    def deactivate(self):
        self.diagram.unbind("<Button-1>")

    def action(self, event):
        clicked_node_shape: Shape[Node] | None = self.diagram.find_shape_of_type_at(Node, event.x, event.y)

        if clicked_node_shape:
            if self.start_node is None:
                self.start_node = clicked_node_shape.component
            else:
                self.diagram.create_beam(self.start_node, clicked_node_shape.component)
                self.start_node = None
        else:
            if self.start_node is None:
                self.start_node = self.diagram.create_node(event.x, event.y)
            else:
                end_node = self.diagram.create_node(event.x, event.y)
                self.diagram.create_beam(self.start_node, end_node)
                self.start_node = None


class SupportTool(Tool):

    ID: int = 2
    NAME: str = 'Support'
    SYMBOL: str = '\u29cb'

    def activate(self):
        for id in self.diagram.find_withtag("node"): self.diagram.tag_bind(id, "<Button-1>", self.action)
    
    def deactivate(self):
        for id in self.diagram.find_withtag("node"): self.diagram.tag_unbind(id, "<Button-1>")

    def action(self, event):
        clicked_node_shape: Shape[Node] | None = self.diagram.find_shape_of_type_at(Node, event.x, event.y)
        if clicked_node_shape:
            node: Node = clicked_node_shape.component
            if not node.supports:
                self.diagram.create_support(node)
                print(f"Created support on Node {node.id}")


class ForceTool(Tool):

    ID: int = 3
    NAME: str = 'Force'
    SYMBOL: str = '\u2b07'

    def activate(self):
        for id in self.diagram.find_withtag("node"): self.diagram.tag_bind(id, "<Button-1>", self.action)
    
    def deactivate(self):
        for id in self.diagram.find_withtag("node"): self.diagram.tag_unbind(id, "<Button-1>")

    def action(self, event):
        clicked_node_shape: Shape[Node] | None = self.diagram.find_shape_of_type_at(Node, event.x, event.y)
        if clicked_node_shape:
            node: Node = clicked_node_shape.component
            if not node.forces:
                self.diagram.create_force(node)
                print(f"Created force on Node {node.id}")


class TwlDiagram(tk.Canvas, TwlWidget):

    STAT_DETERM_LABEL_PADDING: int = 10
    TOOL_BUTTON_SIZE: int = 50

    def __init__(self, master, statical_system):
        tk.Canvas.__init__(self, master)
        self.statical_system: StaticalSystem = statical_system
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

        for shape in self.shapes: shape.draw_label()

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
        node = Node(self.statical_system, x, y)
        self.statical_system.nodes.append(node)
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        beam = Beam(self.statical_system, start_node, end_node)
        self.statical_system.beams.append(beam)
        return beam

    def create_support(self, node: Node):
        support = Support(self.statical_system, node)
        self.statical_system.supports.append(support)
        return support

    def create_force(self, node: Node):
        force = Force(self.statical_system, node)
        self.statical_system.forces.append(force)
        return force

    def find_shape_at(self, x: int, y: int) -> Shape | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: shape.is_at(x, y), self.shapes), None)

    def find_shape_of_list_at(self, shapes: list[Shape], x: int, y: int) -> Shape | None:
        return next(filter(lambda shape: shape.is_at(x, y), shapes), None)

    def find_shape_of_type_at(self, component_type: Type[C], x: int, y: int) -> Shape[C] | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: isinstance(shape.component, component_type) and shape.is_at(x, y), self.shapes), None)

    def shape_for(self, component: C) -> Shape[C]:
        return next(filter(lambda shape: shape.component == component, self.shapes))