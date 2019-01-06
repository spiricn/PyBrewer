from threading import Thread
from time import sleep
import logging

from rpi.DS18B20.TemperatureSensor import TemperatureSensor
from brewer.Handler import Handler
from brewer.TemperatureControlAlgorithm import TemperatureControlAlgorithm
from brewer.SettingsHandler import SettingsHandler
from brewer.HardwareHandler import HardwareHandler, ComponentType

logger = logging.getLogger(__name__)


class TargetTemperatureSensor:

    def __init__(self, controlHandler):
        self._controlHandler = controlHandler

    @property
    def color(self):
        return "rgb(190, 190, 190)"

    @property
    def name(self):
        return "Target Temperature"

    @property
    def componentType(self):
        return ComponentType.SENSOR

    @property
    def reader(self):
        return self

    def getTemperatureCelsius(self):
        return self._controlHandler.targetTemperatureCelsius


class TemperatureControlHandler(Handler):
    '''
    Reads temperatures from the sensors, and turns the relay on or off
    to control the temperature
    '''

    # Sleep time between loops
    SLEEP_TIME_SEC = 2.0

    # Sleep time if error happens
    ERROR_SLEEP_TIME_SEC = 4.0

    #
    STG_KEY_STATE = 'TEMPERATURE_CONTROL_ON'

    #
    STG_KEY_MODE = 'TEMPERATURE_CONTROL_MODE'

    #
    STG_KEY_TARGET_TEMP = 'TEMPERATURE_CONTROL_TARGET'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def onStart(self):
        self.brewer.getModule(HardwareHandler).addCustom(self)
        self.brewer.getModule(HardwareHandler).addCustom(TargetTemperatureSensor(self))

        # Relay controller pin
        self._relayPin = self.brewer.getModule(HardwareHandler).findComponent(self.brewer.config.thermalSwitch)

        if not self._relayPin:
            raise RuntimeError("Unable to find switch with name %r", str(self.brewer.config.thermalSwitch))

        self._relayPin = self._relayPin.pin

        # Temperature sensor
        self._externalSensor = self.brewer.getModule(HardwareHandler).findComponent(self.brewer.config.externalSensor)
        if not self._externalSensor:
            raise RuntimeError("Unable to find sensor with name %r", str(self.brewer.config.externalSensor))
        self._externalSensor = self._externalSensor.reader

        # Controller running or not
        self._running = False

        # Target temperature we're trying to achieve
        self.targetTemperatureCelsius = self.brewer.config.targetTemperatureCelsius

        modeMap = {
            'MODE_HEAT' : TemperatureControlAlgorithm.MODE_HEAT,
            'MODE_COOL' : TemperatureControlAlgorithm.MODE_COOL,
        }

        modeSetting = self.brewer.getModule(SettingsHandler).getString(self.STG_KEY_MODE,
                                                                       self.brewer.config.mode)
        self._mode = modeMap[modeSetting]

        targetCelsius = self.brewer.getModule(SettingsHandler).getFloat(self.STG_KEY_TARGET_TEMP, self.targetTemperatureCelsius)

        # Instantiate the algorithm
        self._controlAlgorithm = TemperatureControlAlgorithm(targetCelsius,
                                                             self._mode,
                                                             self.brewer.config.temperatureHysteresisC)

        # Relay state
        self._currentState = None

        if self.brewer.getModule(SettingsHandler).getBoolean(self.STG_KEY_STATE):
            logger.debug('restoring state')
            self.setState(True, rememberChoice=False)

    def onStop(self):
        # Stop the control (and don't store the choice in DB)
        if self._running:
            self.setState(False, rememberChoice=False)

    @property
    def color(self):
        return 'rgb(128, 128, 128)'

    def _run(self):
        '''
        Start the controller
        '''

        self.brewer.logInfo(__name__,
                            'control started: %.2f C (mode=%d)' % (self.targetTemperatureCelsius, self._mode)
        )

        # Turn the relay off
        self._setRelayState(False)

        errorLogged = False

        # Main loop
        while self._running:
            # Read the current temperature from probe
            currentTemperatureCelsius = self._externalSensor.getTemperatureCelsius()

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

    @property
    def componentType(self):
        return ComponentType.SWITCH

    @property
    def name(self):
        return "TemperatureController"

    @property
    def pin(self):
        return self

    @property
    def output(self):
        return self._running

    def setOutput(self, state):
        self.setState(state)

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

    def setState(self, state, rememberChoice=True):
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

        # Remember our state
        if rememberChoice:
            self.brewer.getModule(SettingsHandler).putBoolean(self.STG_KEY_STATE, state)

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

