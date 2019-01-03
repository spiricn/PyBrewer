class Config:
    '''
    Brewer configuration
    '''

    def __init__(self, cfgDict):
        self._cfgDict = cfgDict

    @property
    def probeDeviceId(self):
        '''
        DS18B20 probe device ID (example: '28-00000482b243')
        '''

        return self._getValue('TEMPERATURE_PROBE_DEV_ID', '')

    @property
    def port(self):
        '''
        HTTP server port
        '''

        return self._getValue('HTTP_PORT', 8080)

    @property
    def root(self):
        '''
        HTTP server root directory
        '''

        return self._getValue('HTTP_ROOT', 'app')

    @property
    def targetTemperatureCelsius(self):
        '''
        Target temperature in celsius
        '''

        return self._getValue('TARGET_TEMPERATURE_C', 25.0)

    @property
    def relayGpioPinNumber(self):
        '''
        Relay control GPIO PIN number
        '''

        return self._getValue('RELAY_GPIO_PIN_NUMBER', -1)

    @property
    def pushoverUserToken(self):
        '''
        Pushover user token
        '''

        return self._getValue('PUSHOVER_USER_TOKEN', '')

    @property
    def pushoverAppToken(self):
        '''
        Pushover application token
        '''

        return self._getValue('PUSHOVER_APP_TOKEN', '')

    @property
    def displayTimeout(self):
        '''
        Time until display turns off
        '''

        return self._getValue('DISPLAY_TIMEOUT', 2 * 60.0)

    @property
    def databasePath(self):
        '''
        Database path
        '''

        return self._getValue('DATABASE_PATH', 'app/pybrewer.db')

    @property
    def validTemperatureRangeCelsius(self):
        '''
        Temperature range considered valid.
        Temperatures outside of this range will be treated as errors.
        '''

        return self._getValue('VALID_TEMPERATURE_RANGE_CELSIUS', (10, 40))

    @property
    def mode(self):
        '''
        Temperature control mode (heating/cooling)
        '''

        return self._getValue('TEMPERATURE_CONTROL_MODE', 'HEAT')

    def _getValue(self, key, defaultValue=None):
        if key in self._cfgDict:
            return self._cfgDict[key]
        else:
            return defaultValue
