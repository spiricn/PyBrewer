class Handler:

    def __init__(self, brewer):
        self._brewer = brewer

    @property
    def brewer(self):
        return self._brewer

    def update(self, elapsedTime):
        pass

    def onStart(self):
        pass

    def onStop(self):
        pass

