class Handler:
    '''
    Base handler class all handlers should inherit
    '''

    def __init__(self, brewer):
        self._brewer = brewer

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

