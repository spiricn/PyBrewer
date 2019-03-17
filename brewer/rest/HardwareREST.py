from brewer.HardwareHandler import HardwareHandler
from brewer.rest.BaseREST import BaseREST
from brewer.AComponent import ComponentType

class HardwareREST(BaseREST):
    '''
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'hardware/')

        self.addAPI('getComponents',
            self._getComponents,
'''
Get the list of hardware components available
'''
        )

        self.addAPI('readValue', self._readValue,
'''\
Read value of specific hardware component

@param id Component ID
'''
        )
        self.addAPI('toggleSwitch', self._toggleSwitch,
'''\
Toggle switch component on or off

@param id Switch ID
'''
        )

    def _getComponents(self, request):
        return [component.serialize() for component in self._brewer.getModule(HardwareHandler).getComponents()]

    def _toggleSwitch(self, request):
        component = self._findComponent(request)

        if component.componentType != ComponentType.SWITCH:
            raise RuntimeError('Unsupported component type: %r' % str(component.componentType))

        component.setOn(not component.isOn())

        return component.isOn()

    def _findComponent(self, request):
        componentId = request.params['id'][0]

        return self._brewer.getModule(HardwareHandler).findComponent(componentId)

    def _readValue(self, request):
        component = self._findComponent(request)

        value = None
        if component.componentType == ComponentType.SWITCH:
            value = 1.0 if component.isOn() else 0.0
        elif component.componentType == ComponentType.SENSOR:
            value = component.getValue()
        else:
            # TODO
            raise NotImplemented('unhandled component type: ' + str(component.componentType))

        return value