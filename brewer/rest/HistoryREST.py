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
                RestHandler(
                    'history/getSamples',
                    self._getSamples
                ),

                RestHandler(
                    'history/getNumSamples',
                    self._getNumSamples
                ),

                RestHandler(
                    'history/getComponents',
                    self._getComponents
                ),

                RestHandler(
                    'history/getRecords',
                    self._getRecords
                ),

        )

    def _getSamples(self, request):
        startIndex = int(request.params['startIndex'][0])
        endIndex = int(request.params['endIndex'][0])
        record = request.params['record'][0]

        return (CODE_OK, MIME_JSON,
                            {'success' : True, 'res' : self._brewer.getModule(HistoryHandler).getSamples(record, startIndex, endIndex)})

    def _getNumSamples(self, request):
        record = request.params['record'][0]

        component = request.params['component'][0]

        return (CODE_OK, MIME_JSON,
                            {'success' : True, 'res' : self._brewer.getModule(HistoryHandler).getNumSamples(record, component)})

    def _getComponents(self, request):
        record = request.params['record'][0]

        return (CODE_OK, MIME_JSON, {'success' : True, 'res' : self._brewer.getModule(HistoryHandler).getComponents(record)})

    def _getRecords(self, request):
        return (CODE_OK, MIME_JSON,
                            {'success' : True, 'res' : self._brewer.getModule(HistoryHandler).getRecords()})

    def _getHistory(self, request):
        res = {}

        for component in self._brewer.getModule(HardwareHandler).getComponents():

            if component.componentType == ComponentType.SENSOR:
                value = component.getValue()
            elif component.componentType == ComponentType.SWITCH:
                value = 1.0 if component.isOn() else 0.0

            res[component.name] = {'value' : value, 'type' : component.componentType.name}

        return (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : res})
