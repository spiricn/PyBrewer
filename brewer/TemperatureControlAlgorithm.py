import logging

logger = logging.getLogger(__name__)


class TemperatureControlAlgorithm:
    '''
    Temperature control algorithm - decides when to turn the cooling on or off
    '''

    MODE_HEAT, \
    MODE_COOL = range(2)

    def __init__(self, targetTemperatureCelsius, mode, hysteresis):
        self._targetTemperatureCelsius = targetTemperatureCelsius
        self._mode = mode
        # On by default
        self._on = True

        self._hysteresis = hysteresis

    def control(self, currentTemperatureC):
        if self._on:
            # Heating/cooling is on, and we still didn't reach desired temperature
            if (self._mode == self.MODE_HEAT and currentTemperatureC <= self._targetTemperatureCelsius) \
                or (self._mode == self.MODE_COOL and currentTemperatureC >= self._targetTemperatureCelsius):
                # Just continue regulating temperature
                return True
            else:
                # We reached desired temperature, so turn off
                self._on = False
                return False

        else:
            # Detect when temperature dropped below/above acceptable
            if (self._mode == self.MODE_HEAT and currentTemperatureC <= self._targetTemperatureCelsius - self._hysteresis) \
                or (self._mode == self.MODE_COOL and currentTemperatureC >= self._targetTemperatureCelsius + self._hysteresis):

                self._on = True
                return True
            else:
                return False
