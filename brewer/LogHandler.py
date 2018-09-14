from brewer.Handler import Handler
import logging
from contextlib import closing
import datetime
import html
from brewer.PushNotifications import PushNotifications

logger = logging.getLogger(__name__)


class LogHandler(Handler):
    '''
    Handlers which stores logs into the database, and reads them

    Only the most important logs (which are of concern to the end user) should go trough this handler
    '''

    # Main table name
    TABLE_LOGS = 'logs'

    # Time format used to encode time in
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    # Maximum number of notifications this handler can generate in one day
    MAX_DAILY_NOTIFICATIONS = 50

    # Log level
    COL_LEVEL = 'level'

    # Log source module
    COL_MODULE = 'module'

    # Log message
    COL_MESSAGE = 'message'

    # Log timestamp
    COL_TIME = 'time'

    # Log level considered worthy of a push notification
    PUSH_NOTIFICATION_LEVELS = [logging.ERROR, logging.CRITICAL, logging.WARN]

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        # Date of last update
        self._lastDate = datetime.datetime.now()

        # Number of notifications sent today
        self._notificationsSent = 0

        # Instantiate push notifications handler
        self._pushNotifications = PushNotifications(
            self.brewer.config.pushoverUserToken, self.brewer.config.pushoverAppToken
        )

    def update(self, elapsedTime):
        # Get current  date & time
        currentDate = datetime.datetime.now()

        # Reset notification counter on day change
        if currentDate.day != self._lastDate.day:
            self.brewer.logDebug(__name__, 'removing notifications limit: %d != %d' % (currentDate.day, self._lastDate.day))

            self._lastDate = currentDate

            self._notificationsSent = 0

    def log(self, level, module, message):
        # Log the message to regular logger
        logger.log(level, '[%s] %s' % (module, message))

        # Get  current time
        time = datetime.datetime.now().strftime(self.TIME_FORMAT)

        # Send a push notification if conditions are met
        if level in self.PUSH_NOTIFICATION_LEVELS:
            if self._notificationsSent > self.MAX_DAILY_NOTIFICATIONS:
                self.brewer.logWarning(__name__, 'Max daily notifications exceeded')

            else:
                levelMap = {
                    logging.ERROR : 'ERROR',
                    logging.WARN: 'WARNING',
                    logging.CRITICAL : 'CRITICAL',

                }

                self._pushNotifications.sendNotification('%s: %s' % (levelMap[level], module),
                                                         message)
                self._notificationsSent += 1

        # Write the message to database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO %s VALUES (?,?,?,?)'
                                   % (self.TABLE_LOGS,),
                                   (level, module, message, time)
                    )

    def clear(self):
        '''
        Clears all the logs from the database
        '''

        logger.debug('clearing logs')

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('DELETE from %s'
                                   % (self.TABLE_LOGS,)
                     )

        return True

    def getLogs(self):
        '''
        Gets all the logs from database
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    # Parse the time/date and HTML escape the message
                    return [(level, module, html.escape(message), datetime.datetime.strptime(time, self.TIME_FORMAT))
                             for level, module, message, time in cursor.execute('SELECT * FROM %s ORDER BY %s DESC'
                                                                                % (self.TABLE_LOGS, self.COL_TIME)
                             ).fetchall()]

    def getNumErrors(self):
        '''
        Get number of errors in the database

        TODO: Make a generic version of this
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    return cursor.execute('SELECT COUNT(*) FROM %s WHERE %s IN (?,?)'
                                          % (self.TABLE_LOGS, self.COL_LEVEL),
                                          (logging.ERROR, logging.CRITICAL)
                     ).fetchone()[0]

    def getLatestError(self):
        '''
        Get latest error message

        TODO: Make a generic version of this

        @return: Date when the last error message happened
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT %s FROM %s WHERE %s IN (?,?) ORDER BY %s DESC LIMIT 1'
                                         % (self.COL_TIME, self.TABLE_LOGS, self.COL_LEVEL, self.COL_TIME),
                                         (logging.ERROR, logging.CRITICAL)
                    ).fetchone()
                    if not res:
                        return None

                    # Parse date
                    return datetime.datetime.strptime(res[0], self.TIME_FORMAT)

    def onStart(self):
        # Create log table if it doesn't exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s integer, %s text, %s text, %s text)'
                                   % (self.TABLE_LOGS, self.COL_LEVEL, self.COL_MODULE, self.COL_MESSAGE, self.COL_TIME)
                    )

        self.log(logging.INFO, __name__, 'Session start')

    def onStop(self):
        self.log(logging.INFO, __name__, 'Session stop')
