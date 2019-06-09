class MockIOPin:
    def __init__(self, number):
        self._number = number
        self._output = False

    @staticmethod
    def init():
        pass

    @property
    def output(self):
        return self._output

    @staticmethod
    def createOutput(number):
        return MockIOPin(number)

    def setOutput(self, output):
        self._output = output
