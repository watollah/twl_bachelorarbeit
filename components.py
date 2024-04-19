from typing import Callable
from abc import ABC, abstractmethod
from twl_math import Point

class Component(ABC):
    def __init__(self, id: int):
        self.id: int = id #id corresponding to the id of the Shape in the diagram

    def select(self):
        pass

    def deselect(self):
        pass


    @abstractmethod
    def get_table_entry(self) -> tuple:
        pass #return a function that takes a component and returns a table-entry for it, to be implemented by subclasses

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
    
    def get_table_entry(self) -> tuple:
        return (self.x, self.y)
    

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

    def get_table_entry(self) -> tuple:
        return (self.start_node.id, self.end_node.id)


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
    
    def get_table_entry(self) -> tuple:
        return (self.angle, self.node.id)


class Force(Component):
    def __init__(self, id, node: Node):
        super().__init__(id)
        self.node: Node = node