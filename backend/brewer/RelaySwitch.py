from brewer.ASwitch import ASwitch
from rpi.IOPin import IOPin


class RelaySwitch(ASwitch):

    def __init__(self, name : str, id : str, color : str, pin : IOPin, graph : bool):
        ASwitch.__init__(self, name, id, color, graph)

        self._pin = pin

    def isOn(self):
        return self._pin.output

    def setOn(self, on : bool):
        self._pin.setOutput(on)
