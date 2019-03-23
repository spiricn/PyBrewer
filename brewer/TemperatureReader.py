from rpi.DS18B20.TemperatureSensor import TemperatureSensor
import time

from threading import Lock


class TemperatureReader():
    '''
    Class which handles multi-threaded temperature reads and caching
    '''

    # Maximum read frequency
    READ_CACHE_DURATION_SEC = 5

    # Number of attempts we'll make during temperature reads
    NUM_READ_RETRIES = 3

    # Sleep between read attempts
    RETRY_SLEEP_SEC = 0.5

    def __init__(self, deviceId, validTempRange, errorCallback=None):
        # Global lock
        self._lock = Lock()

        # Last read temperature time
        self._lastRead = time.time()

        # Cached temperature
        self._cachedTemp = None

        # Temperature sensor
        self._temperatureSensor = TemperatureSensor(deviceId)

        self._deviceId = deviceId

        self._validTemperatureRange = validTempRange

        self._errorCallback = errorCallback

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
            if self._cachedTemp == None or elapsedTime >= self.READ_CACHE_DURATION_SEC or not self._validTempC(self._cachedTemp):
                currentTempC = TemperatureSensor.TEMP_INVALID_C

                # Read current temperature (with retries)
                for i in range(self.NUM_READ_RETRIES):
                    currentTempC = self._temperatureSensor.getTemperatureCelsius()

                    # Read failed, so sleep & re-try
                    if not self._validTempC(currentTempC):
                        time.sleep(self.RETRY_SLEEP_SEC)
                        continue

                    # Read successful
                    break

                # Cache the value & remember when we got it
                self._cachedTemp = currentTempC
                self._lastRead = currentTime

                # Check if the temperature is in valid range
                if not self._validTempC(self._cachedTemp):
                    if self._errorCallback != None:
                        self._errorCallback('temperature read failure: ' + str(self._cachedTemp) + ' C / ' + self._deviceId)

                    self._cachedTemp = TemperatureSensor.TEMP_INVALID_C

            return self._cachedTemp

    def _validTempC(self, tempC):
        # Temperature is considered valid if it's in specified valid range
        minValidTempC, maxValidTempC = self._validTemperatureRange

        return tempC > minValidTempC and tempC < maxValidTempC

