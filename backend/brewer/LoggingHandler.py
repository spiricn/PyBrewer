import logging
from os.path import sys


class LoggingHandler(logging.Handler):
    '''
    Application logging handler. All the logger.* calls go trough this
    '''

    def __init__(self, filePath):
        logging.Handler.__init__(self)

        self._filePath = filePath

        # Open log file
        self._file = open(filePath, 'ab+')

    @property
    def path(self):
        '''
        Log file path
        '''

        return self._filePath

    def emit(self, record):
        try:
            # Format message
            msg = self.format(record)

            # Pick stream based on level
            if record.levelno < logging.WARNING:
                stream = sys.stdout
            else:
                stream = sys.stderr
            fs = "%s\n"

            # Write to stream
            stream.write(fs % msg)
            stream.flush()

            # Write to file
            self._file.write((fs % msg).encode('ascii'))
            self._file.flush()

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
