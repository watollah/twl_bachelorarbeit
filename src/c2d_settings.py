import tkinter as tk

from c2d_update import UpdateManager


class Settings:
    """Class that stores global settings used throughout the application."""

    def __init__(self, update_manager: UpdateManager) -> None:
        """Create an instance of Settings."""
        self.update_manager = update_manager

        self.show_node_labels = tk.BooleanVar(value=True)
        self.show_beam_labels = tk.BooleanVar(value=True)
        self.show_force_labels = tk.BooleanVar(value=True)
        self.show_support_labels = tk.BooleanVar(value=True)

        self.show_grid = tk.BooleanVar(value=True)
        self.grid_snap_radius = tk.IntVar(value=7)
        self.show_angle_guide = tk.BooleanVar(value=True)

        self.force_spacing = tk.BooleanVar(value=True)
        self.show_cremona_labels = tk.BooleanVar(value=True)