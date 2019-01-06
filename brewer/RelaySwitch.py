from brewer.ASwitch import ASwitch
from rpi.IOPin import IOPin


class RelaySwitch(ASwitch):

    def __init__(self, name : str, color : str, pin : IOPin):
        ASwitch.__init__(self, name, color)

        self._pin = pin

    def isOn(self):
        return self._pin.output

    def setOn(self, on : bool):
        self._pin.setOutput(on)
