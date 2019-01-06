from collections import namedtuple
from rpi.IOPin import IOPin
from brewer.TemperatureReader import TemperatureReader
from brewer.Handler import Handler
import logging
from enum import Enum

Switch = namedtuple('Switch', 'name, componentType, pin, color')
Sensor = namedtuple('Sensor', 'name, componentType, reader, color')

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    SWITCH = 1
    SENSOR = 2
    TEMPERATURE_CONTROLLER = 3

class HardwareHandler(Handler):

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        self._components = {}

    def addSwitch(self, name : str, pinNumber : int, color : str):
        self._addComponent(
            Switch(name, ComponentType.SWITCH, IOPin.createOutput(pinNumber), color)
        )

    def addSensor(self, name : str, deviceId : str, color : str):
        self._addComponent(
            Sensor(name, ComponentType.SENSOR, 
                   TemperatureReader(deviceId, self.brewer.config.validTemperatureRangeCelsius, lambda errorMessage: self.brewer.logError(errorMessage)),
                   color
                   )
        )

    def addCustom(self, component):
        self._addComponent(component)

    def getComponents(self, componentType : ComponentType=None):
        return [component for component in self._components.values() if (componentType == None or component.componentType == componentType)]

    def findComponent(self, name : str):
        if name in self._components:
            return self._components[name]

        return None

    def _addComponent(self, component):
        if component.name in self._components:
            raise RuntimeError('Component with name %r already exists' % component.name)

        self._components[component.name] = component

        logger.debug('new component: ' + str(component))
