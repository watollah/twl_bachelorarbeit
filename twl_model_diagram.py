import tkinter as tk

from twl_app import TwlApp
from twl_math import Point, Line, Triangle, Polygon
from twl_components import Node, Beam, Support, Force
from twl_diagram import ComponentShape, TwlDiagram


class NodeShape(ComponentShape[Node]):

    TAG: str = "node"

    RADIUS: int = 6
    BORDER: int = 2

    LABEL_OFFSET = 15

    def __init__(self, node: Node, diagram: 'ModelDiagram') -> None:
        super().__init__(node, diagram)
        p1, p2 = self.circle_coords()
        self.oval_id = diagram.create_oval(p1.x, p1.y, p2.x, p2.y, 
                            fill=self.BG_COLOR, 
                            outline=self.COLOR, 
                            width = self.BORDER, 
                            tags=[*self.TAGS, str(node.id)])
        self.tk_shapes[self.oval_id] = Polygon(p1, p2)

    def circle_coords(self) -> tuple[Point, Point]:
        return Point(self.component.x - self.RADIUS, self.component.y - self.RADIUS), Point(self.component.x + self.RADIUS, self.component.y + self.RADIUS)

    def is_at(self, x: int, y: int) -> bool:
        return True if abs(self.component.x - x) <= self.RADIUS and abs(self.component.y - y) <= self.RADIUS else False

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    @property
    def label_position(self) -> Point:
        return Point(self.component.x + self.LABEL_OFFSET, self.component.y - self.LABEL_OFFSET)

    def label_visible(self) -> bool:
        return TwlApp.settings().show_node_labels.get()

    @property
    def bounds(self) -> Polygon:
        return Polygon(Point(self.component.x, self.component.y))

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.oval_id, width=self.BORDER * factor)

class BeamShape(ComponentShape[Beam]):

    TAG: str = "beam"
    WIDTH: int = 4

    def __init__(self, beam: Beam, diagram: 'ModelDiagram') -> None:
        super().__init__(beam, diagram)
        line = self.line_coords()
        self.line_id = diagram.create_line(line.start.x, line.start.y,
                            line.end.x, line.end.y,
                            fill=self.COLOR,
                            width=self.WIDTH,
                            tags=[*self.TAGS, str(beam.id)])
        self.tk_shapes[self.line_id] = Polygon(line.start, line.end)
        diagram.tag_lower(BeamShape.TAG, NodeShape.TAG)
        diagram.tag_lower(BeamShape.TAG, SupportShape.TAG)
        diagram.tag_lower(BeamShape.TAG, ForceShape.TAG)

    def line_coords(self) -> Line:
        return Line(Point(self.component.start_node.x, self.component.start_node.y), Point(self.component.end_node.x, self.component.end_node.y))

    def is_at(self, x: int, y: int) -> bool:
        return Point(x, y).distance_to_line(self.line_coords()) < self.WIDTH/2

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        return self.line_coords().midpoint()

    def label_visible(self) -> bool:
        return TwlApp.settings().show_beam_labels.get()

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.line_id, width=self.WIDTH * factor)


class SupportShape(ComponentShape[Support]):

    TAG: str = "support"

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2

    LINE_TAG: str = "support_line"
    LINE_SPACING: int = 5

    LABEL_OFFSET = 20

    def __init__(self, support: Support, diagram: 'ModelDiagram') -> None:
        super().__init__(support, diagram)
        triangle = self.triangle_coords()
        self.triangle_id = diagram.create_polygon(triangle.p1.x, 
                               triangle.p1.y, 
                               triangle.p2.x, 
                               triangle.p2.y, 
                               triangle.p3.x, 
                               triangle.p3.y, 
                               fill=self.BG_COLOR, 
                               outline=self.COLOR, 
                               width=self.BORDER, 
                               tags=[*self.TAGS, str(support.id)])
        self.tk_shapes[self.triangle_id] = Polygon(triangle.p1, triangle.p2, triangle.p3)
        if support.constraints == 1:
            line = self.line_coordinates
            self.line_id = diagram.create_line(line.start.x, 
                                line.start.y, 
                                line.end.x, 
                                line.end.y, 
                                fill=self.COLOR, 
                                width=self.BORDER, 
                                tags=[*self.TAGS, str(support.id), self.LINE_TAG])
            self.tk_shapes[self.line_id] = Polygon(line.start, line.end)
        diagram.tag_lower(SupportShape.TAG, NodeShape.TAG)

    def is_at(self, x: int, y: int) -> bool:
        return self.triangle_coords().inside_triangle(Point(x, y))

    def triangle_coords(self) -> Triangle:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT)
        triangle = Triangle(n_point, l_point, r_point)
        triangle.rotate(n_point, self.component.angle + 180)
        return triangle

    @property
    def line_coordinates(self) -> Line:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT + self.LINE_SPACING)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT + self.LINE_SPACING)
        line = Line(l_point, r_point)
        line.rotate(n_point, self.component.angle + 180)
        return line

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.COLOR} if self.LINE_TAG in tags else {"fill": self.BG_COLOR, "outline": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR} if self.LINE_TAG in tags else {"fill": self.SELECTED_BG_COLOR, "outline": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(self.component.node.x, self.component.node.y + self.HEIGHT + self.LABEL_OFFSET)
        point.rotate(n_point, self.component.angle + 180)
        return point

    def label_visible(self) -> bool:
        return TwlApp.settings().show_support_labels.get()

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.triangle_id, width=self.BORDER * factor)
        if self.component.constraints == 1:
            self.diagram.itemconfig(self.line_id, width=self.BORDER * factor)


class ForceShape(ComponentShape[Force]):

    TAG: str = "force"

    LENGTH = 40
    WIDTH = 6
    DISTANCE_FROM_NODE = 15
    ARROW_SHAPE = (15,14,10)

    LABEL_OFFSET = 20

    def __init__(self, force: Force, diagram: 'ModelDiagram') -> None:
        super().__init__(force, diagram)
        arrow = self.arrow_coords()
        self.arrow_id = diagram.create_line(arrow.start.x, 
                            arrow.start.y, 
                            arrow.end.x, 
                            arrow.end.y, 
                            width=self.WIDTH, 
                            arrow=tk.FIRST, 
                            arrowshape=self.ARROW_SHAPE, 
                            fill=self.COLOR, 
                            tags=[*self.TAGS, str(force.id)])
        self.tk_shapes[self.arrow_id] = Polygon(arrow.start, arrow.end)

    def is_at(self, x: int, y: int) -> bool:
        return Point(x, y).distance_to_line(self.arrow_coords()) < self.WIDTH/2

    def arrow_coords(self) -> Line:
        n = Point(self.component.node.x, self.component.node.y)
        a1 = Point(n.x, n.y - self.DISTANCE_FROM_NODE)
        a2 = Point(a1.x, a1.y - self.LENGTH)
        line = Line(a1, a2)
        line.rotate(n, self.component.angle)
        return line

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        n_point = Point(self.component.node.x, self.component.node.y)
        point = Point(n_point.x + self.LABEL_OFFSET, n_point.y - self.DISTANCE_FROM_NODE - ((self.LENGTH + self.ARROW_SHAPE[0]) // 2))
        point.rotate(n_point, self.component.angle)
        return point

    def label_visible(self) -> bool:
        return TwlApp.settings().show_force_labels.get()

    def scale(self, factor: float):
        super().scale(factor)
        scaled_arrow = tuple(value * factor for value in self.ARROW_SHAPE)
        self.diagram.itemconfig(self.arrow_id, width=self.WIDTH * factor, arrowshape=scaled_arrow)


class ModelDiagram(TwlDiagram):

    def __init__(self, master):
        super().__init__(master)

    def update(self) -> None:
        super().update()
        self.clear()

        for node in TwlApp.model().nodes: self.shapes.append(NodeShape(node, self))
        for beam in TwlApp.model().beams: self.shapes.append(BeamShape(beam, self))
        for support in TwlApp.model().supports: self.shapes.append(SupportShape(support, self))
        for force in TwlApp.model().forces: self.shapes.append(ForceShape(force, self))

        self.tag_raise(NodeShape.TAG)
        self.tag_raise(ComponentShape.LABEL_BG_TAG)
        self.tag_raise(ComponentShape.LABEL_TAG)

        self.refresh()

    def create_node(self, x: int, y: int) -> Node:
        """Creates a new node in the model."""
        TwlApp.update_manager().pause()
        node = Node(TwlApp.model(), x, y)
        TwlApp.model().nodes.append(node)
        TwlApp.update_manager().resume()
        return node

    def create_beam(self, start_node: Node, end_node: Node) -> Beam:
        """Creates a new beam in the model."""
        TwlApp.update_manager().pause()
        beam = Beam(TwlApp.model(), start_node, end_node)
        TwlApp.model().beams.append(beam)
        TwlApp.update_manager().resume()
        return beam

    def create_support(self, node: Node, angle: float=0):
        """Creates a new support in the model."""
        TwlApp.update_manager().pause()
        support = Support(TwlApp.model(), node, angle)
        TwlApp.model().supports.append(support)
        TwlApp.update_manager().resume()
        return support

    def create_force(self, node: Node, angle: float=180):
        """Creates a new force in the model."""
        TwlApp.update_manager().pause()
        force = Force(TwlApp.model(), node, angle)
        TwlApp.model().forces.append(force)
        TwlApp.update_manager().resume()
        return force