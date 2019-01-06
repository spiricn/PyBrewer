from threading import Thread
from time import sleep
import logging

from rpi.DS18B20.TemperatureSensor import TemperatureSensor
from brewer.Handler import Handler
from brewer.TemperatureControlAlgorithm import TemperatureControlAlgorithm
from brewer.SettingsHandler import SettingsHandler
from brewer.HardwareHandler import HardwareHandler
from brewer.ASensor import ASensor
from brewer.ASwitch import ASwitch

logger = logging.getLogger(__name__)


class TargetTemperatureSensor(ASensor):

    def __init__(self, controlHandler):
        ASensor.__init__(self, "Target Temperature", "rgb(190, 190, 190)")

        self._controlHandler = controlHandler

    def getValue(self):
        return self._controlHandler.targetTemperatureCelsius


class TemperatureControlSwitch(ASwitch):

    def __init__(self, controlHandler):
        ASwitch.__init__(self, "TemperatureController", 'rgb(128, 128, 128)')

        self._controlHandler = controlHandler

    def isOn(self):
        return self._controlHandler.running

    def setOn(self, on : bool):
        self._controlHandler.setState(on, rememberChoice=True)


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
        # Add virtual switch, used to turn the controller on/off
        self.brewer.getModule(HardwareHandler).addCustom(TemperatureControlSwitch(self))

        # Add virtual sensor, used to monitor target temperature
        self.brewer.getModule(HardwareHandler).addCustom(TargetTemperatureSensor(self))

        # Relay controller pin
        self._thermalSwitch = self.brewer.getModule(HardwareHandler).findComponent(self.brewer.config.thermalSwitch)

        if not self._thermalSwitch:
            raise RuntimeError("Unable to find switch with name %r", str(self.brewer.config.thermalSwitch))

        # Find pump switch
        self._pumpSwitch = self.brewer.getModule(HardwareHandler).findComponent(self.brewer.config.pumpSwitch)

        if not self._pumpSwitch:
            raise RuntimeError("Unable to find switch with name %r", str(self.brewer.config.pumpSwitch))

        # Temperature sensor
        self._externalSensor = self.brewer.getModule(HardwareHandler).findComponent(self.brewer.config.externalSensor)
        if not self._externalSensor:
            raise RuntimeError("Unable to find sensor with name %r", str(self.brewer.config.externalSensor))

        # Controller running or not
        self._running = False

        # Target temperature we're trying to achieve
        self.targetTemperatureCelsius = self.brewer.config.targetTemperatureCelsius

        modeMap = {
            'MODE_HEAT' : TemperatureControlAlgorithm.Mode.HEAT,
            'MODE_COOL' : TemperatureControlAlgorithm.Mode.COOL,
        }

        modeSetting = self.brewer.getModule(SettingsHandler).getString(self.STG_KEY_MODE,
                                                                       self.brewer.config.mode)
        self._mode = modeMap[modeSetting]

        targetCelsius = self.brewer.getModule(SettingsHandler).getFloat(self.STG_KEY_TARGET_TEMP, self.targetTemperatureCelsius)

        # Instantiate the algorithm
        self._controlAlgorithm = TemperatureControlAlgorithm(targetCelsius,
                                                             self._mode,
                                                             self.brewer.config.temperatureHysteresisC,
                                                             self.brewer.config.dispersionPeriodSec,
                                                             self.brewer.config.dispersionDurationSec
                                                             )

        # Relay state
        self._currentState = None

        if self.brewer.getModule(SettingsHandler).getBoolean(self.STG_KEY_STATE):
            logger.debug('restoring state')
            self.setState(True, rememberChoice=False)

    def onStop(self):
        # Stop the control (and don't store the choice in DB)
        if self._running:
            self.setState(False, rememberChoice=False)

    def _run(self):
        '''
        Start the controller
        '''

        self.brewer.logInfo(__name__,
                            'control started: %.2f C (%s)' % (self.targetTemperatureCelsius, str(self._mode))
        )

        # Start control
        thermalSwitchOn, pumpOn = self._controlAlgorithm.startControl()

        self._thermalSwitch.setOn(thermalSwitchOn)
        self._pumpSwitch.setOn(pumpOn)

        errorLogged = False

        # Main loop
        while self._running:
            # Read the current temperature from probe
            currentTemperatureCelsius = self._externalSensor.getValue()

            # Check if the read failed
            if currentTemperatureCelsius == TemperatureSensor.TEMP_INVALID_C:

                # Log the error only once (if the probe failed we can except an error every loop)
                if not errorLogged:
                    self.brewer.logError(__name__, 'failure reading temperature value, shutting off')

                    # Turn heating/cooling off
                    self._thermalSwitch.setOn(False)

                    # Keep the pump running
                    self._pumpSwitch.setOn(True)

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

            # Control the relay
            thermalSwitchOn, pumpOn = self._controlAlgorithm.control(currentTemperatureCelsius)

            self._thermalSwitch.setOn(thermalSwitchOn)
            self._pumpSwitch.setOn(pumpOn)

            # Wait a bit
            sleep(self.SLEEP_TIME_SEC)

        # Turn everything off
        self._thermalSwitch.setOn(False)
        self._pumpSwitch.setOn(False)

        self.brewer.logInfo(__name__,
                            'control stopped'
        )

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

