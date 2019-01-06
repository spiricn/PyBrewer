from brewer.Handler import Handler
import logging
from brewer.AComponent import ComponentType

logger = logging.getLogger(__name__)


class HardwareHandler(Handler):

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        self._components = {}

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
