from enum import Enum


class ComponentType(Enum):
    SWITCH = 1
    SENSOR = 2
    TEMPERATURE_CONTROLLER = 3


class AComponent:

    def __init__(self, name : str, componentType : ComponentType, color : str):
        self._name = name
        self._color = color
        self._componentType = componentType

    @property
    def componentType(self):
        return self._componentType

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

