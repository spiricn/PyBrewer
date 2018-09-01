from brewer.Handler import Handler
import logging
from contextlib import closing
import datetime

logger = logging.getLogger(__name__)


class LogHandler(Handler):
    TABLE_LOGS = 'logs'

    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def update(self, elapsedTime):
        pass

    def log(self, level, module, message):
        logger.log(level, '[%s] %s' % (module, message))

        time = datetime.datetime.now().strftime(self.TIME_FORMAT)

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

                    return [(level, module, message, datetime.datetime.strptime(time, self.TIME_FORMAT)) for level, module, message, time in cursor.execute('''SELECT * FROM ''' + self.TABLE_LOGS).fetchall()]

    def onStart(self):
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                            (level integer, module text, message text, time text)''' % self.TABLE_LOGS)

        self.log(logging.INFO, __name__, 'Session start')

    def onStop(self):
        pass
