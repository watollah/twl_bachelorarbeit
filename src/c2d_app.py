import tkinter as tk

from c2d_update import UpdateManager
from c2d_settings import Settings
from c2d_components import Model
from c2d_solver import Solver


class TwlApp():
    """Makes shared data accessible all over the application."""

    _saved_state = None
    _changed_state = None

    _update_manager = None
    _settings = None
    _model = None
    _solver = None

    @staticmethod
    def saved_state():
        """Saved state of the project. Is set to False when a change is made to the model. 
        Is set to True whenever the project is saved."""
        if TwlApp._saved_state is None:
            TwlApp._saved_state = tk.BooleanVar()
        return TwlApp._saved_state

    @staticmethod
    def changed_state():
        """Changed state of the project. Is set to True when a change is made to the model. 
        Is set to False whenever the model is solved by TwlSolver
        (whenever the user switches to Cremona or Result tab)."""
        if TwlApp._changed_state is None:
            TwlApp._changed_state = tk.BooleanVar()
        return TwlApp._changed_state


    @staticmethod
    def update_manager():
        """Makes shared UpdateManager instance accessible globally."""
        if TwlApp._update_manager is None:
            TwlApp._update_manager = UpdateManager()
        return TwlApp._update_manager

    @staticmethod
    def settings():
        """Makes shared Settings instance accessible globally."""
        if TwlApp._settings is None:
            TwlApp._settings = Settings(TwlApp.update_manager())
        return TwlApp._settings

    @staticmethod
    def model():
        """Makes shared Model instance accessible globally."""
        if TwlApp._model is None:
            TwlApp._model = Model(TwlApp.update_manager())
        return TwlApp._model

    @staticmethod
    def solver():
        """Makes shared Solver instance accessible globally."""
        if TwlApp._solver is None:
            TwlApp._solver = Solver(TwlApp.model())
        return TwlApp._solver