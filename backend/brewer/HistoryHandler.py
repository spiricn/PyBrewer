from brewer.Handler import Handler
import datetime
import logging
from contextlib import closing
from brewer.HardwareHandler import HardwareHandler
from brewer.AComponent import ComponentType
from rpi.DS18B20.TemperatureSensor import TemperatureSensor
import sqlite3
from collections import namedtuple

logger = logging.getLogger(__name__)

Event = namedtuple('Event', 'id, name, time')

class HistoryHandler(Handler):
    '''
    Handler which records hardware component state history periodically. These samples may later be retreived to be graphed.
    '''

    # Component column value name prefix
    COMP_COLUMN_PREFIX = 'COMP_'

    # Sample recording rate
    SAMPLE_PERIOD_SEC = 30

    # Date format used for samples
    DATE_FORMAT = '%Y-%m-%d'

    # Time format used for samples
    TIME_FORMAT = '%H:%M:%S'

    # Date / time format used for samples
    DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

    # Samples table
    TABLE_SAMPLES = 'samples'

    # Sample date
    COL_DATE = 'date'

    # Sample time
    COL_TIME = 'time'

    # Sample actual temperature
    COL_VALUE = 'value'

    # Events table
    TABLE_EVENTS = 'events'

    # Event name
    COL_EVENT_NAME = 'name'

    # Event ID
    COL_EVENT_ID = 'id'

    # Maximum sensor value to be considered valid
    MAX_VALID_SENSOR_VALUE = 9999

    # Default sensor value to be used in case reading was invalid
    DEFAULT_SENSOR_VALUE = 0

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

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

        # Sample values which will be inserted into the table (start with time/date)
        sampleValues = [
            currentDate.strftime(self.DATE_FORMAT),
            currentDate.strftime(self.TIME_FORMAT),
        ]

        # Sample columns which will be inserted into the table
        sampleColumns = [
            self.COL_DATE,
            self.COL_TIME
        ]

        # Add hardware component columns dynamically
        sampleColumns += self._getComponentColumns()

        # Get values for each component
        for component in self.brewer.getModule(HardwareHandler).getComponents():
            if component.componentType == ComponentType.SENSOR:
                # Just use sensor read value
                value = component.getValue()
            elif component.componentType == ComponentType.SWITCH:
                # For switches convert on state to 1 or 0
                value = 1.0 if component.isOn() else 0.0
            else:
                raise RuntimeError('Component type support not implemented')

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
        '''
        Get column names for hardware components dynamically
        '''

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

                        if value == None or value >= self.MAX_VALID_SENSOR_VALUE:
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

                    cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s integer primary key autoincrement, %s text, %s text)'
                                    % ( self.TABLE_EVENTS, self.COL_EVENT_ID, self.COL_EVENT_NAME, self.COL_TIME)
                    )

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

    def createEvent(self, name):
        '''
        Create an event with given name

        @param name Event name
        @return Event object
        '''

        currentTime = datetime.datetime.now().strftime(self.DATE_TIME_FORMAT)

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO %s (%s, %s) VALUES(?,?)'
                        % (self.TABLE_EVENTS, self.COL_EVENT_NAME, self.COL_TIME), (name, currentTime)
                    )

                    return Event(cursor.lastrowid, name, currentTime)

    def getEvent(self, eventId):
        '''
        Get an event with given ID

        @param eventId Event ID
        @return Event object if successful, None otherwise
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('SELECT * FROM %s WHERE %s=?'
                        % ( self.TABLE_EVENTS, self.COL_EVENT_ID), (eventId,)
                    )

                    res = cursor.fetchone()

                    if not res:
                        return None

                    return Event(res[0], res[1], res[2])

    def updateEvent(self, eventId, name, time):
        '''
        Update event with given ID

        @param eventId Event ID
        @param name New name
        @param time New time
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('UPDATE %s set %s=?, %s=? WHERE %s=?'
                        % ( self.TABLE_EVENTS, self.COL_EVENT_NAME, self.COL_TIME, self.COL_EVENT_ID), (name, time, eventId)
                    )

    def deleteEvent(self, eventId):
        '''
        Delete event with given ID

        @param eventId Event ID
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('DELETE FROM %s WHERE %s=?'
                        % (self.TABLE_EVENTS, self.COL_EVENT_ID), (eventId,)
                    )

    def getEvents(self):
        '''
        Get all available events

        @param list of events
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('SELECT * FROM %s'
                        % self.TABLE_EVENTS
                    )

                    events = []

                    for res in cursor.fetchall():
                        events.append(Event(res[0], res[1], res[2]))

                    return events
