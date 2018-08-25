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
from rpi.SSD1306.Ssd1306 import Ssd1306
import subprocess
from threading import Lock

logger = logging.getLogger(__name__)


class Brewer():
    '''
    Main brewer module
    '''

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

        self._display = Ssd1306()
        self._display.renderer.clear()
        self._display.renderer.display()

        self._display.setButtonListener(Ssd1306.BUTTON_B, lambda button, pressed: self._onButtonBPressed() if pressed else None)

        self._display.setButtonListener(Ssd1306.BUTTON_A, lambda button, pressed: self._onButtonAPressed() if pressed else None)

        self._display.setButtonListener(Ssd1306.BUTTON_CENTER,
                                         lambda button, pressed:  self._onButtonCenterPressed() if pressed else None)

        self._lock = Lock()

        self._displayEnabled = True
        self._lastActionTime = time.time()

    def _onButtonBPressed(self):
        self._relayPin.setOutput(not self._relayPin.output)

        self._resetTimer()

        self._updateDisplay()

    def _onButtonAPressed(self):
        self._resetTimer()

        self._updateDisplay()

    def _resetTimer(self):
        self._lastActionTime = time.time()
        self._displayEnabled = True

    def _onButtonCenterPressed(self):
        self._resetTimer()

        self._temperatureControl.setState(not self._temperatureControl.running)

        self._updateDisplay()

    def _mainLoop(self):
        '''
        Main loop
        '''

        # Update display every 2 seconds
        while self._running:
            currentTime = time.time()

            if currentTime - self._lastActionTime >= 2 * 60:
                if self._displayEnabled:
                    self._displayEnabled = False
                    self._updateDisplay()
            else:
                self._updateDisplay()

            time.sleep(2)

        logger.debug('main loop stopped')

        # CLear display
        self._display.renderer.clear()
        self._display.renderer.display()

    def start(self):
        self._updateDisplay()

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

    def _updateDisplay(self):
        with self._lock:
            if not self._displayEnabled:
                self._display.renderer.clear()
                self._display.renderer.display()
                return

            text = ''

            if self._display.isButtonPressed(Ssd1306.BUTTON_A):
                # If button A is pressed, display stats

                # IP address
                cmd = "hostname -I | cut -d\' \' -f1"
                ip = subprocess.check_output(cmd, shell=True)

                text += 'IP: %s\n' % ip.decode('utf-8')

                # CPU load
                cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
                cpu = subprocess.check_output(cmd, shell=True)

                text += cpu.decode('utf-8') + '\n'

                # Memory
                cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
                memUsage = subprocess.check_output(cmd, shell=True)

                text += memUsage.decode('utf-8')

            else:
                # Display status

                # Temperature
                text += 'Temperature: '

                tempC = self._temperatureSensor.getTemperatureCelsius()

                if tempC != TemperatureSensor.TEMP_INVALID_C:
                    text += '%.2f C' % tempC
                else:
                    text += '?'

                text += '\n'

                # Relay on?
                if self._relayPin.output:
                    text += 'Relay ON'
                text += '\n'

                # Temperature control running?
                if self._temperatureControl.running:
                    text += 'Control: ON'

            # Render text & update display
            self._display.renderer.clear()
            self._display.renderer.drawText((0, 0), text)
            self._display.renderer.display()

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
