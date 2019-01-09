from brewer.Handler import Handler
import datetime
import logging
from contextlib import closing
from brewer.HardwareHandler import HardwareHandler
from brewer.AComponent import ComponentType
from rpi.DS18B20.TemperatureSensor import TemperatureSensor

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

    # Samples table
    TABLE_SAMPLES = 'samples'

    # Sample date
    COL_DATE = 'date'

    # Sample time
    COL_TIME = 'time'

    # Sample actual temperature
    COL_VALUE = 'value'

    COL_COMPONENT = 'component'

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

        # Get current time
        currentDate = datetime.datetime.now()

        for component in self.brewer.getModule(HardwareHandler).getComponents():

            if component.componentType == ComponentType.SENSOR:
                value = component.getValue()
            elif component.componentType == ComponentType.SWITCH:
                value = 1.0 if component.isOn() else 0.0

            # Create a temperature/seconds sample
            sample = (currentDate.strftime(self.DATE_FORMAT),
                      currentDate.strftime(self.TIME_FORMAT),
                      value,
                      component.name
            )

            # Insert into database
            with self.brewer.database as conn:
                with conn:
                    with closing(conn.cursor()) as cursor:
                        cursor.execute('INSERT INTO %s VALUES (?,?,?,?)'
                                        % (self.TABLE_SAMPLES,),
                                        sample
                        )

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
                return [i[0] for i in cursor.execute('SELECT distinct(%s) from %s ORDER BY %s DESC'
                                                     % (self.COL_DATE, self.TABLE_SAMPLES, self.COL_DATE)
                ).fetchall()]

    def getSamples(self, date):
        '''
        Get recorded samples for given date

        @param date: Date encoded in self.DATE_FORMAT format
        @return: List of samples
        '''

        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                res = cursor.execute('SELECT DISTINCT(%s) FROM %s WHERE %s=? ORDER BY %s'
                  % (self.COL_COMPONENT, self.TABLE_SAMPLES, self.COL_DATE, self.COL_TIME),
                  (date,)
                )

                components = [i[0] for i in res.fetchall()]

                timeSamples = []

                samples = {}

                for index, component in enumerate(components):
                    res = cursor.execute('''
                            SELECT %s, %s, 
                            CASE
                                WHEN %s > 9999 THEN 0
                            ELSE %s
                            END

                            FROM %s WHERE %s=? AND %s=? ORDER BY %s'''
                                % (self.COL_DATE, self.COL_TIME, self.COL_VALUE, self.COL_VALUE, self.TABLE_SAMPLES, self.COL_DATE, self.COL_COMPONENT, self.COL_TIME),
                                (date, component,)
                    )
#
                    samples[component] = []

                    for date, time, value in res.fetchall():
                        if index == 0:
                            timeSamples.append(date + 'T' + time)

                        samples[component].append(value);

                return {'time' : timeSamples, 'samples' : samples}

    def onStart(self):
        # Create table if it does not exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s text, %s text, %s real, %s text)'
                                   % (self.TABLE_SAMPLES, self.COL_DATE, self.COL_TIME, self.COL_VALUE, self.COL_COMPONENT)
                    )
