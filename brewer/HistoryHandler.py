from brewer.Handler import Handler
import sqlite3
import datetime
import logging
from contextlib import closing

logger = logging.getLogger(__name__)


class HistoryHandler(Handler):
    SAMPLE_PERIOD_SEC = 30
    RECORD_PREFIX = 'record_'
    RECORD_FILE_NAME = 'temperature_history.json'

    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'

    DATABASE = 'history.db'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

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

        # Get current time
        currentDate = datetime.datetime.now()

        # Create a temperature/seconds sample
        sample = (currentDate.strftime(self.DATE_FORMAT),
                  currentDate.strftime(self.TIME_FORMAT),
                  tempC)

        # Insert into database
        with self.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO samples VALUES (?,?,?)', sample)

        # Reset time
        self._elapsedSec = 0

    @property
    def database(self):
        return closing(sqlite3.connect(self.DATABASE))

    def getRecords(self):
        with self.database as conn:
            with closing(conn.cursor()) as cursor:
                return [i[0] for i in cursor.execute('SELECT distinct(date) from samples').fetchall()]

    def getSamples(self, date):
        with self.database as conn:
            with closing(conn.cursor()) as cursor:
                return cursor.execute('SELECT date, time, temperature FROM samples WHERE date=? ORDER BY time ', (date,)).fetchall()

    def onStart(self):
        # Create tables
        with self.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS samples
                            (date text, time text, temperature real)''')

    def onStop(self):
        pass
