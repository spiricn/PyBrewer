class Handler:
    def __init__(self, brewer):
        self._brewer = brewer

    @property
    def brewer(self):
        return self._brewer

    def update(self, elapsedTime):
        raise NotImplementedError('Not implemented')

    def onStart(self):
        raise NotImplementedError('Not implemented')

    def onStop(self):
        raise NotImplementedError('Not implemented')
