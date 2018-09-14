import hashlib
from contextlib import closing
import logging
import random
import datetime
from collections import namedtuple

from brewer.Handler import Handler

logger = logging.getLogger(__name__)

Session = namedtuple('Session', 'id authorized expires maxAge')


class SessionHandler(Handler):
    '''
    Handler used to create and authorize sessions
    '''

    # Main table name
    TABLE_SESSIONS = 'sessions'

    TABLE_USERS = 'users'

    # Salt used when generating session IDs
    SALT = 'pybrewsalt'

    # Duration of session
    SESSION_DURATION_SEC = 1 * 60 * 60 * 24  # 1 day

    # Time format
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    COL_ID = 'id'
    COL_AUTHORIZED = 'authorized'
    COL_EXPIRES = 'expires'

    COL_USERNAME = 'username'
    COL_PASSWORD = 'password'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def createSession(self):
        '''
        Creates a new session
        '''

        # Generate an ID
        sessionId = self._generateSessionId()

        expires = (datetime.datetime.now() + datetime.timedelta(0, self.SESSION_DURATION_SEC)).strftime(self.TIME_FORMAT)

        # Write to database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO ' + self.TABLE_SESSIONS + ' VALUES (?,?,?)', (sessionId, 0, expires))

        return self.getSession(sessionId)

    def getSession(self, sessionId):
        '''
        Check if session is authorized
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT ' + self.COL_ID + ', ' + self.COL_AUTHORIZED + ', ' + self.COL_EXPIRES + ' FROM ' + self.TABLE_SESSIONS + ' WHERE ' + self.COL_ID + '=?', (sessionId,)).fetchone()

                    if not res:
                        logger.debug('session does not exist %r' % sessionId)
                        return None

                    expires = datetime.datetime.strptime(res[2], self.TIME_FORMAT)

                    if datetime.datetime.now() > expires:
                        logger.debug('session expired')

                        cursor.execute('DELETE FROM ' + self.TABLE_SESSIONS + ' WHERE ' + self.COL_ID + '=?', (sessionId,)).fetchone()

                        return None

                    return Session(res[0],
                                   res[1],
                                   expires,
                                   SessionHandler.SESSION_DURATION_SEC
                     )

    def terminateSession(self, sessionId):
        '''
        Terminate a session
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    rc = cursor.execute('UPDATE ' + self.TABLE_SESSIONS + ' SET ' + self.COL_AUTHORIZED + '=0 WHERE ' + self.COL_ID + '=?', (sessionId,)).rowcount
                    if rc != 1:
                        logger.error('update failed: %d != 1' % rc)
                        return False

                    logger.debug('terminated session')

                    return True

    def authorizeSession(self, sessionId, username, password):
        '''
        Attempt to authorize a session

        @param sessionId: Session ID
        @param username: Username username
        @param password: User Password

        @return: True if authorized successfully, False otherwise
        '''

        # Hash the password
        password = SessionHandler._hash(password)

        # Check if there are any users in the database, if not create one with this username/password combo
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    numUsers = cursor.execute('SELECT COUNT(*) from ' + self.TABLE_USERS).fetchone()[0]

                    if numUsers == 0:
                        logger.debug('creating new user %r' % username)

                        # Create user
                        cursor.execute('INSERT INTO ' + self.TABLE_USERS + ' VALUES (?,?)', (username, password))

        # Verify if a user with this username and password exists
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT ' + self.COL_PASSWORD + ' from ' + self.TABLE_USERS + ' WHERE ' + self.COL_USERNAME + '=?', (username,)).fetchone()
                    if not res:
                        logger.error('invalid username')
                        return False

                    if res[0] != password:
                        logger.error('invalid password')
                        return False

        # Authorize the user
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    rc = cursor.execute('UPDATE ' + self.TABLE_SESSIONS + ' SET ' + self.COL_AUTHORIZED + '=1 WHERE ' + self.COL_ID + '=?', (sessionId,)).rowcount

                    if rc != 1:
                        logger.error('update failed: %d != 1 for session %r' % (rc, sessionId))
                        return False

                    logger.debug('authorized session')

                    return True

    @staticmethod
    def _generateSessionId():
        '''
        Generate a random session ID

        @return: Session ID
        '''

        return SessionHandler._hash(str(random.random()))

    @staticmethod
    def _hash(value):
        md5 = hashlib.md5()

        # Session ID is a salted MD5 hash of a random number
        md5.update((value + SessionHandler.SALT).encode('utf-8'))

        return md5.hexdigest()

    def onStart(self):
        # Create table if it does not exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_SESSIONS + '''
                            (''' + self.COL_ID + ''' text, ''' + self.COL_AUTHORIZED + ''' integer, ''' + self.COL_EXPIRES + ''' text)''')

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_USERS + '''
                            (''' + self.COL_USERNAME + ' text, ''' + self.COL_PASSWORD + ''' text)''')
