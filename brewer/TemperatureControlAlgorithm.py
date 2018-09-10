import logging

logger = logging.getLogger(__name__)


class TemperatureControlAlgorithm:
    '''
    Temperature control algorithm - decides when to turn the cooling on or off
    '''

    # Temperature epsilon after which the relay will turn off
    EPSILON_C = 0.5

    def __init__(self, targetTemperatureCelsius):
        self._targetTemperatureCelsius = targetTemperatureCelsius

    def control(self, currentTemperatureC):
        if currentTemperatureC >= self._targetTemperatureCelsius:
            # Turn the cooling on if temperature is above target
            return True

        elif currentTemperatureC <= self._targetTemperatureCelsius - self.EPSILON_C:
            # Turn cooling off if temperature is below target
            return False
