import os
import sys
import pprint
from os.path import expanduser

class Config:
    '''
    Brewer configuration
    '''

    def __init__(self):
        # Indication if login authorization is enabled
        self.authorizationEnabled = False

        # HTTP server port
        self.port = 8080

        # Pushover user token
        self.pushoverUserToken = ''

        # Pushover application token
        self.pushoverAppToken = ''

        # Temperature range considered valid.
        # Temperatures outside of this range will be treated as errors.
        self.validTemperatureRangeCelsius = (10, 40)

        # Temperature control mode (heating/cooling)
        self.mode = 'MODE_HEAT'

        # List of hardware switches
        self.switches = []

        # List of hardware sensors
        self.sensors = []

        # Wort sensor ID
        self.wortSensor = None

        # External sensor ID
        self.externalSensor = None

        # Thermal switch ID
        self.thermalSwitch = None

        # Pump switch ID
        self.pumpSwitch = None

        # Temperature control delta
        self.temperatureHysteresisC = 0.3

        # Warning temperature
        self.warningTemperatureC = None

        # Dropbox application token
        self.dropboxToken = ''

        # Periodic backup time
        self.backupPeriodSec = -1

        # Email client SMTP server address
        self.smtpServer = ''

        # Email client SMTP server port
        self.smtpPort = 587

        # Email client SMTP server username
        self.smtpUsername = ''

        # Email client SMTP server password
        # TODO Stored in plain text, terrribly unsercure...
        self.smtpPassword = ''

        # Comma separated list of emails the daily report should be sent to
        self.reportMails = ''

        # Time at which the report will be sent every day format: %HH:%MM:%SS
        self.reportTime = '08:00:00'

    def serialize(self):
        '''
        Serialize configuration to file system
        '''

        with open(self.configPath, 'w') as fileObj:
            fileObj.write( pprint.pformat(self.__dict__, indent=4) )

    def deserialize(self):
        '''
        Deserialize configuration from file system
        '''

        with open(self.configPath, 'r') as fileObj:
            configDict = eval(fileObj.read())

            for key in configDict:
                if key not in self.__dict__:
                    raise RuntimeError('Invalid configuration key %r' % key)

                self.__dict__[key] = configDict[key]

    @property
    def root(self):
        '''
        HTTP root directory
        '''

        return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'app')

    @property
    def home(self):
        '''
        Home directory used for database/config files etc.
        '''
        return expanduser("~/.pybrewer")

    @property
    def databasePath(self):
        '''
        Database path
        '''

        return os.path.join(self.home, 'pybrewer.db')

    @property
    def configPath(self):
        '''
        Configuration file path
        '''

        return os.path.join(self.home, 'config.py')