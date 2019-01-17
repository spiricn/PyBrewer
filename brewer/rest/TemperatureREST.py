from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST


class TemperatureREST:
    '''
    Rest API used to read temperature from probes
    '''

    def __init__(self, brewer):
        self._brewer = brewer

    def getRestAPI(self):
        return (
                # Get temperature reading
                RestHandler(
                    'temperature/get',
                    lambda request: (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : self._brewer.temperatureSensor.getTemperatureCelsius()})
                ),

                # Toggle temperature controller
                RestHandler(
                    'temperature/controller/toggle',
                    self.toggleControllerState
                ),

                # Set target temperature
                RestHandler(
                    'temperature/controller/setTarget',
                    self._setTargetTemp
                ),
        )

    def _setTargetTemp(self, request):
        targetTemperature = float(request.params['temperatureC'][0])

        self._brewer.temperatureControl.setTargetTemperature(targetTemperature)

        return (CODE_OK, MIME_JSON, {'success' : True})

    def toggleControllerState(self, request):
        '''
        Toggles temperature control
        '''

        self._brewer.temperatureControl.setState(
            not self._brewer.temperatureControl.running)

        return (CODE_OK, MIME_JSON, {'success' : True})
