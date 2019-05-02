from ssc.servlets.RestServlet import RestHandler
from brewer.rest.BaseREST import BaseREST
from brewer.TemperatureControlHandler import TemperatureControlHandler

class TemperatureControlREST(BaseREST):
    '''
    Temperature controller handler REST API
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'temperatureControl/')

        self.addAPI('setTarget', self._setTargetTemp)

    def _setTargetTemp(self, request):
        '''
        Set target temperature the controller should achieve

        @param temperatuerC Target temperature in celsius
        '''

        targetTemperature = float(request.params['temperatureC'][0])

        self.brewer.getModule(TemperatureControlHandler).setTargetTemperature(targetTemperature)
