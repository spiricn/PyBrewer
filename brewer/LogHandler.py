from brewer.Handler import Handler
import logging
from contextlib import closing
import datetime
import html
from brewer.PushNotifications import PushNotifications

logger = logging.getLogger(__name__)


class LogHandler(Handler):
    TABLE_LOGS = 'logs'

    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    MAX_DAILY_NOTIFICATIONS = 50

    PUSH_NOTIFICATION_LEVELS = [logging.ERROR, logging.CRITICAL, logging.WARN]

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

        self._lastDate = datetime.datetime.now()

        self._notificationsSent = 0

        # Push notifications
        self._pushNotifications = PushNotifications(self.brewer.config.pushoverUserToken, self.brewer.config.pushoverAppToken)

    def update(self, elapsedTime):
        currentDate = datetime.datetime.now()

        if currentDate.day != self._lastDate.day:
            self.brewer.logDebug(__name__, 'removing notifications limit: %d != %d' % (currentDate.day, self._lastDate.day))

            self._lastDate = currentDate

            self._notificationsSent = 0

    def log(self, level, module, message):
        logger.log(level, '[%s] %s' % (module, message))

        time = datetime.datetime.now().strftime(self.TIME_FORMAT)

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

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''INSERT INTO ''' + self.TABLE_LOGS + '''
                        VALUES (?,?,?,?)''', (level, module, message, time))

    def clear(self):
        logger.debug('clearing logs')

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''DELETE from ''' + self.TABLE_LOGS)

        return True

    def getLogs(self):
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:

                    return [(level, module, html.escape(message), datetime.datetime.strptime(time, self.TIME_FORMAT))
                             for level, module, message, time in cursor.execute('''SELECT * FROM ''' + self.TABLE_LOGS + ''' ORDER BY time DESC''').fetchall()]

    def getNumErrors(self):
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    return cursor.execute('SELECT COUNT(*) FROM ' + self.TABLE_LOGS + ' WHERE level IN (?,?)', (logging.ERROR, logging.CRITICAL)).fetchone()[0]

    def getLatestError(self):
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT time from ' + self.TABLE_LOGS + ' WHERE level IN (?,?) ORDER BY time DESC LIMIT 1', (logging.ERROR, logging.CRITICAL)).fetchone()
                    if not res:
                        return None

                    return datetime.datetime.strptime(res[0], self.TIME_FORMAT)

    def onStart(self):
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                            (level integer, module text, message text, time text)''' % self.TABLE_LOGS)

        self.log(logging.INFO, __name__, 'Session start')

    def onStop(self):
        self.log(logging.INFO, __name__, 'Session stop')
