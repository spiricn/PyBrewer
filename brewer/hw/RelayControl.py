

class RelayControl:
    '''
    Controls the relay and reads its state
    '''

    def __init__(self):
        self._state = False

    def getState(self):
        '''
        Get current relay state
        '''

        return self._state

    def setState(self, state):
        '''
        Set relay state
        '''

        # TODO Implement
        self._state = state
