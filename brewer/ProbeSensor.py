from brewer.ASensor import ASensor
from brewer.TemperatureReader import TemperatureReader


class ProbeSensor(ASensor):

    def __init__(self, name : str, id : str, color : str, temperatureReader : TemperatureReader, graph : bool):
        ASensor.__init__(self, name, id, color, graph)

        self._reader = temperatureReader

    def getValue(self):
        return self._reader.getTemperatureCelsius()

