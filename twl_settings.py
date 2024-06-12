import tkinter as tk

from twl_update import UpdateManager


class Settings:

    def __init__(self, update_manager: UpdateManager) -> None:
        self.update_manager = update_manager
    
        self.show_node_labels = tk.BooleanVar(value=True)
        self.show_node_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_beam_labels = tk.BooleanVar(value=True)
        self.show_beam_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_force_labels = tk.BooleanVar(value=True)
        self.show_force_labels.trace_add("write", lambda *ignore: self.update_manager.update())
        self.show_support_labels = tk.BooleanVar(value=True)
        self.show_support_labels.trace_add("write", lambda *ignore: self.update_manager.update())

        self.show_grid = tk.BooleanVar(value=True)
        self.show_grid.trace_add("write", lambda *ignore: self.update_manager.update())
        self.grid_snap_radius = tk.IntVar(value=7)
        self.grid_snap_radius.trace_add("write", lambda *ignore: self.update_manager.update())

        self.show_angle_guide = tk.BooleanVar(value=True)
        self.show_angle_guide.trace_add("write", lambda *ignore: self.update_manager.update())

        self.force_spacing = tk.BooleanVar(value=True)
        self.force_spacing.trace_add("write", lambda *ignore: self.update_manager.update_results())