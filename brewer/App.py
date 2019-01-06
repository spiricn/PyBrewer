import sys
import os
import threading
import logging
from Config import Config
from Brewer import Brewer
import argparse
from brewer import __version__ as appVersion
import traceback

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

    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Configuration file path')

    args = parser.parse_args()

    with open(args.config, 'r') as fileObj:
        configDict = eval(fileObj.read())

    brewer = Brewer(Config(configDict))

    # Start application

    logger.debug('\n#################\nPyBrewer %s started, press CTRL+C to stop\n#################\n' % appVersion)

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
    brewer.logCritical(__name__, 'unhandled exception occurred:\n%s' %
        traceStr)

    os._exit(-1)


if __name__ == '__main__':
    # Register the global exception hook
    installThreadExcepthook()

    # Run the app
    sys.exit(main())

