from brewer.Handler import Handler
import datetime
import logging
from contextlib import closing
from tmp.brewer.hw.TemperatureSensor import TemperatureSensor

logger = logging.getLogger(__name__)


class HistoryHandler(Handler):
    SAMPLE_PERIOD_SEC = 30
    RECORD_PREFIX = 'record_'
    RECORD_FILE_NAME = 'temperature_history.json'

    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        self._elapsedSec = self.SAMPLE_PERIOD_SEC

        self._prevPath = None

    def update(self, elapsedTime):
        # Measure time
        self._elapsedSec += elapsedTime

        if self._elapsedSec < self.SAMPLE_PERIOD_SEC:
            # Not yet time to update
            return

        # Get current temperature reading
        tempC = self.brewer.temperatureSensor.getTemperatureCelsius()

        # Get current time
        currentDate = datetime.datetime.now()

        # Create a temperature/seconds sample
        sample = (currentDate.strftime(self.DATE_FORMAT),
                  currentDate.strftime(self.TIME_FORMAT),
                  tempC)

        # Insert into database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO samples VALUES (?,?,?)', sample)

        # Reset time
        self._elapsedSec = 0

    def getRecords(self):
        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                return [i[0] for i in cursor.execute('SELECT distinct(date) from samples ORDER BY date DESC').fetchall()]

    def getSamples(self, date):
        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                return [(date, time, temperature) for date, time, temperature in cursor.execute('SELECT date, time, temperature FROM samples WHERE date=? ORDER BY time ', (date,)).fetchall()
                           if temperature != TemperatureSensor.TEMP_INVALID_C]

    def onStart(self):
        # Create tables
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS samples
                            (date text, time text, temperature real)''')

    def onStop(self):
        pass
