from collections import namedtuple
import time
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    INFO = 1
    WARNING = 2

Message = namedtuple('Message', 'type, title, message, timestamp')

class Handler:
    '''
    Base handler class all handlers should inherit
    '''

    def __init__(self, brewer, name):
        self._brewer = brewer
        self._messages = []
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def brewer(self):
        '''
        Parent brewer instance
        '''

        return self._brewer

    def update(self, elapsedTime):
        '''
        Called periodically on all handlers.

        @param elapsedTime: Time elapsed since last update call
        '''

        pass

    def onStart(self):
        '''
        Called on after application has been initialized
        '''

        pass

    def onStop(self):
        '''
        Called after application has been stopped
        '''

        pass

    def getMessages(self):
        '''
        TODO
        '''

        self.onGetMessages()

        return self._messages

    def onGetMessages(self):
        '''
        TODO
        '''

        pass

    def createMessage(self, messageType, message):
        '''
        TODO
        '''

        message = Message(messageType, self.name, message, time.time())

        logger.debug('new message: ' + str(message))

        self._messages.append(message)

        return message

    def deleteMessage(self, message):
        '''
        TODO
        '''

        self._messages.remove(message)
