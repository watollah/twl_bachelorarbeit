from typing import Any
from tkinter import BooleanVar

from twl_widget import *

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