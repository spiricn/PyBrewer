from contextlib import closing
import logging
import os
import sqlite3
from threading import Thread
from time import sleep
import time
from logging import Formatter


from ssc.http import HTTP
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from ssc.servlets.RestServlet import RestHandler
from ssc.servlets.ServletContainer import ServletContainer

import brewer
from brewer.HistoryHandler import HistoryHandler
from brewer.LogHandler import LogHandler
from brewer.SessionHandler import SessionHandler
from brewer.TemperatureControlHandler import TemperatureControlHandler
from brewer.SettingsHandler import SettingsHandler
from brewer.rest.HistoryREST import HistoryREST
from brewer.rest.LogREST import LogREST
from brewer.rest.HardwareREST import HardwareREST
from brewer.rest.TemperatureControlREST import TemperatureControlREST
from brewer.SessionServlet import SessionServlet
from brewer.rest.UserREST import UserREST
from brewer.rest.SystemREST import SystemREST
from brewer.HardwareHandler import HardwareHandler, ComponentType
from brewer.RelaySwitch import RelaySwitch
from brewer.ProbeSensor import ProbeSensor
from brewer.TemperatureReader import TemperatureReader
from brewer.NotificationHandler import NotificationHandler
from brewer.LoggingHandler import LoggingHandler
from brewer.DropboxHandler import DropboxHandler
from brewer.MailHandler import MailHandler
from brewer.ReportHandler import ReportHandler
from brewer.Utils import Utils

logger = logging.getLogger(__name__)


if Utils.isRunningOnPi():
    from rpi.IOPin import IOPin
else:
    from brewer.MockIOPin import MockIOPin as IOPin


class Brewer():
    '''
    Main brewer module
    '''

    EVENT_HEARTBEAT = range(1)

    # Settings key used to remember the last time we backed up
    STG_KEY_LAST_BACKUP = 'LAST_BACKUP_SEC'

    # Number of attempts to backup before giving up
    NUM_BACKUP_RETRIES = 5

    def __init__(self, config):
        # Is the brewer running or not
        self._running = False

        self._restart = False

        IOPin.init()

        logging.getLogger("Adafruit_I2C").setLevel(logging.WARNING)

        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.NOTSET)

        self._logHandler = LoggingHandler(os.path.join(config.home, 'log.txt'))
        rootLogger.addHandler(self._logHandler)
        self._logHandler.setFormatter(Formatter('%(asctime)s %(levelname)s/%(name)s: %(message)s'))

        # Configuration
        self._config = config

        self._mainThread = None

        # Module classes
        modules = (
                    DropboxHandler,
                    SettingsHandler,
                    SessionHandler,
                    LogHandler,
                    TemperatureControlHandler,
                    HistoryHandler,
                    HardwareHandler,
                    NotificationHandler,
                    MailHandler,
                    ReportHandler,
        )

        self._modules = []

        # Instantiate modules
        for module in modules:
            self._modules.append(module(self))

        # Add switches
        for switch in self.config.switches:
            logger.debug('Add switch %r' % switch['ID'])

            self.getModule(HardwareHandler).addCustom(
                RelaySwitch(
                    switch['NAME'],
                    switch['ID'],
                    switch['COLOR'],
                    IOPin.createOutput(switch['GPIO_PIN']),
                    bool(switch['GRAPH'])
                    )
                )

        # Add sensors
        for sensor in self.config.sensors:
            logger.debug('Add sensor %r' % sensor['ID'])

            self.getModule(HardwareHandler).addCustom(
                ProbeSensor(
                    sensor['NAME'],
                    sensor['ID'],
                    sensor['COLOR'],
                    TemperatureReader(sensor['DEV_ID'], self.config.validTemperatureRangeCelsius, lambda errorMessage: self.logError("TemperatureReader", errorMessage)),
                    bool(sensor['GRAPH'])
                    )
                )

    @property
    def database(self):
        return closing(sqlite3.connect(self.config.databasePath))

    def getModule(self, clazz):
        for module in self._modules:
            if isinstance(module, clazz):
                return module

        return None

    def getMessages(self):
        '''
        TODO
        '''

        messages = []

        # Get messages from all the modules
        for module in self._modules:
            messages += module.getMessages()

        # Sort by timestamp
        messages.sort(key=lambda item: item.timestamp)

        return messages

    @property
    def server(self):
        return self._server

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

        # Start the server
        self._server.start()

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

            # Check if we need to backup
            lastBackup = self.getModule(SettingsHandler).getFloat(self.STG_KEY_LAST_BACKUP)

            # Check if it's time for periodic backup
            if self.config.backupPeriodSec > 0 and currentTime - lastBackup >= self.config.backupPeriodSec:
                logger.debug('backing up after %d sec'  % (currentTime - lastBackup))

                success = False

                # Attempt to backup with retries
                for i in range(self.NUM_BACKUP_RETRIES):
                    try:
                        self.backup()
                    except Exception as e:
                        logger.error('Backup failed: %s' % str(e))
                        continue

                    success = True
                    break

                if not success:
                    self.logError(__name__, 'backup failed')
                else:
                    self.logDebug(__name__, 'backup success')

                # Remember when we last backed up
                self.getModule(SettingsHandler).putFloat(self.STG_KEY_LAST_BACKUP, currentTime)

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
                                     os.path.join(self._config.home, 'tmp')
         )

        self._server.insertServlet(0, SessionServlet(self, self._server, '(.*?)'))

        # Create REST API
        self._server.addRestAPI()

        # Add all the REST modules
        restModules = (
            HardwareREST(self),
            TemperatureControlREST(self),
            LogREST(self),
            HistoryREST(self),
            UserREST(self),
            SystemREST(self),
        )

        for module in restModules:
            self._server.rest.addApi(module.getRestAPI())

        # Register ourselves to the servlet environment (will be available from all the templates)
        self._server.env['Brewer'] = self

        self._mainThread = Thread(target=self._mainLoop())
        self._mainThread.start()

    def restart(self):
        self._restart = True

        self.stop()

    def backup(self):
        '''
        Backup files to Dropbox
        '''

        # Files we're backing up
        backupFiles = (
            self.config.configPath,
            self.config.databasePath
        )

        for filePath in backupFiles:
            logger.debug('backing up %r' % filePath)

            # Upload file
            self.getModule(DropboxHandler).upload(filePath,
                '/' + os.path.basename(filePath))

        logger.debug('backup done')

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

        # Error code 64 is an indication to the watchdog, that we should restart right away
        return 0 if not self._restart else 64
