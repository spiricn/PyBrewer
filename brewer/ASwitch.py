from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASwitch(AComponent):

    def __init__(self, name : str, id : str, color : str, graph : bool):
        AComponent.__init__(self, name, id, ComponentType.SWITCH, color, graph)

    @abstractmethod
    def isOn(self):
        pass

    @abstractmethod
    def setOn(self, on : bool):
        pass

