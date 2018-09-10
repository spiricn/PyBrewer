from threading import Thread
from time import sleep
import logging

from rpi.DS18B20.TemperatureSensor import TemperatureSensor
from brewer.Handler import Handler
from brewer.TemperatureControlAlgorithm import TemperatureControlAlgorithm

logger = logging.getLogger(__name__)


class TemperatureControlHandler(Handler):
    '''
    Reads temperatures from the sensors, and turns the relay on or off
    to control the temperature
    '''

    # Sleep time between loops
    SLEEP_TIME_SEC = 2.0

    # Sleep time if error happens
    ERROR_SLEEP_TIME_SEC = 4.0

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def onStart(self):
        # Relay controller pin
        self._relayPin = self.brewer.relayPin

        # Temperature sensor
        self._temperatureSensor = self.brewer.temperatureSensor

        # Controller running or not
        self._running = False

        # Target temperature we're trying to achieve
        self.targetTemperatureCelsius = self.brewer.config.targetTemperatureCelsius

        # Instantiate the algorithm
        self._controlAlgorithm = TemperatureControlAlgorithm(self.targetTemperatureCelsius)

        # Relay state
        self._currentState = None

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

        # Main loop
        while self._running:
            # Read the current temperature from probe
            currentTemperatureCelsius = self._temperatureSensor.getTemperatureCelsius()

            # Check if the read failed
            if currentTemperatureCelsius == TemperatureSensor.TEMP_INVALID_C:

                # Log the error only once (if the probe failed we can except an error every loop)
                if not errorLogged:
                    self.brewer.logError(__name__, 'failure reading temperature value, shutting off')

                    # Shut the relay off
                    self._setRelayState(False)

                    # Wait before trying again
                    sleep(self.ERROR_SLEEP_TIME_SEC)

                    # Don't log consecutive errors
                    errorLogged = True

                    continue

            # Log we resumed after read failures
            if errorLogged:
                self.brewer.logInfo(__name__, 'resuming'
                )

            errorLogged = False

            # Control the relasy
            self._setRelayState(self._controlAlgorithm.control(currentTemperatureCelsius))

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

        # Ignore same state changes
        if self._currentState != None and self._currentState == state:
            return

        # Change state
        logger.debug('setting relay state: ' + str(state))
        self._relayPin.setOutput(state)

        self._currentState = state

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

