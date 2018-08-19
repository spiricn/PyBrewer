from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST


class RelayREST:
    '''
    Rest API used to control the relay
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
                    'relay/get_state',
                    lambda: (CODE_OK, MIME_JSON,
                                {'success' : True, 'res' : self._brewer.relayControl.getState()})
                ),

                # Toggle relay state
                RestHandler(
                    'relay/toggle',
                    self.toggle
                ),
        )

    def toggle(self, **kwargs):
        '''
        Toggle the relay state
        '''

        if self._brewer.temperatureControl.running:
            return (CODE_BAD_REQUEST, MIME_JSON, {'success' : False, 'message' : 'Automatic temperature controller running'})

        self._brewer.relayControl.setState(not self._brewer.relayControl.getState())

        return (CODE_OK, MIME_JSON, {'success' : True})