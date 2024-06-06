import tkinter as tk

from twl_app import *
from twl_update import *
from twl_components import *
from twl_settings import *
from twl_solver import *

class CremonaDiagram(tk.Canvas, TwlWidget):

    START_POINT = Point(800, 50)
    SCALE = 6

    BASE_LINE_TAG = "baseline"
    BASE_LINE_LENGTH = 20
    BASE_LINE_SPACING = 20
    BASE_LINE_DASH = (2, 1, 1, 1)
    BASE_LINE_WIDTH = 1

    LINE_WIDTH = 2
    SELECTED_LINE_WIDTH = 3
    ARROW_SHAPE = (12,12,4)

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)
        self.support_forces: dict[Force, Support] = {}
        self.beam_forces: dict[Force, Beam] = {}
        self.forces_for_nodes: dict[Node, dict[Force, Component]] = {}
        self.steps: List[tuple[int, Force, Component]] = []

    def update(self) -> None:
        self.delete("all")
        pos = self.START_POINT
        self.support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        self.beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        self.forces_for_nodes = {node: self.get_forces_for_node(node) for node in TwlApp.model().nodes}
        self.steps = []
        self.draw_baseline(pos)
        for force in TwlApp.model().forces:
            pos = self.draw_line(pos, force, force)
        self.draw_baseline(pos)
        pos = Point(pos.x + self.BASE_LINE_SPACING, pos.y)
        for force, support in self.support_forces.items():
            pos = self.draw_line(pos, force, support)
        pos = Point(pos.x - 2 * self.BASE_LINE_SPACING, pos.y)
        node = self.find_next_node()
        while node:
            start_angle = self.get_start_angle(self.forces_for_nodes[node])
            sorted_forces = dict(sorted(self.forces_for_nodes[node].items(), key=lambda item: (item[0].angle - start_angle) % 360))
            start_coords = self.coords(self.find_withtag(list(sorted_forces.keys())[0].id)[0])
            pos = Point(round(start_coords[2]), round(start_coords[3]))
            for force, component in sorted_forces.items():
                if type(component) == Support or type(component) == Force:
                    line_id = self.find_withtag(force.id)[0]
                    self.steps.append((line_id, force, component))
                    coords = self.coords(line_id)
                    x = round(coords[2] - (coords[2] - self.START_POINT.x) - self.BASE_LINE_SPACING)
                    pos = Point(x, round(coords[3]))
                else:
                    pos = self.draw_line(pos, force, component)
            self.forces_for_nodes.pop(node)
            node = self.find_next_node()

    def find_next_node(self):
        return next((node for node in self.forces_for_nodes.keys() if self.count_unknown_on_node(node) <= 2), None)

    def count_unknown_on_node(self, node) -> int:
        return sum(len(self.find_withtag(force.id)) == 0 for force in self.forces_for_nodes[node])

    def get_start_angle(self, forces: dict[Force, Component]):
        return next((force.angle for force in forces.keys() if len(self.find_withtag(force.id)) > 0 and force.strength > 0.001), 0)

    def get_forces_for_node(self, node: Node) -> dict[Force, Component]:
        forces: dict[Force, Component] = {force: force for force in node.forces}
        forces.update({force: support for force, support in self.support_forces.items() if force.node == node})
        forces.update(self.get_beam_forces_on_node(node))
        return forces

    def get_beam_forces_on_node(self, node: Node) -> dict[Force, Beam]:
        forces: dict[Force, Beam] = {}
        for beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            angle = Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
            strength = next((force.strength for force in TwlApp.solver().solution.keys() if force.id == beam.id))
            forces[Force.dummy(beam.id, node, angle, strength)] = beam
        return forces

    def find_start_node(self):
        return next(node for node in TwlApp.model().nodes if len(node.beams) <= 2)

    def draw_baseline(self, pos: Point):
        self.create_line(pos.x - self.BASE_LINE_LENGTH - self.BASE_LINE_SPACING, pos.y, pos.x + self.BASE_LINE_LENGTH + self.BASE_LINE_SPACING, pos.y, dash=self.BASE_LINE_DASH, tags=self.BASE_LINE_TAG)

    def draw_line(self, start: Point, force: Force, component: Component) -> Point:
        angle = math.radians((force.angle + 180) % 360) if type(component) == Force else math.radians(force.angle)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        self.steps.append((self.create_line(start.x, start.y, end.x, end.y, width=self.LINE_WIDTH, arrow=tk.LAST, arrowshape=self.ARROW_SHAPE, tags=force.id), force, component))
        return end

    def find_withtag(self, tagOrId: str | int) -> tuple[int, ...]:
        return tuple(filter(lambda id: (id == tagOrId) or (tagOrId in self.gettags(id)), self.find_all()))