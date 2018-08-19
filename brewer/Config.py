class Config:
    '''
    Brewer configuration
    '''

    def __init__(self, port, root, targetTemperatureCelsius):
        self._port = port
        self._root = root
        self._targetTemperatureCelsius = targetTemperatureCelsius

    @property
    def port(self):
        '''
        HTTP server port
        '''

        return self._port

    @property
    def root(self):
        '''
        HTTP server root directory
        '''

        return self._root

    @property
    def targetTemperatureCelsius(self):
        '''
        Target temperature in celsius
        '''

        return self._targetTemperatureCelsius
