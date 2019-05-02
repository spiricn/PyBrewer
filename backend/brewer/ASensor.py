from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASensor(AComponent):
    '''
    Base class for all the sensor components
    '''

    def __init__(self, name : str, id : str, color : str, graph: bool):
        AComponent.__init__(self, name, id, ComponentType.SENSOR, color, graph)

    @abstractmethod
    def getValue(self):
        '''
        Read value
        '''

        pass

    @abstractmethod
    def isMalfunctioning(self):
        '''
        Check if the sensor is malfunctioning

        @return True if it is, False otherwise
        '''

        pass
