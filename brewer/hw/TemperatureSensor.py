import os


class TemperatureSensor:
    '''
    Reads temperature from a DS18B20 probe using a 1 wire protocol
    '''

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
        self._devicePath = os.path.join(self.ONE_WIRE_DEVICES_PATH, self._deviceId, self.ONE_WIRE_DEVICES_PATH)

    def getTemperatureCelsius(self):
        '''
        Read temperature using raspbian w1 protocol
        '''

        # Check if device file exists
        if not os.path.exists(self._devicePath):
            raise RuntimeError('Could not find device file: %r' % self._devicePath)

        # Read & parse data
        with open(self._devicePath, 'r') as fileObj:
            tempData = fileObj.read()

            # Split the data into lines
            lines = tempData.splitlines()

            # Need at least one line
            if len(lines) < 2:
                raise RuntimeError('Invalid data: %r' % tempData)

            # Take last token of the CRC line
            crc = lines[0].split(' ')[-1]

            # Check CRC
            if crc != self.CRC_YES:
                raise RuntimeError('Invalid CRC: %r' % crc)

            temperature = int(lines[1].split(self.TEMPERATURE_ID)[1])

            return temperature / 1000.0
