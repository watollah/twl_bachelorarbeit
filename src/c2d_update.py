from abc import abstractmethod


class Observer:
    """Class (for example a ui widget) that gets registered with an Observable class. Gets notified when it has to update."""

    @abstractmethod
    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update this Observer to show changes. Optionally provided ids for more precise updating."""
        pass


class UpdateManager:
    """Class that keeps track of a list of Observers that get can be notified to reflect changes."""

    def __init__(self) -> None:
        """Create an instance of UpdateManager."""
        self._paused: bool = False
        self._observers: list[Observer] = []

    def pause_observing(self):
        """Pause the UpdateManager from notifying its Observers for updates. Resume with UpdateManager.resume()."""
        self._paused = True

    def resume_observing(self):
        """Resume notifying Observers for updates."""
        self._paused = False
        self.notify_observers()

    def register_observer(self, observer: Observer):
        self._observers.append(observer)

    def notify_observers(self, component_id: str="", attribute_id: str=""):
        """Notify Observers to update themselves. Doesn't do anything while the UpdateManager is paused."""
        if not self._paused:
            for observer in self._observers: observer.update_observer(component_id, attribute_id)