from rpi.SSD1306.Ssd1306 import Ssd1306
from brewer.Handler import Handler
import subprocess
import time
import logging
from rpi.DS18B20.TemperatureSensor import TemperatureSensor

logger = logging.getLogger(__name__)


class DisplayHandler(Handler):
    '''
    Handler in charge of displaying data, and taking commands from SSD1306 module
    '''

    # Screen IDs
    SCREEN_MAIN, SCREEN_STATS = range(2)

    # Screen list
    SCREENS = (SCREEN_MAIN, SCREEN_STATS)

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        # Instantiate SSD1306 module
        self._display = Ssd1306()

        # Register listeners for all the buttons
        for button in Ssd1306.BUTTONS:
            self._display.setButtonListener(button, lambda button, pressed: self._onButtonPressed(button) if pressed else None)

        # Set current screen
        self._currentScreen = self.SCREEN_MAIN

    def onStart(self):
        # Enable screen
        self._onActivity()

        # Clear screen
        self._display.renderer.clear()
        self._display.renderer.display()

    def onStop(self):
        # Clear screen
        self._display.renderer.clear()
        self._display.renderer.display()

    def _onButtonPressed(self, button):
        '''
        Called when any SSD1306 button is pressed
        '''

        wasEnabled = self._enabled

        self._onActivity()

        # If the screen wasn't enabled, just enable it without processing the command
        if not wasEnabled:
            self.update()
            return

        if button == Ssd1306.BUTTON_A:
            # Cycle trough screens on button A
            self._currentScreen = (self._currentScreen + 1) % len(self.SCREENS)
            self.update()

        elif button == Ssd1306.BUTTON_B:
            # Turn relay on/off on button B
            self.brewer.relayPin.setOutput(not self.brewer.relayPin.output)
            self.update()

        elif button == Ssd1306.BUTTON_UP:
            # Turn temperature control on, on button UP
            if not self.brewer.temperatureControl.running:
                self.brewer.temperatureControl.setState(True)
                self.update()

        elif button == Ssd1306.BUTTON_DOWN:
            # Turn temperature control on, on button DOWN

            if self.brewer.temperatureControl.running:
                self.brewer.temperatureControl.setState(False)
                self.update()

        # If this combination of buttons is pressed simultaneously stop the application
        if self._display.isButtonPressed(Ssd1306.BUTTON_A) and self._display.isButtonPressed(Ssd1306.BUTTON_B) and self._display.isButtonPressed(Ssd1306.BUTTON_CENTER):
            logger.debug('Stopping')
            self.brewer.stop()

    def _onActivity(self):
        '''
        Triggered on any user activity
        '''

        # Remember last activity time & enable screen
        self._lastActionTime = time.time()
        self._enabled = True

    def update(self, elapsedTime=0):
        '''
        Called periodically
        '''

        if not self._enabled:
            return

        # Check if the screen timedout
        lastActionElapsedTime = time.time() - self._lastActionTime

        if self._enabled and lastActionElapsedTime > self.brewer.config.displayTimeout:
            # We timedout so clear display
            logger.debug('Screen timeout')

            self._enabled = False
            self._display.renderer.clear()
            self._display.renderer.display()
            return

        # Screen handlers
        screenHandlers = (
            self._getMainScreenText,
            self._getStatsScreenText,
            )

        # Render text & update display
        self._display.renderer.clear()
        self._display.renderer.drawText((0, 0), screenHandlers[self._currentScreen]())
        self._display.renderer.display()

    def _getMainScreenText(self):
        '''
        Main screen text. Displays temperature, control and relay state
        '''

        text = ''

        # Temperature
        text += 'Temperature: '

        tempC = self.brewer.temperatureSensor.getTemperatureCelsius()

        if tempC != TemperatureSensor.TEMP_INVALID_C:
            text += '%.2f C' % tempC
        else:
            text += '?'

        text += '\n'

        # Relay on?
        if self.brewer.relayPin.output:
            text += 'Relay ON'
        text += '\n'

        # Temperature control running?
        if self.brewer.temperatureControl.running:
            text += 'Control: ON'

        return text

    def _getStatsScreenText(self):
        '''
        Stats screen, shows IP address, CPU load etc.
        '''

        text = ''

        # IP address
        cmd = "hostname -I | cut -d\' \' -f1"
        ip = '?'

        try :
            ip = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            pass

        text += 'IP: %s\n' % ip.decode('utf-8')

        # CPU load
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"

        cpu = '?'
        try:
            cpu = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            pass

        text += cpu.decode('utf-8') + '\n'

        # Memory
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"

        memUsage = ''
        try:
            memUsage = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            pass

        text += memUsage.decode('utf-8')

        return text
