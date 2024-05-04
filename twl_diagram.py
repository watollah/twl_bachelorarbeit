import tkinter as tk
from tkinter import ttk
from typing import final, TypeVar, Generic

from twl_components import Node
from twl_widget import *
from twl_components import *


C = TypeVar('C', bound=Component)


class Shape(Generic[C]):
    """Represents the shape of a component in the TwlDiagram."""

    FILL_COLOR: str = "pink"
    SELECTED_FILL_COLOR: str = "pink"
    BORDER_COLOR: str = "pink"
    SELECTED_BORDER_COLOR: str = "pink"

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


class NodeShape(Shape[Node]):

    FILL_COLOR: str = "white"
    SELECTED_FILL_COLOR: str = "white"
    BORDER_COLOR: str = "black"
    SELECTED_BORDER_COLOR: str = "red"

    RADIUS: int = 6
    BORDER: int = 2

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


class BeamShape(Shape[Beam]):

    FILL_COLOR: str = "black"
    SELECTED_FILL_COLOR: str = "red"

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


class SupportShape(Shape[Support]):

    FILL_COLOR: str = "white"
    SELECTED_FILL_COLOR: str = "white"
    BORDER_COLOR: str = "black"
    SELECTED_BORDER_COLOR: str = "red"

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2

    def __init__(self, support: Support, diagram: 'TwlDiagram') -> None:
        super().__init__(support, diagram)
        self.tk_id = diagram.create_polygon(support.node.x, 
                               support.node.y, 
                               support.node.x - SupportShape.WIDTH / 2, 
                               support.node.y + SupportShape.HEIGHT, 
                               support.node.x + SupportShape.WIDTH / 2, 
                               support.node.y + SupportShape.HEIGHT, 
                               fill=SupportShape.FILL_COLOR, 
                               outline=SupportShape.BORDER_COLOR, 
                               width=SupportShape.BORDER, 
                               tags=(Support.TAG, str(support.id)))
        diagram.tag_lower(Support.TAG, Node.TAG)

    def is_at(self, x: int, y: int) -> bool:
        return self.triangle_coordinates().inside_triangle(Point(x, y))

    def triangle_coordinates(self) -> Triangle:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT)
        triangle = Triangle(n_point, l_point, r_point)
        triangle.rotate(n_point, self.component.angle)
        return triangle

    @property
    def default_style(self) -> dict[str, str]:
        return {"fill": self.FILL_COLOR, "outline": self.BORDER_COLOR}

    @property
    def selected_style(self) -> dict[str, str]:
        return {"fill": self.SELECTED_FILL_COLOR, "outline": self.SELECTED_BORDER_COLOR}


class ForceShape(Shape[Force]):

    FILL_COLOR: str = "black"
    SELECTED_FILL_COLOR: str = "red"

    LENGTH = 40
    WIDTH = 6
    DISTANCE_FROM_NODE = 10
    ARROW_SHAPE = (15,14,10)

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

    def __init__(self, master, statical_system):
        tk.Canvas.__init__(self, master)
        self.statical_system: StaticalSystem = statical_system
        self.shapes: list[Shape] = []
        self.selection: list[Shape] = []
        
        #create toolbar
        self.tools = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self.selected_tool: Tool = self.tools[0]

        toolbar = tk.Frame(self)
        toolbar.place(relx=0, rely=0, anchor=tk.NW)
        for tool in self.tools:
            rb = ttk.Radiobutton(toolbar, text=tool.SYMBOL, variable=cast(tk.Variable, self.selected_tool), value=tool, command=tool.selected, style='Toolbutton')
            rb.grid(row=0, column=tool.ID)
        ttk.Style().configure('Toolbutton', font=('Helvetica', 14), padding = (10, 10), width = 2) #todo: improve sizing with grid

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

        self.selected_tool.activate()

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