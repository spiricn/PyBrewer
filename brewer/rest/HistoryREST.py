from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler
from brewer.HistoryHandler import HistoryHandler
from brewer.HardwareHandler import HardwareHandler, ComponentType


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
        res = {}

        for component in self._brewer.getModule(HardwareHandler).getComponents():

            if component.componentType == ComponentType.SENSOR:
                value = component.reader.getTemperatureCelsius()
            elif component.componentType == ComponentType.SWITCH:
                value = 1.0 if component.pin.output else 0.0

            res[component.name] = {'value' : value, 'type' : component.componentType.name}

        return (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : res})
