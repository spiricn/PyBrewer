from collections import namedtuple
import time
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    '''
    Message type
    '''

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
        '''
        Handler name
        '''

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
        Get active messages created by this handler

        @return List of messages
        '''

        self.onGetMessages()

        return self._messages

    def onGetMessages(self):
        '''
        Called in the base class when @getMessages is called by the user
        '''

        pass

    def createMessage(self, messageType, message):
        '''
        Creates a new message.

        @param messageType Type of the message
        @param message Message body
        '''

        # Create message object
        message = Message(messageType, self.name, message, time.time())

        logger.debug('new message: ' + str(message))

        # Store it
        self._messages.append(message)

        return message

    def deleteMessage(self, message):
        '''
        Delete message

        @param message Message
        '''

        self._messages.remove(message)
