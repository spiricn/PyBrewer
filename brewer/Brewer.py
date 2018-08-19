import os
from hw.TemperatureSensor import TemperatureSensor
from ssc.http import HTTP
from ssc.servlets.RestServlet import RestHandler
from ssc.servlets.ServletContainer import ServletContainer
from rest.TemperatureREST import TemperatureREST
from rest.RelayREST import RelayREST
from hw.RelayControl import RelayControl
from TemperatureControl import TemperatureControl
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from time import sleep


class Brewer():
    '''
    Main brewer module
    '''

    def __init__(self, config):
        # Is the brewer running or not
        self._running = False

        # Configuration
        self._config = config

        # Temperature sensor
        self._temperatureSensor = TemperatureSensor()

        # Relay control
        self._relayControl = RelayControl()

        # Temperature control (uses sensor & relay contorl to achieve target temperature)
        self._temperatureControl = TemperatureControl(self._relayControl, self._temperatureSensor, self._config.targetTemperatureCelsius)

    def start(self):
        if self._running:
            raise RuntimeError('Already running')

        self._running = True

        # Create HTTP server
        self._server = ServletContainer('',
                                     self._config.port,
                                     self._config.root,
                                     os.path.join(self._config.root, 'tmp')
         )

        # Create REST API
        self._server.addRestAPI()

        # Add all the REST modules
        restModules = (
            TemperatureREST(self),
            RelayREST(self),
        )

        for module in restModules:
            self._server.rest.addApi(module.getRestAPI())

        # Add our own REST API
        self._server.rest.addApi(
            (
             RestHandler(
                    'status',
                    self._restStatus
                    ),

            )
        )

        # Register ourselves to the servlet environment (will be available from all the templates)
        self._server.env['Brewer'] = self

        # Start the server
        self._server.start()

        input()

        self._server.stop()

    @property
    def temperatureSensor(self):
        '''
        Temperature sensor
        '''

        return self._temperatureSensor

    @property
    def relayControl(self):
        '''
        Relay control
        '''

        return self._relayControl

    @property
    def temperatureControl(self):
        '''
        Temperature controller
        '''

        return self._temperatureControl

    def _restStatus(self, **kwargs):
        '''
        Reads the status of everything
        '''

        status = {
            'temp' : self._temperatureSensor.getTemperatureCelsius(),
            'relay_on' : self._relayControl.getState(),
            'temperature_controller_running' : self._temperatureControl.running,
            'temperature_controller_target_temp' : self._temperatureControl.targetTemperatureCelsius
        }

        return (CODE_OK, MIME_JSON, status)

    def wait(self):
        '''
        Wait until we're done processing requests
        '''

        # TODO semaphores
        while self._running:
            sleep(1)

        # TODO Correct return code
        return 0
