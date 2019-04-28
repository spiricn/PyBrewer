import sys
import os
import threading
import logging
import argparse
import traceback


from brewer.Config import Config
from brewer.Brewer import Brewer
from brewer.Utils import Utils

logger = logging.getLogger(__name__)


def signalHandler(sig, frame):
    global brewer

    logger.debug('stopping ..')

    brewer.stop()


def main():
    '''
    Main app entry point
    '''

    global brewer

    config = Config()

    # Create home directory if it doesn't exist
    if not os.path.isdir(config.home):
        print('creating home dir: %r' % config.home)
        os.mkdir(config.home)

    if not os.path.isfile(config.configPath):
        # Create default config file if it doesn't exist
        print('creating config file: %r' % config.configPath)
        config.serialize()
    else:
        # Deserialize config file
        try:
            config.deserialize()
        except Exception as e:
            print('Error parsing config file %r: %r' % (config.configPath, str(e)))
            return -1

    # Instantiate brewer
    brewer = Brewer(config)

    # Start application
    logger.debug('\n#################\nPyBrewer started, press CTRL+C to stop\n#################\n')

    brewer.start()

    return brewer.wait()


def installThreadExcepthook():
    '''
    Workaround for sys.excepthook thread bug
    (https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470).
    Call once from __main__ before creating any threads.
    If using psyco, call psycho.cannotcompile(threading.Thread.run)
    since this replaces a new-style class method.
    '''
    runOld = threading.Thread.run

    def run(*args, **kwargs):
        try:
            runOld(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            sys.excepthook(*sys.exc_info())

    threading.Thread.run = run

    sys.excepthook = exceptionHook


def exceptionHook(exctype, value, tb):
    '''
    Global unhandled exception hook, it catches unhandled exceptions
    logs them, and exists the application
    '''

    traceStr = ''.join(traceback.format_exception(exctype, value, tb))

    message = 'unhandled exception occurred:\n' + traceStr

    try:
        # Log fatal message
        brewer.logCritical(__name__, message)
    except NameError:
        # App not yet initialized, so just print
        print(message)

    os._exit(-1)


if __name__ == '__main__':
    # Register the global exception hook
    installThreadExcepthook()

    # Run the app
    sys.exit(main())

