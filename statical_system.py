from typing import TypeVar
import math

class Point:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def rotate(self, center_of_rotation: 'Point', angle: float):
        #Translate the point to be rotated so that the center of rotation becomes the origin
        translated_x = self.x - center_of_rotation.x
        translated_y = self.y - center_of_rotation.y
        
        #Rotate the translated point around the origin by the specified angle
        rotated_x = int(translated_x * math.cos(angle) - translated_y * math.sin(angle))
        rotated_y = int(translated_x * math.sin(angle) + translated_y * math.cos(angle))
        
        #Translate the rotated point back to its original position
        self.x = rotated_x + center_of_rotation.x
        self.y = rotated_y + center_of_rotation.y

    def subtract(self, other) -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def dot_product(self, other) -> float:
        return self.x * other.x + self.y * other.y

class Polygon:
    def __init__(self, *points: Point) -> None:
        self.points: list[Point] = list(points)
        
    @classmethod
    def from_list(cls, point_list: list[Point]) -> 'Polygon':
        return cls(*point_list)

class Component:
    def __init__(self, id: int):
        self.id: int = id #id corresponding to the id of the Shape in the diagram

    def select(self):
        pass

    def deselect(self):
        pass

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

class Beam(Component):

    WIDTH: int = 4

    def __init__(self, id: int, start_node: Node, end_node: Node):
        super().__init__(id)
        self.start_node: Node = start_node
        self.end_node:Node = end_node

    def is_at(self, x: int, y: int) -> bool:
        #Algorithm to calculate distance from point to line segment
        px = self.end_node.x-self.start_node.x
        py = self.end_node.y-self.start_node.y

        norm = px*px + py*py

        u =  ((x - self.start_node.x) * px + (y - self.start_node.y) * py) / float(norm)
        u = max(min(1, u), 0)

        dx = x - (self.start_node.x + u * px)
        dy = y - (self.start_node.y + u * py)

        dist = (dx*dx + dy*dy)**.5

        return dist < self.WIDTH/2

class Support(Component):

    HEIGHT: int = 24
    WIDTH: int = 28
    BORDER: int = 2

    def __init__(self, id, node: Node, angle: int = 0):
        super().__init__(id)
        self.node: Node = node
        self.angle: int = angle

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

class Force(Component):
    def __init__(self, id, node: Node):
        super().__init__(id)
        self.node: Node = node

class StaticalSystem:
    def __init__(self):
        self.nodes: list[Node] = []
        self.beams: list[Beam] = []
        self.supports: list[Support] = []
        self.forces: list[Force] = []

    def create_node(self, id: int, x: int, y: int) -> Node:
        node = Node(id, x, y)
        self.nodes.append(node)
        return node

    def create_beam(self, id: int, start_node: Node, end_node: Node) -> Beam:
        beam = Beam(id, start_node, end_node)
        self.beams.append(beam)
        return beam
    
    def create_support(self, id: int, node: Node) -> Support:
        support = Support(id, node)
        self.supports.append(support)
        return support
    
    C = TypeVar('C', bound=Component)
    @staticmethod
    def find_component_at(x: int, y: int, components: list[C]) -> C | None:
        """Checks if one of the components in the list is at the specified Coordinate"""
        return next(filter(lambda c: c.is_at(x, y), components), None)
