import tkinter as tk

from c2d_app import TwlApp
from c2d_math import Point, Line, Triangle, Polygon
from c2d_components import AngleAttribute, ConstraintsAttribute, EndNodeAttribute, Node, Beam, NodeAttribute, StartNodeAttribute, Support, Force, XCoordinateAttribute, YCoordinateAttribute
from c2d_diagram import Shape, ComponentShape, TwlDiagram


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

    def is_at(self, x: float, y: float) -> bool:
        return True if abs(self.component.x - x) <= self.RADIUS and abs(self.component.y - y) <= self.RADIUS else False

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.BG_COLOR, "outline": self.COLOR}

    @property
    def label_position(self) -> Point:
        return Point(self.component.x + self.LABEL_OFFSET, self.component.y - self.LABEL_OFFSET)

    @property
    def bounds(self) -> Polygon:
        return Polygon(Point(self.component.x, self.component.y))

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.oval_id, width=self.BORDER * factor)

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        if component_id == self.component.id and attribute_id in (XCoordinateAttribute.ID, YCoordinateAttribute.ID):
            p1, p2 = self.circle_coords()
            self.tk_shapes[self.oval_id] = Polygon(p1, p2)
            self.update_label_pos()
            for beam in self.component.beams:
                beam_shape = self.diagram.shapes_of_type_for(BeamShape, beam)[0]
                beam_shape.update_observer(beam.id, StartNodeAttribute.ID if beam.start_node == self.component else EndNodeAttribute.ID)
            for support in self.component.supports:
                support_shape = self.diagram.shapes_of_type_for(SupportShape, support)[0]
                support_shape.update_observer(support.id, NodeAttribute.ID)
            for force in self.component.forces:
                force_shape = self.diagram.shapes_of_type_for(ForceShape, force)[0]
                force_shape.update_observer(force.id, NodeAttribute.ID)
            self.diagram.refresh()
        super().update_observer(component_id, attribute_id)


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

    def is_at(self, x: float, y: float) -> bool:
        return Point(x, y).distance_to_line(self.line_coords()) < self.WIDTH/2

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.COLOR}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR}

    @property
    def label_position(self) -> Point:
        return self.line_coords().midpoint()

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.line_id, width=self.WIDTH * factor)

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        if component_id == self.component.id and attribute_id in (StartNodeAttribute.ID, EndNodeAttribute.ID):
            line = self.line_coords()
            self.tk_shapes[self.line_id] = Polygon(line.start, line.end)
            self.update_label_pos()
            self.diagram.refresh()
        super().update_observer(component_id, attribute_id)


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
        triangle = self.triangle_coords
        self.triangle_tk_id = diagram.create_polygon(triangle.p1.x, 
                               triangle.p1.y, 
                               triangle.p2.x, 
                               triangle.p2.y, 
                               triangle.p3.x, 
                               triangle.p3.y, 
                               fill=self.BG_COLOR, 
                               outline=self.COLOR, 
                               width=self.BORDER, 
                               tags=[*self.TAGS, str(support.id)])
        self.tk_shapes[self.triangle_tk_id] = Polygon(triangle.p1, triangle.p2, triangle.p3)
        line = self.line_coords
        self.line_tk_id = diagram.create_line(line.start.x, 
                            line.start.y, 
                            line.end.x, 
                            line.end.y, 
                            fill=self.COLOR, 
                            width=self.BORDER, 
                            tags=[*self.TAGS, str(support.id), self.LINE_TAG])
        self.tk_shapes[self.line_tk_id] = Polygon(line.start, line.end)
        self.update_line_visibility()
        diagram.tag_lower(SupportShape.TAG, NodeShape.TAG)

    def is_at(self, x: float, y: float) -> bool:
        return self.triangle_coords.inside_triangle(Point(x, y))

    @property
    def triangle_coords(self) -> Triangle:
        n_point = Point(self.component.node.x, self.component.node.y)
        l_point = Point(int(n_point.x - self.WIDTH / 2), n_point.y + self.HEIGHT)
        r_point = Point(int(n_point.x + self.WIDTH / 2), n_point.y + self.HEIGHT)
        triangle = Triangle(n_point, l_point, r_point)
        triangle.rotate(n_point, self.component.angle + 180)
        return triangle

    @property
    def line_coords(self) -> Line:
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

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.triangle_tk_id, width=self.BORDER * factor)
        self.diagram.itemconfig(self.line_tk_id, width=self.BORDER * factor)

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        if component_id == self.component.id:
            if attribute_id in (NodeAttribute.ID, AngleAttribute.ID):
                triangle = self.triangle_coords
                self.tk_shapes[self.triangle_tk_id] = Polygon(triangle.p1, triangle.p2, triangle.p3)
                line = self.line_coords
                self.tk_shapes[self.line_tk_id] = Polygon(line.start, line.end)
                self.update_label_pos()
                self.diagram.refresh()
            elif attribute_id == ConstraintsAttribute.ID:
                self.update_line_visibility()
                self.diagram.refresh()
        super().update_observer(component_id, attribute_id)

    def update_line_visibility(self):
        line_visibility = tk.NORMAL if self.component.constraints == 1 else tk.HIDDEN
        self.diagram.itemconfig(self.line_tk_id, state=line_visibility)


class ForceShape(ComponentShape[Force]):

    TAG: str = "force"

    LENGTH = 40
    WIDTH = 6
    DISTANCE_FROM_NODE = 15
    ARROW_SHAPE = (15,14,10)

    LABEL_OFFSET = 20

    def __init__(self, force: Force, diagram: 'ModelDiagram') -> None:
        super().__init__(force, diagram)
        arrow = self.arrow_coords
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

    def is_at(self, x: float, y: float) -> bool:
        return Point(x, y).distance_to_line(self.arrow_coords) < self.WIDTH/2

    @property
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
        point = Point(n_point.x + self.LABEL_OFFSET, n_point.y - self.DISTANCE_FROM_NODE - ((self.LENGTH + self.ARROW_SHAPE[0]) / 2))
        point.rotate(n_point, self.component.angle)
        return point

    def scale(self, factor: float):
        super().scale(factor)
        scaled_arrow = tuple(value * factor for value in self.ARROW_SHAPE)
        self.diagram.itemconfig(self.arrow_id, width=self.WIDTH * factor, arrowshape=scaled_arrow)

    def update_observer(self, component_id: str="", attribute_id: str=""):
        if component_id == self.component.id and attribute_id in (NodeAttribute.ID, AngleAttribute.ID):
            arrow = self.arrow_coords
            self.tk_shapes[self.arrow_id] = Polygon(arrow.start, arrow.end)
            self.update_label_pos()
            self.diagram.refresh()
        super().update_observer(component_id, attribute_id)


class ModelDiagram(TwlDiagram):

    def __init__(self, master):
        super().__init__(master)
        TwlApp.settings().show_node_labels.trace_add("write", lambda *ignore: self.refresh())
        TwlApp.settings().show_beam_labels.trace_add("write", lambda *ignore: self.refresh())
        TwlApp.settings().show_support_labels.trace_add("write", lambda *ignore: self.refresh())
        TwlApp.settings().show_force_labels.trace_add("write", lambda *ignore: self.refresh())

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Updates the diagram whenever a component is added to or removed from the model."""
        model_components = TwlApp.model().all_components
        [shape.remove() for shape in self.component_shapes if not shape.component in model_components]

        [self.shapes.append(NodeShape(node, self)) for node in TwlApp.model().nodes if not self.shapes_of_type_for(NodeShape, node)]
        [self.shapes.append(BeamShape(beam, self)) for beam in TwlApp.model().beams if not self.shapes_of_type_for(BeamShape, beam)]
        [self.shapes.append(SupportShape(support, self)) for support in TwlApp.model().supports if not self.shapes_of_type_for(SupportShape, support)]
        [self.shapes.append(ForceShape(force, self)) for force in TwlApp.model().forces if not self.shapes_of_type_for(ForceShape, force)]

        self.tag_raise(NodeShape.TAG)
        self.tag_raise(ComponentShape.LABEL_BG_TAG)
        self.tag_raise(ComponentShape.LABEL_TAG)

        super().update_observer(component_id, attribute_id)

    def label_visible(self, shape: Shape) -> bool:
        visible: dict[type[Shape], bool] = {
            NodeShape: TwlApp.settings().show_node_labels.get(),
            BeamShape: TwlApp.settings().show_beam_labels.get(),
            SupportShape: TwlApp.settings().show_support_labels.get(),
            ForceShape: TwlApp.settings().show_force_labels.get()
        }
        return visible.get(type(shape), True)