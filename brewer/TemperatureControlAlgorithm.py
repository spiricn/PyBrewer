import logging
from enum import Enum
import time

logger = logging.getLogger(__name__)


class TemperatureControlAlgorithm:
    '''
    Temperature control algorithm - decides when to turn the cooling on or off
    '''

    DISPERSION_PERIOD_SEC = 30

    DISPERSION_DURATION = 10

    class Mode(Enum):
        HEAT = 1
        COOL = 2

    class State(Enum):
        # Thermal element active (cooling/heating)
        THERMAL_ACTIVE = 1

        # Idling
        IDLE = 2

        # Dispersing heat (fan/pump)
        THERMAL_DISPERSION = 3

    def __init__(self, targetTemperatureCelsius : float, mode, hysteresis : float):
        self._targetTemperatureCelsius = targetTemperatureCelsius
        self._mode = mode
        # On by default
        self._state = None

        self._setState(self.State.THERMAL_DISPERSION)

        self._hysteresis = hysteresis

        self._lastTime = time.time()

        self._dispersionSec = 0

    def control(self, currentTemperatureC : float):

        currTime = time.time()

        elapsedSec = currTime - self._lastTime

        self._lastTime = currTime

        if self._state == self.State.THERMAL_ACTIVE:
            # Heating/cooling is on, and we still didn't reach desired temperature
            if (self._mode == self.Mode.HEAT and currentTemperatureC <= self._targetTemperatureCelsius) \
                or (self._mode == self.Mode.COOL and currentTemperatureC >= self._targetTemperatureCelsius):
                # Just continue regulating temperature (both pump, and thermal element on)
                pass
            else:
                # We reached desired temperature, so start period dispersion
                self._setState(self.State.THERMAL_DISPERSION)
                self._dispersionSec = 0

        elif self._state in [self.State.THERMAL_DISPERSION, self.State.IDLE]:
            # Detect when temperature dropped below/above acceptable
            if (self._mode == self.Mode.HEAT and currentTemperatureC <= self._targetTemperatureCelsius - self._hysteresis) \
                or (self._mode == self.Mode.COOL and currentTemperatureC >= self._targetTemperatureCelsius + self._hysteresis):

                # Start regulating temperature (both pump, and thermal element on)
                self._setState(self.State.THERMAL_ACTIVE)
            else:
                self._dispersionSec += elapsedSec

                if self._state == self.State.THERMAL_DISPERSION:
                    if self._dispersionSec > self.DISPERSION_DURATION:
                        # Dispersion done, switch to idle
                        self._setState(self.State.IDLE)
                        self._dispersionSec = 0
                    else:
                        # Dispersion active, keep going
                        pass

                else:
                    if self._dispersionSec > self.DISPERSION_PERIOD_SEC:
                        # Start dispersion
                        self._setState(self.State.THERMAL_DISPERSION)
                        self._dispersionSec = 0
                    else:
                        # We're idle so keep everything off
                        pass

            return self._getState()

    def _getState(self):
        if self._state == self.State.IDLE:
            return (False, False)
        elif self._state == self.State.THERMAL_DISPERSION:
            return (False, True)
        elif self._state == self.State.THERMAL_ACTIVE:
            return (True, True)

    def _setState(self, state):
        logger.debug('state: %s -> %s' % (str(self._state), str(state)))

        self._state = state
