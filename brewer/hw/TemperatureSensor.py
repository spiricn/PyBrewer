import os
import logging

logger = logging.getLogger(__name__)


class TemperatureSensor:
    '''
    Reads temperature from a DS18B20 probe using a 1 wire protocol
    '''

    # Invalid temperature value
    TEMP_INVALID_C = 99999999

    # Path to 1 wire devices
    ONE_WIRE_DEVICES_PATH = '/sys/bus/w1/devices'

    # Name of the device file
    ONE_WIRE_DEVICE_FILE = 'w1_slave'

    # CRC value yes according to w1 protocol
    CRC_YES = 'YES'

    # Temperature value splitter from the probe
    TEMPERATURE_ID = 't='

    def __init__(self, deviceId):
        self._deviceId = deviceId
        self._devicePath = os.path.join(self.ONE_WIRE_DEVICES_PATH, self._deviceId, self.ONE_WIRE_DEVICE_FILE)
        logger.debug('Using W1 device: %r @ %r' % (self._deviceId, self._devicePath))

    def getTemperatureCelsius(self):
        '''
        Read temperature using raspbian w1 protocol
        '''

        # Check if device file exists
        if not os.path.exists(self._devicePath):
            logger.error('Could not find device file: %r' % self._devicePath)
            return self.TEMP_INVALID_C

        # Read & parse data
        with open(self._devicePath, 'r') as fileObj:
            tempData = fileObj.read()

            # Split the data into lines
            lines = tempData.splitlines()

            # Need at least one line
            if len(lines) < 2:
                logger.error('Invalid data: %r' % tempData)
                return self.TEMP_INVALID_C

            # Take last token of the CRC line
            crc = lines[0].split(' ')[-1]

            # Check CRC
            if crc != self.CRC_YES:
                logger.error('Invalid CRC: %r' % crc)
                return self.TEMP_INVALID_C

            temperature = int(lines[1].split(self.TEMPERATURE_ID)[1])

            return temperature / 1000.0
