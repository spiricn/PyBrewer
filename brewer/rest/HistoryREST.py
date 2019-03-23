from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler
from brewer.HistoryHandler import HistoryHandler
from brewer.HardwareHandler import HardwareHandler, ComponentType
from brewer.rest.BaseREST import BaseREST

class HistoryREST(BaseREST):
    '''
    API used to fetch informatino from history hadnler
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'history/')

        self.addAPI('getSamples', self._getSamples)


    def _getSamples(self, request):
        return self._brewer.getModule(HistoryHandler).getSamples()