from brewer.ASwitch import ASwitch


class RelaySwitch(ASwitch):
    '''
    Hardware relay switch implementation controled by a GPIO pin
    '''

    def __init__(self, name : str, id : str, color : str, pin, graph : bool):
        ASwitch.__init__(self, name, id, color, graph)

        self._pin = pin

    def isOn(self):
        return self._pin.output

    def setOn(self, on : bool):
        self._pin.setOutput(on)
