from brewer.Handler import Handler
import datetime
import logging
from contextlib import closing
from tmp.brewer.hw.TemperatureSensor import TemperatureSensor

logger = logging.getLogger(__name__)


class HistoryHandler(Handler):
    '''
    Handler which records temperature / controller / relay history
    '''

    # Sample recording rate
    SAMPLE_PERIOD_SEC = 30

    # Date format used for samples
    DATE_FORMAT = '%Y-%m-%d'

    # Time format used for samples
    TIME_FORMAT = '%H:%M:%S'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        # Time elapsed since last sample was recorded
        self._elapsedSec = self.SAMPLE_PERIOD_SEC

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
                  tempC,
                  self.brewer.config.targetTemperatureCelsius,
                  1 if self.brewer.relayPin.output else 0
        )

        # Insert into database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO samples VALUES (?,?,?,?,?)', sample)

        # Reset time
        self._elapsedSec = 0

    def getRecords(self):
        '''
        Get records by day

        @return List of dates we have records for. Dates are encoded in self.DATE_FORMAT format 

        TODO: Return a class of records instead of a date string
        '''

        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                return [i[0] for i in cursor.execute('SELECT distinct(date) from samples ORDER BY date DESC').fetchall()]

    def getSamples(self, date):
        '''
        Get recorded samples for given date

        @param date: Date encoded in self.DATE_FORMAT format
        @return: List of samples
        '''

        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                return [(date, time, temperature, target, relay) for date, time, temperature, target, relay in cursor.execute('SELECT date, time, temperature, target, relay FROM samples WHERE date=? ORDER BY time ', (date,)).fetchall()
                           if temperature != TemperatureSensor.TEMP_INVALID_C]

    def onStart(self):
        # Create table if it does not exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS samples
                            (date text, time text, temperature real, target real, relay integer)''')
