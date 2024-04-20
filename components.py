from abc import ABC, abstractmethod
from twl_math import Point, Line

class Component(ABC):
    def __init__(self, id: int):
        self.id: int = id #id corresponding to the id of the Shape in the diagram

    def select(self):
        pass

    def deselect(self):
        pass

    @classmethod
    @abstractmethod
    def get_table_columns(cls) -> tuple:
        pass #returns the table columns for the component type

    @abstractmethod
    def get_table_entry(self) -> tuple:
        pass #return a table entry for the component instance

    def is_at(self, x: int, y: int) -> bool:
        return False


class Node(Component):

    RADIUS: int = 6
    BORDER: int = 2

    def __init__(self, id: int, x: int, y: int):
        super().__init__(id)
        self.x: int = x
        self.y: int = y

    def is_at(self, x: int, y: int) -> bool:
        return True if abs(self.x - x) <= self.RADIUS and abs(self.y - y) <= self.RADIUS else False

    @classmethod
    def get_table_columns(cls) -> tuple:
        return ()

    def get_table_entry(self) -> tuple:
        return ()
    

class Beam(Component):

    WIDTH: int = 4

    def __init__(self, id: int, start_node: Node, end_node: Node):
        super().__init__(id)
        self.start_node: Node = start_node
        self.end_node:Node = end_node

    def is_at(self, x: int, y: int) -> bool:
        beam = Line(Point(self.start_node.x, self.start_node.y), Point(self.end_node.x, self.end_node.y))
        return Point(x, y).distance(beam) < self.WIDTH/2
    
    def length(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).length()

    def angle(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).angle()

    @classmethod
    def get_table_columns(cls) -> tuple:
        return ("Length", "Angle")

    def get_table_entry(self) -> tuple:
        return (self.length(), self.angle())


class Support(Component):

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2

    def __init__(self, id, node: Node, angle: float=0):
        super().__init__(id)
        self.node: Node = node
        self.angle: float = angle

    def is_at(self, x: int, y: int) -> bool:
        s_point = Point(x, y)
        n_point = Point(self.node.x, self.node.y)
        l_point = Point(int(n_point.x - Support.WIDTH / 2), n_point.y + Support.HEIGHT)
        r_point = Point(int(n_point.x + Support.WIDTH / 2), n_point.y + Support.HEIGHT)
        l_point.rotate(n_point, self.angle)
        r_point.rotate(n_point, self.angle)

        v0 = l_point.subtract(n_point)
        v1 = r_point.subtract(n_point)
        v2 = s_point.subtract(n_point)

        dot00 = v0.dot_product(v0)
        dot01 = v0.dot_product(v1)
        dot02 = v0.dot_product(v2)
        dot11 = v1.dot_product(v1)
        dot12 = v1.dot_product(v2)

        # Compute barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        w = 1 - u - v

        #Check if the point is inside the triangle
        return u >= 0 and v >= 0 and w >= 0 and u + v + w <= 1
    
    @classmethod
    def get_table_columns(cls) -> tuple:
        return ("Angle", "Node")

    def get_table_entry(self) -> tuple:
        return (self.angle, self.node.id)


class Force(Component):

    LENGTH = 40
    WIDTH = 6
    DISTANCE_FROM_NODE = 10
    ARROW_SHAPE = (15,14,10)

    def __init__(self, id, node: Node, angle: float=0):
        super().__init__(id)
        self.node: Node = node
        self.angle: float = angle

    def is_at(self, x: int, y: int) -> bool:
        return Point(x, y).distance(self.arrow()) < self.WIDTH/2

    def arrow(self) -> Line:
        n = Point(self.node.x, self.node.y)
        a1 = Point(n.x, n.y + Force.DISTANCE_FROM_NODE)
        a2 = Point(a1.x, a1.y + Force.LENGTH)
        a1.rotate(n, self.angle)
        a2.rotate(n, self.angle)
        return Line(a1, a2)

    @classmethod
    def get_table_columns(cls) -> tuple:
        return ("Angle", "Node")

    def get_table_entry(self) -> tuple:
        return (self.angle, self.node.id)