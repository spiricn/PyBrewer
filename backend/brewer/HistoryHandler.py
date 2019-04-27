from brewer.Handler import Handler
import datetime
import logging
from contextlib import closing
from brewer.HardwareHandler import HardwareHandler
from brewer.AComponent import ComponentType
from rpi.DS18B20.TemperatureSensor import TemperatureSensor
import sqlite3

logger = logging.getLogger(__name__)


class HistoryHandler(Handler):
    '''
    Handler which records temperature / controller / relay history
    '''

    # Component column value name prefix
    COMP_COLUMN_PREFIX = 'COMP_'

    # Sample recording rate
    SAMPLE_PERIOD_SEC = 30

    # Date format used for samples
    DATE_FORMAT = '%Y-%m-%d'

    # Time format used for samples
    TIME_FORMAT = '%H:%M:%S'

    DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

    # Samples table
    TABLE_SAMPLES = 'samples'

    # Sample date
    COL_DATE = 'date'

    # Sample time
    COL_TIME = 'time'

    # Sample actual temperature
    COL_VALUE = 'value'

    COL_COMPONENT = 'component'

    # Maximum sensor value to be considered valid
    MAX_VALID_SENSOR_VALUE = 9999

    # Default sensor value to be used in case reading was invalid
    DEFAULT_SENSOR_VALUE = 0

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

        sampleValues = [
            currentDate.strftime(self.DATE_FORMAT),
            currentDate.strftime(self.TIME_FORMAT),
        ]

        sampleColumns = [
            self.COL_DATE,
            self.COL_TIME
        ]

        sampleColumns += self._getComponentColumns()

        for component in self.brewer.getModule(HardwareHandler).getComponents():
            if component.componentType == ComponentType.SENSOR:
                value = component.getValue()
            elif component.componentType == ComponentType.SWITCH:
                value = 1.0 if component.isOn() else 0.0

            sampleValues.append(value)

        # Insert into database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO %s (%s) VALUES (%s)'
                                    % (self.TABLE_SAMPLES, ','.join(sampleColumns), ','.join(['?'] * len(sampleValues))),
                                    sampleValues
                    )

        # Reset time
        self._elapsedSec = 0

    def _getComponentColumns(self):
        sampleColumns = []

        for component in self.brewer.getModule(HardwareHandler).getComponents():
            sampleColumns.append(self._getComponentColumnName(component))

        return sampleColumns

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


    def getSamples(self, date=None):
        if date:
            startDate = datetime.datetime.strptime(date, self.DATE_FORMAT)
        else:
            startDate = datetime.datetime.now() - datetime.timedelta(hours=24)

        return self.getSamplesRange(startDate,
                                    startDate + datetime.timedelta(hours=24))

    def getSamplesRange(self, startDate, endDate):
        '''
        Get recorded samples for given date

        @param date: Date encoded in self.DATE_FORMAT format
        @return: List of samples
        '''

        with self.brewer.database as conn:
            with closing(conn.cursor()) as cursor:
                timeSamples = []

                samples = {}

                # List of component value columns
                compColumns = self._getComponentColumns()

                # Colum names we're querying
                columns = [self.COL_DATE, self.COL_TIME] + compColumns

                res = cursor.execute('''
                        SELECT %s

                        FROM %s

                        WHERE datetime(%s || " " || %s) BETWEEN ? and ? ORDER BY datetime(%s || " " ||  %s)'''
                            % (','.join(columns),
                                self.TABLE_SAMPLES,
                                self.COL_DATE, self.COL_TIME,
                                self.COL_DATE, self.COL_TIME
                                ),
                            (startDate.strftime(self.DATE_TIME_FORMAT), endDate.strftime(self.DATE_TIME_FORMAT))
                )

                for values in res.fetchall():
                    # Create time sample
                    timeSamples.append(values[0] + 'T' + values[1])

                    # Component values
                    compValues = values[2:]

                    # component names
                    compNames = [self._getComponentName(i) for i in compColumns]

                    # Create sample values
                    for index, compName in enumerate(compNames):
                        if compName not in samples:
                            samples[compName] = []


                        value = compValues[index]

                        if value >= self.MAX_VALID_SENSOR_VALUE:
                            # Invalid value, so use default value
                            value = self.DEFAULT_SENSOR_VALUE

                        samples[compName].append(value)

                return {'time' : timeSamples, 'samples' : samples}

    def onStart(self):
        # Create table if it does not exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    # Create base table
                    cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s text, %s text)'
                                   % (self.TABLE_SAMPLES, self.COL_DATE, self.COL_TIME)
                    )

                    # Add column for each component dynamically
                    for component in self.brewer.getModule(HardwareHandler).getComponents():
                        # Create column name from component name
                        name = self._getComponentColumnName(component)

                        # Add the column
                        try:
                            cursor.execute('ALTER TABLE %s ADD COLUMN %s REAL'
                                % ( self.TABLE_SAMPLES, name)
                            )
                        except sqlite3.OperationalError as e:
                            # Exception thrown if col already exists, probably not the best of solutions..
                            pass

    @staticmethod
    def _getComponentColumnName(component):
        '''
        Gets database column name for given component
        '''

        return HistoryHandler.COMP_COLUMN_PREFIX + component.id

    @staticmethod
    def _getComponentName(columName):
        '''
        Gets component name from given column name
        '''

        if not columName.startswith(HistoryHandler.COMP_COLUMN_PREFIX):
            raise RuntimeError('Invalid colum name %r' % columName)

        return columName[len(HistoryHandler.COMP_COLUMN_PREFIX):]