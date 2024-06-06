import tkinter as tk

from twl_app import *
from twl_update import *
from twl_components import *
from twl_settings import *
from twl_solver import *

class CremonaDiagram(tk.Canvas, TwlWidget):

    START_POINT = Point(800, 50)
    SCALE = 6
    BASE_LINE_LENGTH = 20
    BASE_LINE_SPACING = 20

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)
        self.support_forces = []
        self.beam_forces = []
        self.forces_for_nodes: dict[Node, List[Force]] = {}
        self.lines: List[int] = []

    def update(self) -> None:
        self.delete("all")
        pos = self.START_POINT
        self.support_forces = [force for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)]
        self.beam_forces = [force for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)]
        self.forces_for_nodes = {node: self.get_forces_for_node(node) for node in TwlApp.model().nodes}
        self.lines = []
        self.draw_baseline(pos)
        for force in TwlApp.model().forces:
            pos = self.draw_line(pos, force)
        self.draw_baseline(pos)
        pos = Point(pos.x + self.BASE_LINE_SPACING, pos.y)
        for force in self.support_forces:
            pos = self.draw_line(pos, force)
        pos = Point(pos.x - 2 * self.BASE_LINE_SPACING, pos.y)
        node = self.find_next_node()
        while node:
            start_angle = self.get_start_angle(self.forces_for_nodes[node])
            sorted_forces = sorted(self.forces_for_nodes[node], key=lambda force: (force.angle - start_angle) % 360)
            start_coords = self.coords(self.find_withtag(sorted_forces[0].id)[0])
            pos = Point(round(start_coords[0]), round(start_coords[1]))
            for force in sorted_forces:
                if force in self.support_forces or force in node.forces:
                    coords = self.coords(self.find_withtag(force.id)[0])
                    pos = Point(round(coords[2]), round(coords[3]))
                else:
                    pos = self.draw_line(pos, force)
            self.forces_for_nodes.pop(node)
            node = self.find_next_node()

    def find_next_node(self):
        return next((node for node in self.forces_for_nodes.keys() if self.count_unknown_on_node(node) <= 2), None)

    def count_unknown_on_node(self, node) -> int:
        return sum(len(self.find_withtag(force.id)) == 0 for force in self.forces_for_nodes[node])

    def get_start_angle(self, forces: List[Force]):
        return next(force.angle for force in forces if len(self.find_withtag(force.id)) > 0)

    def get_forces_for_node(self, node: Node):
        forces: List[Force] = node.forces
        forces.extend([force for force in self.support_forces if force.node == node])
        forces.extend(self.get_beam_forces_on_node(node))
        return forces

    def get_beam_forces_on_node(self, node: Node) -> List[Force]:
        forces: List[Force] = []
        for beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            angle = Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
            strength = next((force.strength for force in TwlApp.solver().solution.keys() if force.id == beam.id))
            forces.append(Force.dummy(beam.id, node, angle, strength))
        return forces

    def find_start_node(self):
        return next(node for node in TwlApp.model().nodes if len(node.beams) <= 2)

    def draw_baseline(self, pos: Point):
        self.create_line(pos.x - self.BASE_LINE_LENGTH - self.BASE_LINE_SPACING, pos.y, pos.x + self.BASE_LINE_LENGTH + self.BASE_LINE_SPACING, pos.y, dash=(2, 1, 1, 1))

    def draw_line(self, start: Point, force: Force) -> Point:
        angle = math.radians(force.angle)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        self.lines.append(self.create_line(start.x, start.y, end.x, end.y, arrow=tk.LAST, tags=force.id))
        return end

    def find_withtag(self, tagOrId: str | int) -> tuple[int, ...]:
        return tuple(filter(lambda id: (id == tagOrId) or (tagOrId in self.gettags(id)), self.find_all()))