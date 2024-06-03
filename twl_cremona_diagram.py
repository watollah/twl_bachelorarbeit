import tkinter as tk

from twl_app import *
from twl_update import *
from twl_components import *
from twl_settings import *
from twl_solver import *

class CremonaDiagram(tk.Canvas, TwlWidget):

    START_POINT = Point(400, 100)
    SCALE = 3

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.configure(background="white", highlightthickness=0)

    def update(self) -> None:
        pos = self.START_POINT
        for force in TwlApp.model().forces:
            pos = self.draw_line(pos, force)
        for Force, Component in TwlApp.solver().solution.items():
            pass

    def draw_line(self, start: Point, force: Force) -> Point:
        angle = math.radians(force.angle)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        self.create_line(start.x, start.y, end.x, end.y, arrow=tk.LAST)
        return end