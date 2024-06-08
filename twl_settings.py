from typing import Any
from tkinter import BooleanVar, IntVar

from twl_update import *

class Settings:

    def __init__(self, update_manager: TwlUpdateManager) -> None:
        self.update_manager = update_manager
    
        self.show_node_labels = BooleanVar(value=True)
        self.show_node_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_beam_labels = BooleanVar(value=True)
        self.show_beam_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_force_labels = BooleanVar(value=True)
        self.show_force_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_support_labels = BooleanVar(value=True)
        self.show_support_labels.trace_add("write", lambda *ignore: self.update_manager.update())

        self.show_grid = BooleanVar(value=True)
        self.show_grid.trace_add("write", lambda *ignore: self.update_manager.update())
        self.grid_snap_radius = IntVar(value=7)
        self.grid_snap_radius.trace_add("write", lambda *ignore: self.update_manager.update())

        self.show_angle_guide = BooleanVar(value=True)
        self.show_angle_guide.trace_add("write", lambda *ignore: self.update_manager.update())

        self.force_spacing = BooleanVar(value=True)
        self.force_spacing.trace_add("write", lambda *ignore: self.update_manager.update_results())