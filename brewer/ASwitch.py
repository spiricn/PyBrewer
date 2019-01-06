from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASwitch(AComponent):

    def __init__(self, name, color):
        AComponent.__init__(self, name, ComponentType.SWITCH, color)

    @abstractmethod
    def isOn(self):
        pass

    @abstractmethod
    def setOn(self, on : bool):
        pass

