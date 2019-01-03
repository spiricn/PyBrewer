from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler
from brewer.HistoryHandler import HistoryHandler


class HistoryREST:
    '''
    API used to fetch informatino from history hadnler
    '''

    def __init__(self, brewer):
        self._brewer = brewer

    def getRestAPI(self):
        '''
        Create REST API
        '''

        return (
                # Fetch relay state
                RestHandler(
                    'history/get',
                    self._getHistory
                ),

                RestHandler(
                    'history/getRecords',
                    self._getRecords
                ),

        )

    def _getRecords(self, request):
        return (CODE_OK, MIME_JSON,
                            {'success' : True, 'res' : self._brewer.getModule(HistoryHandler).getRecords()})

    def _getHistory(self, request):
        res = {
            'temperature' : self._brewer.temperatureSensor.getTemperatureCelsius(),
            'target' : self._brewer.config.targetTemperatureCelsius,
            'relay' : self._brewer.relayPin.output
        }

        return (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : res})
