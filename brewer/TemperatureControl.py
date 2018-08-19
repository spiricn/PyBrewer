from threading import Thread
from time import sleep
import logging

logger = logging.getLogger(__name__)


class TemperatureControl():
    '''
    Reads temperatures from the sensors, and turns the relay on or off
    to control the temperature
    '''

    # Temperature epsilon after which the relay will turn off
    EPSILON_C = 0.5

    # Sleep time between loops
    SLEEP_TIME_SEC = 2.0

    def __init__(self, relayControl, temperatureSensor, targetTemperatureCelsius):

        # Relay controller
        self._relayControl = relayControl

        # Temperature sensor
        self._temperatureSensor = temperatureSensor

        # Controller running or not
        self._running = False

        # Target temperature we're trying to achieve
        self.targetTemperatureCelsius = targetTemperatureCelsius

    def _run(self):
        '''
        Start the controller
        '''

        logger.debug('start control: %.2f' % self.targetTemperatureCelsius)

        # Turn the relay off
        self._setRelayState(False)

        while self._running:
            # Read the current temperature from probe
            currentTemperatureCelsius = self._temperatureSensor.getTemperatureCelsius()

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

            # Wait abit
            sleep(self.SLEEP_TIME_SEC)

        # Turn the relay off
        self._setRelayState(False)

        logger.debug('stop control')

    def _setRelayState(self, state):
        '''
        Turns the relay on or off
        '''

        logger.debug('setting relay state: ' + str(state))
        self._relayControl.setState(state)

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

