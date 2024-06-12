class TwlWidget:
    
    def update(self):
        pass

class UpdateManager:

    def __init__(self) -> None:
        self.paused: bool = False
        self.design_widgets: list[TwlWidget] = []
        self.result_widgets: list[TwlWidget] = []

    def is_active(self) -> bool:
        return True

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