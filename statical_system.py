from typing import TypeVar

class Component:
    def __init__(self, id: int):
        self.id: int = id #id corresponding to the id of the shape in the diagram

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
    def __init__(self, id, node: Node):
        super().__init__(id)
        self.node: Node = node

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
    
    C = TypeVar('C', bound=Component)
    @staticmethod
    def find_component_at(x: int, y: int, components: list[C]) -> C | None:
        """Checks if one of the components in the list is at the specified Coordinate"""
        return next(filter(lambda c: c.is_at(x, y), components), None)
