from twl_components import *
from twl_settings import *
from twl_solver import *

class TwlApp:

    _update_manager = None
    _settings = None
    _model = None
    _solver = None

    @staticmethod
    def update_manager():
        if TwlApp._update_manager is None:
            TwlApp._update_manager = TwlUpdateManager()
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
            TwlApp._solver = TwlSolver(TwlApp.model())
        return TwlApp._solver