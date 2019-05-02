from brewer.HardwareHandler import HardwareHandler
from brewer.rest.BaseREST import BaseREST
from brewer.AComponent import ComponentType

class HardwareREST(BaseREST):
    '''
    Hardware handler REST API
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
        '''
        Get a list of components

        @return List of components
        '''

        return [component.serialize() for component in self._brewer.getModule(HardwareHandler).getComponents()]

    def _toggleSwitch(self, request):
        '''
        Toggle a switch on or off

        @param id Switch ID
        '''

        component = self._findComponent(request)

        if component.componentType != ComponentType.SWITCH:
            raise RuntimeError('Unsupported component type: %r' % str(component.componentType))

        component.setOn(not component.isOn())

        return component.isOn()

    def _findComponent(self, request):
        '''
        Find component from request

        @param request HTTP request

        @return Component if found, None otherwise
        '''

        componentId = request.params['id'][0]

        return self._brewer.getModule(HardwareHandler).findComponent(componentId)

    def _readValue(self, request):
        '''
        Read component value (e.g. sensor reading, or switch state)

        @param id Component ID

        @return Component value
        '''

        component = self._findComponent(request)

        value = None
        if component.componentType == ComponentType.SWITCH:
            # For switches convert state to 0 or 1
            value = 1.0 if component.isOn() else 0.0
        elif component.componentType == ComponentType.SENSOR:
            # Read actual value from sensor
            value = component.getValue()
        else:
            raise NotImplemented('unhandled component type: ' + str(component.componentType))

        return value