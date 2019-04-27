import logging
from os.path import sys


class LoggingHandler(logging.Handler):
    def __init__(self, filePath):
        logging.Handler.__init__(self)

        self._filePath = filePath

        self._file = open(filePath, 'ab+')
        self._filePath

    @property
    def path(self):
        return self._filePath

    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno < logging.WARNING:
                stream = sys.stdout
            else:
                stream = sys.stderr
            fs = "%s\n"

            stream.write(fs % msg)
            stream.flush()

            self._file.write((fs % msg).encode('ascii'))
            self._file.flush()

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)