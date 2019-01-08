from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASensor(AComponent):

    def __init__(self, name : str, color : str, graph: bool):
        AComponent.__init__(self, name, ComponentType.SENSOR, color, graph)

    @abstractmethod
    def getValue(self):
        pass
