from brewer.ASensor import ASensor
from brewer.TemperatureReader import TemperatureReader
import time

class ProbeSensor(ASensor):
    '''
    Hardware DS18B20 probe sensor implementation
    '''

    # No errors for one day to be considered working correctly
    MALFUNCTIONING_DELTA_SEC = 24 * 60 * 60

    def __init__(self, name : str, id : str, color : str, temperatureReader : TemperatureReader, graph : bool):
        ASensor.__init__(self, name, id, color, graph)

        self._reader = temperatureReader

    def getValue(self):
        return self._reader.getTemperatureCelsius()

    def isMalfunctioning(self):
        secSinceLastError = time.time() - self._reader.lastError

        return secSinceLastError <= self.MALFUNCTIONING_DELTA_SEC
