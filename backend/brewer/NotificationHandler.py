from brewer.Handler import Handler
import logging
from brewer.HardwareHandler import HardwareHandler
from brewer.AComponent import ComponentType

logger = logging.getLogger(__name__)


class NotificationHandler(Handler):
    TEMPERATURE_HYSTERESIS_C = 1.0

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

        # Indication of a warning has been sent for a
        self._warningSent = {}

    def update(self, elapsedTime):

        # Go trough all the sensors
        for sensor in self.brewer.getModule(HardwareHandler).getComponents(ComponentType.SENSOR):

            # Set initial state for sensor
            if sensor.name not in self._warningSent:
                self._warningSent[sensor.name] = False

            # Get temperature threshold
            warningTemperature = self.brewer.config.warningTemperatureC

            # Read sensor temperature
            currentTemperatureC = sensor.getValue()

            # Check if we're out of bounds, and did not send a warning
            if currentTemperatureC > warningTemperature and not self._warningSent[sensor.name]:
                # Temperature out of bounds, send a warning
                self.brewer.logCritical(__name__, 'Sensor %r temperature warning : %.2f C (expected below %.2f C)' %
                                       (sensor.name, currentTemperatureC, warningTemperature))

                self._warningSent[sensor.name] = True

            # Check if the temperature returned to normal
            elif (currentTemperatureC < warningTemperature - self.TEMPERATURE_HYSTERESIS_C) and self._warningSent[sensor.name]:
                # Temperature returned to normal
                self.brewer.logWarning(__name__, 'Sensor %r temperature returned to normal: %.2f C'
                                        % (sensor.name, currentTemperatureC))

                self._warningSent[sensor.name] = False
