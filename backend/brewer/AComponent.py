from enum import Enum


class ComponentType(Enum):
    '''
    Component ID
    '''

    # Toggleable binary switch
    SWITCH = 1

    # Sensor which reads values
    SENSOR = 2

    # Virtual temperature controller component
    TEMPERATURE_CONTROLLER = 3

class AComponent:
    '''
    Base hardware component class
    '''

    def __init__(self, name : str, componentId : str, componentType : ComponentType, color : str, graph : bool):
        self._name = name

        self._color = color

        self._componentType = componentType

        self._graph = graph

        self._id = componentId

    @property
    def id(self):
        '''
        Unique ID
        '''

        return self._id

    @property
    def graph(self):
        '''
        Indicates if the component should be graphed out or not
        '''

        return self._graph

    @property
    def componentType(self):
        '''
        Component type
        '''

        return self._componentType

    @property
    def name(self):
        '''
        Component name
        '''

        return self._name

    @property
    def color(self):
        '''
        Component color (used manily for UI)
        '''

        return self._color

    def serialize(self):
        return {
            'id' : self.id,
            'graph' : self.graph,
            'componentType' : self.componentType.name,
            'name' : self.name,
            'color' : self.color
        }
