from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASensor(AComponent):

    def __init__(self, name : str, id : str, color : str, graph: bool):
        AComponent.__init__(self, name, id, ComponentType.SENSOR, color, graph)

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def isMalfunctioning(self):
        pass
