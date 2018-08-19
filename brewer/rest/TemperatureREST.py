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
                    lambda: (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : self._brewer.temperatureSensor.getTemperatureCelsius()})
                ),

                # Toggle temperature controller
                RestHandler(
                    'temperature/controller/toggle',
                    self.toggleControllerState
                ),
        )

    def toggleControllerState(self, **kwargs):
        '''
        Toggles temperature control
        '''

        self._brewer.temperatureControl.setState(
            not self._brewer.temperatureControl.running)

        return (CODE_OK, MIME_JSON, {'success' : True})
