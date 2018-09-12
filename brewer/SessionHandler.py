import hashlib
from contextlib import closing
import logging
import random

from brewer.Handler import Handler

logger = logging.getLogger(__name__)


class SessionHandler(Handler):
    '''
    Handler used to create and authorize sessions
    '''

    # Main table name
    TABLE_SESSIONS = 'sessions'

    TABLE_USERS = 'users'

    # Salt used when generating session IDs
    SALT = 'pybrewsalt'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def createSession(self):
        '''
        Creates a new session
        '''

        # Generate an ID
        sessionId = self._generateSessionId()

        logger.debug('new session: %s' % sessionId)

        # Write to database
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO ' + self.TABLE_SESSIONS + ' VALUES (?,?)', (sessionId, 0))

        return sessionId

    def isSessionAuthorized(self, sessionId):
        '''
        Check if session is authorized
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT authorized FROM ' + self.TABLE_SESSIONS + ' WHERE id=?', (sessionId,)).fetchone()

                    return res and res[0] == 1

    def terminateSession(self, sessionId):
        '''
        Terminate a session
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('UPDATE ' + self.TABLE_SESSIONS + ' set authorized=0 WHERE id=?', (sessionId,))

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
                    res = cursor.execute('SELECT password from ' + self.TABLE_USERS + ' where username=?', (username,)).fetchone()
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
                    cursor.execute('UPDATE ' + self.TABLE_SESSIONS + ' set authorized=1 WHERE id=?', (sessionId,))

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
                            (id text, authorized integer)''')

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_USERS + '''
                            (username text, password text)''')
