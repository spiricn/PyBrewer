from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler


class LogREST:
    '''
    Rest API used to control the log handler
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
                    'log/clear',
                    lambda request: (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : self._brewer.getModule(LogHandler).clear()})
                ),

        )
