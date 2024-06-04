import tkinter as tk

from twl_app import *
from twl_update import *
from twl_components import *
from twl_settings import *
from twl_solver import *

class CremonaDiagram(tk.Canvas, TwlWidget):

    START_POINT = Point(700, 50)
    SCALE = 7
    BASE_LINE_LENGTH = 20
    BASE_LINE_SPACING = 20

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)

    def update(self) -> None:
        self.delete("all")
        pos = self.START_POINT
        self.draw_baseline(pos)
        for force in TwlApp.model().forces:
            pos = self.draw_line(pos, force)
        self.draw_baseline(pos)
        pos = Point(pos.x + self.BASE_LINE_SPACING, pos.y)
        support_forces = [item for item in TwlApp.solver().solution.items() if type(item[1]) == Support]
        for force, component in support_forces:
            pos = self.draw_line(pos, force)
        pos = Point(pos.x - 2 * self.BASE_LINE_SPACING, pos.y)

    def find_start_node(self):
        return next(node for node in TwlApp.model().nodes if len(node.beams) <= 2)

    def draw_baseline(self, pos: Point):
        self.create_line(pos.x - self.BASE_LINE_LENGTH - self.BASE_LINE_SPACING, pos.y, pos.x + self.BASE_LINE_LENGTH + self.BASE_LINE_SPACING, pos.y, dash=(2, 1, 1, 1))

    def draw_line(self, start: Point, force: Force) -> Point:
        angle = math.radians(force.angle)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        self.create_line(start.x, start.y, end.x, end.y, arrow=tk.LAST, tags=force.id)
        return end