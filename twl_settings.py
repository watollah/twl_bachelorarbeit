from typing import Any

from twl_widget import *

class Settings:

    DIAGRAM_DISPLAY_NODE_LABELS = False
    DIAGRAM_DISPLAY_FORCE_LABELS = False
    DIAGRAM_DISPLAY_BEAM_LABELS = False
    DIAGRAM_DISPLAY_SUPPORT_LABELS = False
    DIAGRAM_LABEL_SIZE = 12

    def __init__(self, update_manager: TwlUpdateManager) -> None:
        self.update_manager = update_manager

    def __setattr__(self, name: str, value: Any) -> None:
        """Automatically refresh all ui elements whenever a setting is changed."""
        super().__setattr__(name, value)
        self.update_manager.update()