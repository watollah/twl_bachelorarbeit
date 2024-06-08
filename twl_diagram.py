import tkinter as tk
from tkinter import ttk
from typing import cast, final, TypeVar, Generic

from twl_app import *
from twl_update import *
from twl_components import *
from twl_help import *
from twl_settings import *
from twl_images import *
from twl_style import *
from twl_widgets import *


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

    def __init__(self, component: C, diagram: 'TwlDiagram') -> None: #todo: always draw labels here, configure visibility in update
        self.component: C = component
        self.diagram: 'TwlDiagram' = diagram
        self.tk_shapes: dict[int, Polygon] = {} #all tk_ids related to this shape with their position in the diagram

    def select(self):
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=DARK_SELECTED)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, self.selected_style(*tags))
        self.diagram.selection.append(self)
        print(f"selected: {self.component.id}")

    def deselect(self):
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=BLACK)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, self.default_style(*tags))
        self.diagram.selection.remove(self)
        print(f"deselected: {self.component.id}")

    @abstractmethod
    def is_at(self, x: int, y: int) -> bool:
        return False

    @abstractmethod
    def default_style(self, *tags: str) -> dict[str, str]:
        """Style attributes when the shape is not selected."""
        pass

    @abstractmethod
    def selected_style(self, *tags: str) -> dict[str, str]:
        """Style attributes when the shape is selected."""
        pass

    @property
    @abstractmethod
    def label_position(self) -> Point:
        pass

    def draw_label(self) -> tuple[int, int]:
        return self.diagram.create_text_with_bg(self.label_position.x, 
                                 self.label_position.y, 
                                 text=self.component.id, 
                                 tags=self.LABEL_TAG,
                                 bg_tag=self.LABEL_BG_TAG,
                                 font=('Helvetica', self.LABEL_SIZE))

    @abstractmethod
    def scale(self, factor: float):
        for tk_id, polygon in self.tk_shapes.items():
            coords = [coord * factor for point in polygon.points for coord in (point.x, point.y)]
            self.diagram.coords(tk_id, coords)


class NodeShape(Shape[Node]):

    TAG: str = "node"

    RADIUS: int = 6
    BORDER: int = 2

    LABEL_OFFSET = 15

    def __init__(self, node: Node, diagram: 'TwlDiagram') -> None:
        super().__init__(node, diagram)
        p1, p2 = self.circle_coords()
        tk_id = diagram.create_oval(p1.x, p1.y, p2.x, p2.y, 
                            fill=self.BG_COLOR, 
                            outline=self.COLOR, 
                            width = self.BORDER, 
                            tags=[*self.TAGS, str(node.id)])
        self.tk_shapes[tk_id] = Polygon(p1, p2)
        if (not self.TAG == Shape.TEMP) and TwlApp.settings().show_node_labels.get(): 
            label_tk_id, label_bg_tk_id = self.draw_label()
            self.tk_shapes[label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
            x1, x2, y1, y2 = self.diagram.bbox(label_tk_id)
            self.tk_shapes[label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

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

    @property
    def bounds(self) -> Polygon:
        return Polygon(Point(self.component.x, self.component.y))


class TempNodeShape(NodeShape):

    TAG: str = Shape.TEMP
    COLOR: str = Shape.TEMP_COLOR


class BeamShape(Shape[Beam]):

    TAG: str = "beam"
    WIDTH: int = 4

    def __init__(self, beam: Beam, diagram: 'TwlDiagram') -> None:
        super().__init__(beam, diagram)
        line = self.line_coords()
        tk_id = diagram.create_line(line.start.x, line.start.y,
                            line.end.x, line.end.y,
                            fill=self.COLOR,
                            width=self.WIDTH,
                            tags=[*self.TAGS, str(beam.id)])
        self.tk_shapes[tk_id] = Polygon(line.start, line.end)
        diagram.tag_lower(BeamShape.TAG, NodeShape.TAG)
        diagram.tag_lower(BeamShape.TAG, SupportShape.TAG)
        diagram.tag_lower(BeamShape.TAG, ForceShape.TAG)
        if (not self.TAG == Shape.TEMP) and TwlApp.settings().show_beam_labels.get(): 
            label_tk_id, label_bg_tk_id = self.draw_label()
            self.tk_shapes[label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
            x1, x2, y1, y2 = self.diagram.bbox(label_tk_id)
            self.tk_shapes[label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

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


class TempBeamShape(BeamShape):

    TAG: str = Shape.TEMP
    COLOR: str = Shape.TEMP_COLOR


class SupportShape(Shape[Support]):

    TAG: str = "support"

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2

    LINE_TAG: str = "support_line"
    LINE_SPACING: int = 5

    LABEL_OFFSET = 20

    def __init__(self, support: Support, diagram: 'TwlDiagram') -> None:
        super().__init__(support, diagram)
        triangle = self.triangle_coords()
        tk_id = diagram.create_polygon(triangle.p1.x, 
                               triangle.p1.y, 
                               triangle.p2.x, 
                               triangle.p2.y, 
                               triangle.p3.x, 
                               triangle.p3.y, 
                               fill=self.BG_COLOR, 
                               outline=self.COLOR, 
                               width=self.BORDER, 
                               tags=[*self.TAGS, str(support.id)])
        self.tk_shapes[tk_id] = Polygon(triangle.p1, triangle.p2, triangle.p3)
        if support.constraints == 1:
            line = self.line_coordinates
            tk_id = diagram.create_line(line.start.x, 
                                line.start.y, 
                                line.end.x, 
                                line.end.y, 
                                fill=self.COLOR, 
                                width=self.BORDER, 
                                tags=[*self.TAGS, str(support.id), self.LINE_TAG])
            self.tk_shapes[tk_id] = Polygon(line.start, line.end)
        diagram.tag_lower(SupportShape.TAG, NodeShape.TAG)
        if (not self.TAG == Shape.TEMP) and TwlApp.settings().show_support_labels.get(): 
            label_tk_id, label_bg_tk_id = self.draw_label()
            self.tk_shapes[label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
            x1, x2, y1, y2 = self.diagram.bbox(label_tk_id)
            self.tk_shapes[label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

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
        arrow = self.arrow_coords()
        tk_id = diagram.create_line(arrow.start.x, 
                            arrow.start.y, 
                            arrow.end.x, 
                            arrow.end.y, 
                            width=self.WIDTH, 
                            arrow=tk.FIRST, 
                            arrowshape=self.ARROW_SHAPE, 
                            fill=self.COLOR, 
                            tags=[*self.TAGS, str(force.id)])
        self.tk_shapes[tk_id] = Polygon(arrow.start, arrow.end)
        if (not self.TAG == Shape.TEMP) and TwlApp.settings().show_force_labels.get(): 
            label_tk_id, label_bg_tk_id = self.draw_label()
            self.tk_shapes[label_tk_id] = Polygon(Point(self.label_position.x, self.label_position.y))
            x1, x2, y1, y2 = self.diagram.bbox(label_tk_id)
            self.tk_shapes[label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))

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


class TempForceShape(ForceShape):

    TAG: str = Shape.TEMP
    COLOR = Shape.TEMP_COLOR


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
        self.diagram.bind("<Leave>", lambda *ignore: self.diagram.delete_with_tag(Shape.TEMP))

    def deactivate(self):
        self.diagram.unbind("<Button-1>")
        self.diagram.unbind("<Motion>")
        self.diagram.unbind("<Escape>")
        self.diagram.unbind("<Leave>")
        self.reset()

    def reset(self):
        self.diagram.delete_with_tag(Shape.TEMP)

    def correct_event_pos(self, event):
        """Correct the coordinates of the mouse pointer to account for the scrolling position of the diagram."""
        x_min, y_min, x_max, y_max = self.diagram.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        event.x = event.x + self.diagram.xview()[0] * sr_width - abs(x_min)
        event.y = event.y + self.diagram.yview()[0] * sr_height - abs(y_min)

    def snap_event_to_grid(self, event):
        if TwlApp.settings().show_grid.get():
            snap_point = self.diagram.grid_snap(event.x, event.y)
            event.x = snap_point[0]
            event.y = snap_point[1]

    def _action(self, event):
        self.correct_event_pos(event)
        self.snap_event_to_grid(event)
        self.action(event)

    def action(self, event):
        """Code to be executed when the user clicks on the canvas while the tool is active"""
        pass

    def _preview(self, event):
        self.correct_event_pos(event)
        self.snap_event_to_grid(event)
        self.preview(event)

    def preview(self, event):
        """Preview of the action when the user moves the mouse on the canvas while the tool is active"""
        pass

    def holding_shift_key(self, event) -> bool:
        return event.state & 0x1 #bitwise ANDing the event.state with the ShiftMask flag


class SelectTool(Tool):

    ID: int = 0
    NAME: str = "Select"
    DESCR: str = "Select objects in model."
    ICON: str = "img/select_icon.png"

    def __init__(self, diagram: 'TwlDiagram'):
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
    def selectable_shapes(self) -> list[Shape]:
        return list(filter(lambda s: isinstance(s.component, (Beam, Support, Force)), self.diagram.shapes))

    def action(self, event):
        self.diagram.focus_set()
        shape = self.diagram.find_shape_of_list_at(self.selectable_shapes, event.x, event.y)
        if shape == None:
            self.start_rect_selection(event)
        else:
            self.process_selection(event, shape)

    def start_rect_selection(self, event):
        self.selection_rect = self.diagram.create_rectangle(event.x, event.y, event.x, event.y, outline=Shape.SELECTED_COLOR, width=2)

    def continue_rect_selection(self, event):
        if not self.selection_rect:
            return
        start_x, start_y, _, _ = self.diagram.coords(self.selection_rect)
        self.diagram.coords(self.selection_rect, start_x, start_y, event.x, event.y)

    def end_rect_selection(self, event):
        selected: List[Shape] = []
        if not self.selection_rect:
            return
        x1, y1, x2, y2 = map(int, self.diagram.coords(self.selection_rect))
        print(f"Selected area: ({x1}, {y1}) to ({x2}, {y2})")
        p1 = Point(x1, y1)
        p2 = Point(x2, y2)
        selection = [shape for shape in self.selectable_shapes if all(polygon.in_bounds(p1, p2) for polygon in shape.tk_shapes.values())]
        self.process_selection(event, *selection)

    def process_selection(self, event, *selection: Shape):
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
        TwlApp.update_manager().pause()
        [shape.component.delete() for shape in self.diagram.selection]
        TwlApp.update_manager().resume()
        self.reset()


class BeamTool(Tool):

    ID: int = 1
    NAME: str = "Beam Tool"
    DESCR: str = "Create beam between two nodes."
    ICON: str = "img/beam_icon.png"

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
        if self.holding_shift_key(event):
            self.shift_snap_line(event)    
        if not self.start_node in TwlApp.model().nodes:
            self.start_node = self.diagram.create_node(self.start_node.x, self.start_node.y)
        end_node = clicked_node if clicked_node else self.diagram.create_node(event.x, event.y)
        self.diagram.create_beam(self.start_node, end_node)
        self.start_node = end_node

    def create_temp_node(self, x, y) -> Node:
        temp_node = Node(Model(TwlUpdateManager()), x, y)
        TempNodeShape(temp_node, self.diagram)
        return temp_node

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        temp_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
        if not self.start_node:
            if not temp_node:
                temp_node = Node(Model(TwlUpdateManager()), event.x, event.y)
                TempNodeShape(temp_node, self.diagram)
            return
        if not self.start_node in TwlApp.model().nodes:
            TempNodeShape(self.start_node, self.diagram)
        if self.holding_shift_key(event):
            self.shift_snap_line(event)            
        if not temp_node:
            temp_node = Node(Model(TwlUpdateManager()), event.x, event.y)
            TempNodeShape(temp_node, self.diagram)
        temp_beam = Beam(Model(TwlUpdateManager()), self.start_node, temp_node)
        TempBeamShape(temp_beam, self.diagram)
        self.diagram.focus_set()

    def shift_snap_line(self, event):
        assert(self.start_node)
        start_point = Point(self.start_node.x, self.start_node.y)
        inital_line = Line(start_point, Point(event.x, event.y))
        rounded_line = Line(start_point, Point(start_point.x, start_point.y + 10))
        rounded_line.rotate(start_point, inital_line.angle_rounded())
        new_point = rounded_line.closest_point_on_axis(Point(event.x, event.y))
        event.x = new_point.x
        event.y = new_point.y

class SupportTool(Tool):

    ID: int = 2
    NAME: str = "Support Tool"
    DESCR: str = "Create support on node."
    ICON: str = "img/support_icon.png"

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
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.diagram.create_support(self.node, angle)
            self.reset()

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node and not hovering_node.supports:
                TempSupportShape(Support(Model(TwlUpdateManager()), hovering_node), self.diagram)
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            TempSupportShape(Support(Model(TwlUpdateManager()), self.node, angle), self.diagram)
        self.diagram.focus_set()


class ForceTool(Tool):

    ID: int = 3
    NAME: str = "Force Tool"
    DESCR: str = "Create force on node."
    ICON: str = "img/force_icon.png"

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
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            self.diagram.create_force(self.node, angle)
            self.reset()

    def preview(self, event):
        self.diagram.delete_with_tag(Shape.TEMP)
        if not self.node:
            hovering_node = self.diagram.find_component_of_type_at(Node, event.x, event.y)
            if hovering_node:
                TempForceShape(Force(Model(TwlUpdateManager()), hovering_node), self.diagram)
        else:
            line = Line(Point(self.node.x, self.node.y), Point(event.x, event.y))
            angle = line.angle_rounded() if self.holding_shift_key(event) else line.angle()
            TempForceShape(Force(Model(TwlUpdateManager()), self.node, angle), self.diagram)
        self.diagram.focus_set()


class TwlDiagram(tk.Canvas, TwlWidget):

    ZOOM_STEP: float = 0.05
    MIN_ZOOM: float = 0.1
    MAX_ZOOM: float = 5

    SCROLL_EXTEND: int = 100

    STAT_DETERM_LABEL_PADDING: int = 10
    TOOL_BUTTON_SIZE: int = 50

    TEXT_TAG = "text"
    TEXT_BG_TAG = "text"
    TEXT_SIZE = 10

    GRID_TAG = "grid"
    GRID_COLOR = "lightgrey"
    GRID_SNAP_RADIUS = 5

    ANGLE_GUIDE_TAG = "angle_guide"
    ANGLE_GUIDE_IMG = "img/angle_guide.png"
    ANGLE_GUIDE_SIZE = 120
    ANGLE_GUIDE_PADDING = 10

    NO_UPDATE_TAGS = [GRID_TAG, ANGLE_GUIDE_TAG]

    def __init__(self, master, toolbar):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)
        self.scale_origin = Point(0, 0)
        self.current_scale = 1.0
        self.grid(column=0, row=0, sticky=tk.NSEW)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.create_scrollbars(master)

        self.shapes: list[Shape] = []
        self.selection: list[Shape] = []
        self.grid_visible: bool = False
        self.angle_guide_visible: bool = False

        #toolbar
        self.tools: List[Tool] = [SelectTool(self), BeamTool(self), SupportTool(self), ForceTool(self)]
        self._selected_tool_id: tk.IntVar = IntVar(value=0)
        self.selected_tool: Tool = self.tools[0]
        for tool in self.tools: self.add_button(tool, toolbar)
        outer = ttk.Frame(toolbar, style="Outer.Border.TFrame") #todo: create custom widget BorderFrame
        outer.pack(fill="both", expand=True)
        ttk.Frame(outer, style="Inner.Border.TFrame").pack(padx=1, pady=1, fill="both", expand=True)

        #statically determinate label
        self.stat_determ_label = ttk.Label(self, style= "Diagram.TLabel", text=self.stat_determ_text)
        self.stat_determ_label.place(x=TwlDiagram.STAT_DETERM_LABEL_PADDING, y=TwlDiagram.STAT_DETERM_LABEL_PADDING)

        #zoom label
        self.zoom_label = ttk.Label(self, style="Diagram.TLabel", text="Zoom: 100%")
        self.zoom_label.place(x=200, y=200, anchor=tk.SW)
        #self.zoom_label.place(x=TwlDiagram.STAT_DETERM_LABEL_PADDING, y=self.winfo_height() - TwlDiagram.STAT_DETERM_LABEL_PADDING, anchor=tk.SW)

        #angle guide
        angle_guide_img = add_image_from_path(self.ANGLE_GUIDE_IMG, self.ANGLE_GUIDE_SIZE, self.ANGLE_GUIDE_SIZE)
        self.angle_guide = self.create_image(self.winfo_width() - self.ANGLE_GUIDE_PADDING, 
                                             self.ANGLE_GUIDE_PADDING, 
                                             image=angle_guide_img, 
                                             anchor=tk.NE, 
                                             tags=self.ANGLE_GUIDE_TAG)

        #grid and angle guide refresh
        self.bind("<Configure>", self.resize)
        self.bind("<MouseWheel>", self.zoom)

        self.update_scrollregion()
        #set initial tool
        self.select_tool(SelectTool.ID)

    def create_scrollbars(self, master):
        v_scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=lambda *args: self.scroll(tk.VERTICAL, *args))
        v_scrollbar.grid(column=1, row=0, sticky=tk.NS)

        h_scrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=lambda *args: self.scroll(tk.HORIZONTAL, *args))
        h_scrollbar.grid(column=0, row=1, sticky=tk.EW)

        corner = tk.Frame(master, background=LIGHT_GRAY)
        corner.grid(column=1, row=1, sticky=tk.NSEW)

        self.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

    def scroll(self, scroll_type, *args):
        if scroll_type == tk.VERTICAL:
            self.yview(*args)
        elif scroll_type == tk.HORIZONTAL:
            self.xview(*args)
        self.delete_grid()
        if TwlApp.settings().show_grid.get():
            self.draw_grid()
        self.update_angle_guide_position()

    def update_scrollregion(self):
        shapes = [tk_id for shape in self.shapes for tk_id in shape.tk_shapes.keys()]
        if shapes:
            bbox = self.bbox(*shapes) if shapes else (0, 0, 0, 0)
            self.configure(scrollregion=(min(0, bbox[0] - self.SCROLL_EXTEND), 
                                     min(0, bbox[1] - self.SCROLL_EXTEND), 
                                     max(self.winfo_width(), bbox[2] + self.SCROLL_EXTEND), 
                                     max(self.winfo_height(), bbox[3] + self.SCROLL_EXTEND)))
        else:
            self.configure(scrollregion=(0, 0, self.winfo_width(), self.winfo_height()))
            self.scroll("horizontal", "moveto", 0)
            self.scroll("vertical", "moveto", 0)

    def get_scrollregion(self) -> tuple[int, int, int, int]:
        sr_str = self.cget("scrollregion") or "0 0 0 0"
        sr_int = tuple([int(num) for num in sr_str.split()])
        assert len(sr_int) == 4
        return sr_int

    def zoom(self, event): #todo: scroll to previous position in drawing
        if event.delta < 0:
            self.current_scale = max(self.MIN_ZOOM, self.current_scale - self.ZOOM_STEP)
        else:
            self.current_scale = min(self.MAX_ZOOM, self.current_scale + self.ZOOM_STEP)

        self.zoom_label.configure(text=f"Zoom: {round(self.current_scale * 100, 2)}%")
        for shape in self.shapes:
            shape.scale(self.current_scale)

    def resize(self, event):
        self.update_scrollregion()
        self.delete_grid()
        if TwlApp.settings().show_grid.get():
            self.draw_grid()
        self.update_angle_guide_position()

    def update_angle_guide_position(self):
        x_min, y_min, x_max, y_max = self.get_scrollregion()
        sr_width = abs(x_min) + abs(x_max)
        sr_height = abs(y_min) + abs(y_max)
        self.coords(self.angle_guide, self.winfo_width() + (self.xview()[0] * sr_width) - abs(x_min) - self.ANGLE_GUIDE_PADDING, 
                    self.ANGLE_GUIDE_PADDING + (self.yview()[0] * sr_height) - abs(y_min))

    def delete_grid(self):
        self.delete(self.GRID_TAG)
        self.grid_visible = False

    def draw_grid(self):
        grid_spacing = round(TwlApp.settings().grid_spacing.get() * self.current_scale)
        x_min, y_min, x_max, y_max = self.get_scrollregion()
        x_start = x_min - (x_min % grid_spacing) + grid_spacing
        y_start = y_min - (y_min % grid_spacing) + grid_spacing
        for i in range(x_start, x_max, grid_spacing):
            self.create_line((i, y_min), (i, y_max), fill=self.GRID_COLOR, tags=self.GRID_TAG)
        for i in range(y_start, y_max, grid_spacing):
            self.create_line((x_min, i), (x_max, i), fill=self.GRID_COLOR, tags=self.GRID_TAG)
        self.tag_lower(self.GRID_TAG)
        self.grid_visible = True

    def grid_snap(self, x: int, y: int) -> tuple[int, int]:
        grid_spacing = TwlApp.settings().grid_spacing.get()
        nearest_x = round(x / grid_spacing) * grid_spacing
        nearest_y = round(y / grid_spacing) * grid_spacing
        distance = Point(x, y).distance_to_point(Point(nearest_x, nearest_y))
        if distance < TwlApp.settings().grid_snap_radius.get():
            return nearest_x, nearest_y
        return x, y

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

    def clear(self):
        """Removes all model shapes from the diagram."""
        for shape in self.find_all():
            tags = set(self.gettags(shape))
            if not tags.intersection(self.NO_UPDATE_TAGS):
                self.delete(shape)

    def update(self) -> None:
        """Redraws the diagram completely from the model."""
        self.clear()
        self.shapes.clear()

        for node in TwlApp.model().nodes: self.shapes.append(NodeShape(node, self))
        for beam in TwlApp.model().beams: self.shapes.append(BeamShape(beam, self))
        for support in TwlApp.model().supports: self.shapes.append(SupportShape(support, self))
        for force in TwlApp.model().forces: self.shapes.append(ForceShape(force, self))

        self.stat_determ_label.configure(text=self.stat_determ_text)
        color = GREEN if self.stat_determ_text[:5] == "f = 0" else RED
        ttk.Style().configure("Diagram.TLabel", foreground=color)
        self.tag_lower(self.GRID_TAG)
        self.tag_raise(self.ANGLE_GUIDE_TAG)

        self.update_scrollregion()

        angle_guide_state = tk.NORMAL if TwlApp.settings().show_angle_guide.get() else tk.HIDDEN
        self.itemconfigure(self.angle_guide, state=angle_guide_state)

        if not TwlApp.settings().show_grid.get() and self.grid_visible:
            self.delete_grid()
        elif TwlApp.settings().show_grid.get() and not self.grid_visible:
            self.draw_grid()

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
        self.tag_lower(bg_tag, kw["tags"])
        return text_id, bg_id

    def find_shape_at(self, x: int, y: int) -> Shape | None:
        """Check if there is a shape in the diagram at the specified coordinate."""
        return next(filter(lambda shape: shape.is_at(x, y), self.shapes), None)

    def find_shape_of_list_at(self, shapes: list[Shape], x: int, y: int) -> Shape | None:
        """Check if there is a shape that is included in the list in the diagram at the specified coordinate."""
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

    def find_except_withtags(self, *tagOrIds: str | int) -> tuple[int, ...]:
        return tuple([id for id in self.find_all() if all(id != tagOrId and tagOrId not in self.gettags(id) for tagOrId in tagOrIds)])

    def tag_lower(self, lower: str | int, upper: str | int | None = None) -> None:
        if self.find_withtag(lower) and (not upper or self.find_withtag(upper)):
            super().tag_lower(lower, upper)

    def delete_with_tag(self, tag: str):
        [self.delete(shape) for shape in self.find_withtag("temp")]