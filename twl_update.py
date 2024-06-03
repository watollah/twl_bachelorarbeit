from typing import List

class TwlWidget:
    
    def update(self):
        pass

class TwlUpdateManager:

    def __init__(self) -> None:
        self.paused: bool = False
        self.design_widgets: List[TwlWidget] = []
        self.result_widgets: List[TwlWidget] = []

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self.update()

    def update(self):
        if not self.paused:
            for widget in self.design_widgets: widget.update()

    def force_update(self):
        for widget in self.design_widgets: widget.update()

    def update_results(self):
        if not self.paused:
            for widget in self.result_widgets: widget.update()