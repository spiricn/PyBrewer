import logging

logger = logging.getLogger(__name__)


class TemperatureControlAlgorithm:

    # Temperature epsilon after which the relay will turn off
    EPSILON_C = 0.5

    def __init__(self, targetTemperatureCelsius):
        self._targetTemperatureCelsius = targetTemperatureCelsius

    def control(self, currentTemperatureC):
        if currentTemperatureC >= self._targetTemperatureCelsius:
            return True

        elif currentTemperatureC <= self._targetTemperatureCelsius - self.EPSILON_C:
            return False
