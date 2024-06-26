import tkinter as tk

from c2d_update import UpdateManager
from c2d_settings import Settings
from c2d_components import Model
from c2d_solver import Solver


class TwlApp():

    _saved_state = None
    _changed_state = None

    _update_manager = None
    _settings = None
    _model = None
    _solver = None

    @staticmethod
    def saved_state():
        if TwlApp._saved_state is None:
            TwlApp._saved_state = tk.BooleanVar()
        return TwlApp._saved_state

    @staticmethod
    def changed_state():
        if TwlApp._changed_state is None:
            TwlApp._changed_state = tk.BooleanVar()
        return TwlApp._changed_state


    @staticmethod
    def update_manager():
        if TwlApp._update_manager is None:
            TwlApp._update_manager = UpdateManager()
        return TwlApp._update_manager

    @staticmethod
    def settings():
        if TwlApp._settings is None:
            TwlApp._settings = Settings(TwlApp.update_manager())
        return TwlApp._settings

    @staticmethod
    def model():
        if TwlApp._model is None:
            TwlApp._model = Model(TwlApp.update_manager())
        return TwlApp._model

    @staticmethod
    def solver():
        if TwlApp._solver is None:
            TwlApp._solver = Solver(TwlApp.model())
        return TwlApp._solver