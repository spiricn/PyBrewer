from brewer.Handler import Handler
from contextlib import closing


class SettingsHandler(Handler):
    '''
    Key/value sqlite settings backend.
    
    NOTE: Implementing this in SQL may not be the best of ideas, however
    since we want to store everything inside of a single database, and protect against unexpected
    power interruptions, this seemed like the safest way of doing things.
    '''

    TABLE_SETTINGS = 'settings'

    COL_KEY = 'key'
    COL_VALUE = 'value'

    def __init__(self, brewer):
        Handler.__init__(self, brewer)

    def putBoolean(self, key, value):
        '''
        Save a boolean value

        @param key: Key
        @param value: Value
        '''

        self._put(key, value)

    def getBoolean(self, key, defaultValue=False):
        '''
        Get a boolean value

        @param key: Key
        @param defaultValue: Default value

        @return: Actual value or defaultValue if entry doesn't exist 
        '''

        return self._get(key, defaultValue) == str(True)

    def putString(self, key, value):
        '''
        Save a stringvalue

        @param key: Key
        @param value: Value
        '''

        self._put(key, value)

    def getString(self, key, defaultValue=''):
        '''
        Get a string value

        @param key: Key
        @param defaultValue: Default value

        @return: Actual value or defaultValue if entry doesn't exist 
        '''

        return self._get(key, defaultValue)

    def putFloat(self, key, value):
        '''
        Save an integer value

        @param key: Key
        @param value: Value
        '''

        self._put(key, value)

    def getFloat(self, key, defaultValue=0.0):
        '''
        Get an integer value

        @param key: Key
        @param defaultValue: Default value

        @return: Actual value or defaultValue if entry doesn't exist 
        '''

        return float(self._get(key, defaultValue))

    def putInteger(self, key, value):
        '''
        Save an integer value

        @param key: Key
        @param value: Value
        '''

        self._put(key, value)

    def getInteger(self, key, defaultValue=0):
        '''
        Get an integer value

        @param key: Key
        @param defaultValue: Default value

        @return: Actual value or defaultValue if entry doesn't exist 
        '''

        return int(self._get(key, defaultValue))

    def _get(self, key, defaultValue=None):
        '''
        Get a key value pair from database

        @param key: Key
        @param defaultValue: Value returned if entry does not exist

        @return: value with corresponding key or default value if it doesn't exist  
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    res = cursor.execute('SELECT %s from %s where %s=?'
                                   % (self.COL_VALUE, self.TABLE_SETTINGS, self.COL_KEY),
                                   (key,)
                    ).fetchone()

                    if not res:
                        return defaultValue

                    return res[0]

    def _put(self, key, value):
        '''
        Put a key/value pair into database

        @param key: Key
        @param value: Value  
        '''

        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    # Delete old value
                    cursor.execute('DELETE FROM %s WHERE %s=?'
                                   % (self.TABLE_SETTINGS, self.COL_KEY),
                                   (key,)
                    )

                    # Insert new one
                    cursor.execute('INSERT OR REPLACE INTO %s (%s, %s) VALUES (?,?)'
                                   % (self.TABLE_SETTINGS, self.COL_KEY, self.COL_VALUE),
                                   (key, str(value))
                    )

    def onStart(self):
        # Create settings table if it doesn't exist
        with self.brewer.database as conn:
            with conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s text, %s text)'
                                   % (self.TABLE_SETTINGS, self.COL_KEY, self.COL_VALUE)
                    )
