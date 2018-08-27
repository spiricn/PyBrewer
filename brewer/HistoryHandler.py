from brewer.Handler import Handler
import os
import datetime
import json
import logging
import time

logger = logging.getLogger(__name__)


class RecordDate:

    def __init__(self, date, path):
        self._date = date
        self._path = path

    def readSamples(self):
        with open(self._path, 'r') as fileObj:
            try:
                return json.load(fileObj)
            except Exception as e:
                logger.error('error loading samples from %r: %r' % (str(e), self._path))

        return None

    @property
    def date(self):
        return self._date

    def __str__(self):
        return '{RecordDate ' + str(self._date) + ' / ' + self._path + '}'


class HistoryHandler(Handler):
    SAMPLE_PERIOD_SEC = 30
    RECORD_PREFIX = 'record_'
    RECORD_FILE_NAME = 'temperature_history.json'
    DATE_FORMAT = '%d_%m_%Y'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        self._samples = []

        self._elapsedSec = 0

        self._prevPath = None

    def update(self, elapsedTime):
        # Measure time
        self._elapsedSec += elapsedTime

        if self._elapsedSec < self.SAMPLE_PERIOD_SEC:
            # Not yet time to update
            return

        # Get current temperature reading
        tempC = self.brewer.temperatureSensor.getTemperatureCelsius()

        # Create a temperature/seconds sample
        self._samples.append((int(time.time()), tempC))

        # File path
        filePath = os.path.join(self.brewer.config.historyPath, self.RECORD_PREFIX + datetime.date.today().strftime(self.DATE_FORMAT), self.RECORD_FILE_NAME)

        if filePath != self._prevPath:

            if os.path.isfile(filePath):
                record = self._createRecord(filePath)
                self._samples = record.readSamples()

            self._prevPath = filePath

        fileDir = os.path.dirname(filePath)

        # Create dir if it doesn't exist
        if not os.path.isdir(fileDir):
            os.makedirs(fileDir)

        # Dump the samples
        with open(filePath, 'w') as fileObj:
            json.dump(self._samples, fileObj)

        # Reset time
        self._elapsedSec = 0

    def getRecords(self):
        records = []

        for fileName in os.listdir(self.brewer.config.historyPath):
            fullDirPath = os.path.join(self.brewer.config.historyPath, fileName)

            if fileName.startswith(self.RECORD_PREFIX):
                fullPath = os.path.join(fullDirPath, self.RECORD_FILE_NAME)

                if not os.path.isfile(fullPath):
                    logger.warning('missing record file: %r' % fullPath)
                    continue

                records.append(self._createRecord(fullPath))

        return records

    def _createRecord(self, fullPath):
        fullPath = os.path.normpath(os.path.abspath(fullPath))

        # Parse date
        date = datetime.datetime.strptime(fullPath.split(self.RECORD_PREFIX)[1].split('/')[0],
                                        self.DATE_FORMAT)

        return RecordDate(date, fullPath)

    def onStart(self):
        pass

    def onStop(self):
        pass
