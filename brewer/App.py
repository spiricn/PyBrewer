import sys
import os
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
            format='%(levelname)s/%(name)s: %(message)s')

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
    sys.excepthook = exceptionHook

    # Run the app
    sys.exit(main())

