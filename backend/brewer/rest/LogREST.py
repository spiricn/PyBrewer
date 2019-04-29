from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler
from brewer.rest.BaseREST import BaseREST


class LogREST(BaseREST):
    '''
    Rest API used to control the log handler
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'log/')


        self.addAPI('clear',
            lambda request: self._brewer.getModule(LogHandler).clear()
        )

        self.addAPI('test',
            lambda request: self._brewer.getModule(LogHandler).pushNotifications.sendNotification('PyBrewer', 'This is a test message.')
        )

        self.addAPI('getLogs',
            lambda request: [entry.serialize() for entry in self._brewer.getModule(LogHandler).getLogs()]
        )

        self.addAPI('getMessages', self._getMessages)

    def _getMessages(self, request):
        messages = self._brewer.getMessages()

        serializedMessages = []

        # Convert messages into dictionaries so that they may be serialized to JSON automatically
        for message in messages:
            dictMessage = message._asdict()

            # Convert type to string
            dictMessage['type'] = dictMessage['type'].name

            serializedMessages.append(dictMessage)

        return dictMessage