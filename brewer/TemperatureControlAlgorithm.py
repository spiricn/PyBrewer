import logging
from enum import Enum
import time

logger = logging.getLogger(__name__)


class TemperatureControlAlgorithm:
    '''
    Temperature control algorithm - decides when to turn the cooling on or off
    '''

    class Mode(Enum):
        HEAT = 1
        COOL = 2

    class State(Enum):
        # Thermal element active (cooling/heating)
        THERMAL_ACTIVE = 1

        # Idling
        IDLE = 2

    def __init__(self, targetTemperatureCelsius : float, mode, hysteresis : float):
        self._targetTemperatureCelsius = targetTemperatureCelsius

        self._mode = mode

        self._hysteresis = hysteresis

        self._state = None

    def startControl(self):
        self._setState(self.State.IDLE)

        return self._getState()

    def control(self, currentTemperatureC : float):
        if self._state == self.State.THERMAL_ACTIVE:
            # Heating/cooling is on, and we still didn't reach desired temperature
            if (self._mode == self.Mode.HEAT and currentTemperatureC <= self._targetTemperatureCelsius) \
                or (self._mode == self.Mode.COOL and currentTemperatureC >= self._targetTemperatureCelsius):
                # Just continue regulating temperature (both pump, and thermal element on)
                pass
            else:
                # We reached desired temperature, so go idle
                self._setState(self.State.IDLE)

        elif self._state == self.State.IDLE:
            # Detect when temperature dropped below/above acceptable
            if (self._mode == self.Mode.HEAT and currentTemperatureC <= self._targetTemperatureCelsius - self._hysteresis) \
                or (self._mode == self.Mode.COOL and currentTemperatureC >= self._targetTemperatureCelsius + self._hysteresis):

                # Start regulating temperature (both pump, and thermal element on)
                self._setState(self.State.THERMAL_ACTIVE)
            else:
                # Continue idling
                pass

        return self._getState()

    def _getState(self):
        if self._state == self.State.IDLE:
            return (False, True)

        elif self._state == self.State.THERMAL_ACTIVE:
            return (True, True)

        else:
            raise RuntimeError('Unexpected state %r' % str(self._state))

    def _setState(self, state):
        logger.debug('state: %s -> %s' % (str(self._state), str(state)))

        self._state = state
