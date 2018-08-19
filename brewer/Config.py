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

    def _getValue(self, key, defaultValue=None):
        if key in self._cfgDict:
            return self._cfgDict[key]
        else:
            return defaultValue
