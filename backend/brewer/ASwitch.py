from brewer.AComponent import AComponent, ComponentType
from abc import abstractmethod


class ASwitch(AComponent):
    '''
    Base class for all the switch components
    '''

    def __init__(self, name : str, id : str, color : str, graph : bool):
        AComponent.__init__(self, name, id, ComponentType.SWITCH, color, graph)

    @abstractmethod
    def isOn(self):
        '''
        Check if the switch is on

        @return True if it's on, False otherwise
        '''

        pass

    @abstractmethod
    def setOn(self, on : bool):
        '''
        Turn swithc on or off

        @param on Switch state
        '''

        pass

