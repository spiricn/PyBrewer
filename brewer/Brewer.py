import os
import time
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
from rpi.IOPin import IOPin
import sqlite3
from contextlib import closing

from brewer.DisplayHandler import DisplayHandler
from brewer.HistoryHandler import HistoryHandler
from brewer.LogHandler import LogHandler
from brewer.rest.LogREST import LogREST
from brewer.TemperatureControlHandler import TemperatureControlHandler
from brewer.TemperatureReaderHandler import TemperatureReaderHandler
from brewer.rest.HistoryREST import HistoryREST

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

        # Relay control
        self._relayPin = IOPin.createOutput(self._config.relayGpioPinNumber)

        self._mainThread = None

        # Module classes
        modules = (
                    LogHandler,
                    DisplayHandler,
                    HistoryHandler,
                    TemperatureControlHandler,
                    TemperatureReaderHandler
        )

        self._modules = []

        # Instantiate modules
        for module in modules:
            self._modules.append(module(self))

    @property
    def database(self):
        return closing(sqlite3.connect(self.config.databasePath))

    def getModule(self, clazz):
        for module in self._modules:
            if isinstance(module, clazz):
                return module

        return None

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
            LogREST(self),
            HistoryREST(self),
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

        return self.getModule(TemperatureReaderHandler)

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

        return self.getModule(TemperatureControlHandler)

    def logInfo(self, module, message):
        self.log(logging.INFO, module, message)

    def logDebug(self, module, message):
        self.log(logging.DEBUG, module, message)

    def logWarning(self, module, message):
        self.log(logging.WARN, module, message)

    def logError(self, module, message):
        self.log(logging.ERROR, module, message)

    def logCritical(self, module, message):
        self.log(logging.CRITICAL, module, message)

    def log(self, level, module, message):
        self.getModule(LogHandler).log(level, module, message)

    def _restStatus(self, **kwargs):
        '''
        Reads the status of everything
        '''

        status = {
            'relay_on' : self._relayPin.output,
            'temperature_controller_running' : self.temperatureControl.running,
            'temperature_controller_target_temp' : self.temperatureControl.targetTemperatureCelsius,
            'temp' : self.temperatureSensor.getTemperatureCelsius(),
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

        if self.temperatureControl.running:
            self.temperatureControl.setState(False)

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
