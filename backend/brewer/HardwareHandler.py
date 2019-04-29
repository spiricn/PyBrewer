from brewer.Handler import Handler
import logging
from brewer.AComponent import ComponentType
import re
from brewer.Handler import MessageType

logger = logging.getLogger(__name__)


class HardwareHandler(Handler):

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

        self._components = {}
        self._errors = {}

    def addCustom(self, component):
        self._addComponent(component)

    def getComponents(self, componentType : ComponentType=None):
        components = [component for component in self._components.values() if (componentType == None or component.componentType == componentType)]

        return sorted(components, key=lambda x: x.componentType.value)

    def findComponentByName(self, name : str):
        for component in self._components.values():
            if component.name == name:
                return component
        return None

    def findComponent(self, componentId : str):
        if componentId in self._components:
            return self._components[componentId]

        return None

    def _addComponent(self, component):
        if component.name in self._components:
            raise RuntimeError('Component with name %r already exists' % component.name)

        if not re.compile('^[a-z0-9A-Z_]+$').match(component.id):
            raise RuntimeError('Invalid component ID: %r' % component.id)

        if component.id in self._components:
            raise RuntimeError('Component with ID %r already exists' % component.id)

        self._components[component.id] = component

        logger.debug('new component: ' + str(component))

    def onGetMessages(self):
        # Go trough all the sensors
        for sensor in self.getComponents(ComponentType.SENSOR):
            # If it's malfunctioning, create a message
            if sensor.isMalfunctioning() and sensor.id not in self._errors:
                self._errors[sensor.id] = self.createMessage(MessageType.WARNING, "Sensor malfunctioning: %r" % sensor.id)

            # If not delete, the message if it exsits
            elif not sensor.isMalfunctioning() and sensor.id in self._errors:
                self.deleteMessage(self._errors[sensor.id])
                del self._errors[sensor.id]
