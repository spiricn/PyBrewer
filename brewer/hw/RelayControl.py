# Indication if we have RPI API or not (e.g. running on desktop or PI)
gHasRpiAPI = False

import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO

    gHasRpiAPI = True
except:
    pass


class RelayControl:
    '''
    Controls the relay via raspberry PI GPIO pin
    '''

    def __init__(self, pinNumber):
        self._state = False

        self._pinNumber = pinNumber

        # Initialize PIN
        if gHasRpiAPI:
            logger.debug('initializing relay control on PIN %d' % pinNumber)

            GPIO.setmode(GPIO.BCM)

            # Set our pin as output
            GPIO.setup(self._pinNumber, GPIO.OUT)

        else:
            logger.warning('RPi API not detected')

        # TUrn of on start
        self.setState(False)

    def getState(self):
        '''
        Get current relay state
        '''

        return self._state

    def setState(self, state):
        '''
        Set relay state
        '''

        self._state = state

        # Set to LOW or HIGH depending on the state
        if gHasRpiAPI:
            GPIO.output(self._pinNumber, GPIO.HIGH if state else GPIO.LOW)

