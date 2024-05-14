from typing import List

class TwlWidget:
    
    def update(self):
        pass

class TwlUpdateManager:

    def __init__(self) -> None:
        self.widgets: List[TwlWidget] = []

    def update(self):
        for widget in self.widgets: widget.update()