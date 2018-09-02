from brewer.Handler import Handler
from rpi.DS18B20.TemperatureSensor import TemperatureSensor
import time

from threading import Lock


class TemperatureReaderHandler(Handler):
    '''
    Class which handles multi-threaded temperature reads and caching
    '''

    # Maximum read frequency
    TEMP_READ_PERIOD = 2

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        # Global lock
        self._lock = Lock()

        # Last read temperature time
        self._lastRead = time.time()

        # Cached temperature
        self._cachedTemp = None

        # Temperature sensor
        self._temperatureSensor = TemperatureSensor(self.brewer.config.probeDeviceId)

        self._validTemperatureRange = self.brewer.config.validTemperatureRangeCelsius

    def getTemperatureCelsius(self):
        '''
        Get current temperature in a thread safe way
        '''

        with self._lock:
            # Get current time
            currentTime = time.time()

            # Get elapsed time since last read
            elapsedTime = currentTime - self._lastRead

            # Read new temperature if the value is stale or invalid
            if self._cachedTemp == None or elapsedTime >= self.TEMP_READ_PERIOD or not self._validTempC(self._cachedTemp):
                self._cachedTemp = self._temperatureSensor.getTemperatureCelsius()
                self._lastRead = currentTime

                # Check if the temperature is in valid range
                if not self._validTempC(self._cachedTemp):
                    self.brewer.logError(__name__, 'temperature read failure: ' + str(self._cachedTemp) + ' C')
                    self._cachedTemp = TemperatureSensor.TEMP_INVALID_C

            return self._cachedTemp

    def _validTempC(self, tempC):
        minValidTempC, maxValidTempC = self._validTemperatureRange

        return self._cachedTemp > minValidTempC and self._cachedTemp < maxValidTempC

