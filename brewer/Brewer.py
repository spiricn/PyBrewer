import os
import time
from rpi.DS18B20.TemperatureSensor import TemperatureSensor
from ssc.http import HTTP
from ssc.servlets.RestServlet import RestHandler
from ssc.servlets.ServletContainer import ServletContainer
from rest.TemperatureREST import TemperatureREST
from rest.RelayREST import RelayREST
from TemperatureControl import TemperatureControl
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from time import sleep
import logging
from threading import Thread
import brewer
from brewer.PushNotifications import PushNotifications
from rpi.IOPin import IOPin

from brewer.DisplayHandler import DisplayHandler

logger = logging.getLogger(__name__)


class Brewer():
    '''
    Main brewer module
    '''

    EVENT_HEARTBEAT = range(1)

    def __init__(self, config):
        # Is the brewer running or not
        self._running = False

        IOPin.init()

        logging.getLogger("Adafruit_I2C").setLevel(logging.WARNING)

        # Configuration
        self._config = config

        # Temperature sensor
        self._temperatureSensor = TemperatureSensor(self._config.probeDeviceId)

        # Relay control
        self._relayPin = IOPin.createOutput(self._config.relayGpioPinNumber)

        # Temperature control (uses sensor & relay control to achieve target temperature)
        self._temperatureControl = TemperatureControl(self._relayPin, self._temperatureSensor, self._config.targetTemperatureCelsius)

        # Push notifications
        self._pushNotifications = PushNotifications(self._config.pushoverUserToken, self._config.pushoverAppToken)

        self._mainThread = None

        # Module classes
        modules = (DisplayHandler,
                   )

        self._modules = []

        # Instantiate modules
        for module in modules:
            self._modules.append(module(self))

    @property
    def config(self):
        '''
        Configuration
        '''

        return self._config

    def _mainLoop(self):
        '''
        Main loop
        '''

        logger.debug('main loop started')

        # Start modules
        for module in self._modules:
            module.onStart()

        # Update display every 2 seconds
        lastTime = time.time()

        while self._running:
            currentTime = time.time()

            elapsedTime = currentTime - lastTime

            lastTime = currentTime

            # Update modules
            for module in self._modules:
                module.update(elapsedTime)

            time.sleep(2)

        logger.debug('main loop stopped')

        # Stop modules
        for module in self._modules:
                module.onStop()

    def start(self):
        if self._running:
            raise RuntimeError('Already running')

        self._running = True

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

        self._mainThread = Thread(target=self._mainLoop())
        self._mainThread.start()

    @property
    def temperatureSensor(self):
        '''
        Temperature sensor
        '''

        return self._temperatureSensor

    @property
    def relayPin(self):
        '''
        Relay control pin
        '''

        return self._relayPin

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
            'relay_on' : self._relayPin.output,
            'temperature_controller_running' : self._temperatureControl.running,
            'temperature_controller_target_temp' : self._temperatureControl.targetTemperatureCelsius,
            'temp' : self._temperatureSensor.getTemperatureCelsius(),
        }

        return (CODE_OK, MIME_JSON, status)

    @property
    def version(self):
        '''
        Application version
        '''

        return brewer.__version__

    def stop(self):
        ''''
        Stop the brewer
        '''

        self._running = False

        if self._temperatureControl.running:
            self._temperatureControl.setState(False)

        # Stop main thread
        if self._mainThread:
            self._mainThread.join()
            self._mainThread = None

    def wait(self):
        '''
        Wait until we're done processing requests
        '''

        # TODO semaphores
        while self._running:
            sleep(1)

        logger.debug('stopping')

        self._server.stop()

        return 0
