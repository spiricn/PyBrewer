import sys
import logging
from Config import Config
from Brewer import Brewer
import argparse
import json
import signal
from brewer import __version__ as appVersion

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
        configDict = json.load(fileObj)

    brewer = Brewer(Config(configDict))

    # Start application

    logger.debug('\n#################\nPyBrewer %s started, press CTRL+C to stop\n#################\n' % appVersion)

    brewer.start()

    return brewer.wait()


if __name__ == '__main__':
    # Register signal handler (to stop on CTRL+C)
    signal.signal(signal.SIGINT, signalHandler)

    sys.exit(main())

