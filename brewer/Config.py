class Config:
    '''
    Brewer configuration
    '''

    def __init__(self, cfgPath):
        self._configPath = cfgPath

        with open(self._configPath, 'r') as fileObj:
            configDict = eval(fileObj.read())

        self._cfgDict = configDict

    @property
    def authorizationEnabled(self):
        '''
        '''

        return self._getValue('AUTHORIZATION_ENABLED', False)

    @property
    def configPath(self):
        '''
        '''
        return self._configPath

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

    @property
    def switches(self):
        return self._getValue('SWITCHES', [])

    @property
    def sensors(self):
        return self._getValue('TEMPERATURE_SENSORS', [])

    @property
    def wortSensor(self):
        return self._getValue('WORT_SENSOR', None)

    @property
    def externalSensor(self):
        return self._getValue('EXTERNAL_SENSOR', None)

    @property
    def thermalSwitch(self):
        return self._getValue('THERMAL_SWITCH', None)

    @property
    def pumpSwitch(self):
        return self._getValue('PUMP_SWITCH', None)

    @property
    def temperatureHysteresisC(self):
        return self._getValue('TEMPERATURE_HYSTERESIS_C', 0.3)

    @property
    def warningTemperatureC(self):
        return self._getValue('WARNING_TEMP_C', None)

    def _getValue(self, key, defaultValue=None):
        if key in self._cfgDict:
            return self._cfgDict[key]
        else:
            return defaultValue
