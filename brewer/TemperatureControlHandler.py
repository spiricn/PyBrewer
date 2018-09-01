from threading import Thread
from time import sleep
import logging
from brewer.LogHandler import LogHandler

from rpi.DS18B20.TemperatureSensor import TemperatureSensor
from brewer.Handler import Handler

logger = logging.getLogger(__name__)


class TemperatureControlHandler(Handler):
    '''
    Reads temperatures from the sensors, and turns the relay on or off
    to control the temperature
    '''

    # Temperature epsilon after which the relay will turn off
    EPSILON_C = 0.5

    # Sleep time between loops
    SLEEP_TIME_SEC = 2.0

    # Sleep time if error happens
    ERROR_SLEEP_TIME_SEC = 4.0

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        # Relay controller pin
        self._relayPin = self.brewer.relayPin

        # Temperature sensor
        self._temperatureSensor = self.brewer.temperatureSensor

        # Controller running or not
        self._running = False

        # Target temperature we're trying to achieve
        self.targetTemperatureCelsius = self.brewer.config.targetTemperatureCelsius

    def _run(self):
        '''
        Start the controller
        '''

        self.brewer.logInfo(__name__,
                            'control started: %.2f C' % self.targetTemperatureCelsius
        )

        # Turn the relay off
        self._setRelayState(False)

        errorLogged = False

        while self._running:
            # Read the current temperature from probe
            currentTemperatureCelsius = self._temperatureSensor.getTemperatureCelsius()

            if currentTemperatureCelsius == TemperatureSensor.TEMP_INVALID_C:

                if not errorLogged:
                    self.brewer.logError(__name__, 'failure reading temperature value, shutting off')

                    # Shut the relay off and wait before trying again
                    self._setRelayState(False)
                    sleep(self.ERROR_SLEEP_TIME_SEC)

                    errorLogged = True

                    continue

            if errorLogged:
                self.brewer.logInfo(__name__, 'resuming')

            errorLogged = False

            if currentTemperatureCelsius >= self.targetTemperatureCelsius:
                # Temperature above target, turn on cooling
                logger.debug('temperature above target: %.2f > %.2f',
                             currentTemperatureCelsius,
                             self.targetTemperatureCelsius)

                self._setRelayState(True)

            elif currentTemperatureCelsius <= self.targetTemperatureCelsius - self.EPSILON_C:
                # Temperature below target, turn off cooling
                logger.debug('temperature below target: %.2f < %.2f', currentTemperatureCelsius, self.targetTemperatureCelsius)

                self._setRelayState(False)

            # Wait a bit
            sleep(self.SLEEP_TIME_SEC)

        # Turn the relay off
        self._setRelayState(False)

        self.brewer.logInfo(__name__,
                            'control stopped'
        )

    def _setRelayState(self, state):
        '''
        Turns the relay on or off
        '''

        logger.debug('setting relay state: ' + str(state))
        self._relayPin.setOutput(state)

    def setState(self, state):
        '''
        Set temperature control state on or off
        '''

        if state and self._running:
            raise RuntimeError('Already running')
        elif not state and not self._running:
            raise RuntimeError('Already stopped')

        self._running = state

        if state:
            # Create the thread
            self._thread = Thread(target=self._run)
            self._thread.start()

        else:
            # Wait for thread to finish
            self._thread.join()
            self._thread = None

    def setTargetTemperature(self, targetTemperatureCelsius):
        '''
        Set the target temperature we're trying to achieve
        '''

        self.targetTemperatureCelsius = targetTemperatureCelsius

    @property
    def running(self):
        '''
        Is the controller running
        '''

        return self._running

