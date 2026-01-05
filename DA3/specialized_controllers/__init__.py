"""
Специализированные контроллеры для управления разными аспектами приложения
"""
from .form_controller import FormController
from .point_controller import PointController
from .parameter_controller import ParameterController
from .pazzle_controller import PazzleController
from .step_controller import StepController

__all__ = [
    'FormController',
    'PointController',
    'ParameterController',
    'PazzleController',
    'StepController'
]