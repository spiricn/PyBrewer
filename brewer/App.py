import sys
import logging
from Config import Config
from Brewer import Brewer
import argparse
import json


def main():
    '''
    Main app entry point
    '''

    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
            format='%(levelname)s/%(name)s: %(message)s')
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Configuration file path')

    args = parser.parse_args()

    with open(args.config, 'r') as fileObj:
        configDict = json.load(fileObj)

    # TODO Read configuration from command line arguments
    brewer = Brewer(Config(configDict))

    # Start application
    brewer.start()

    return brewer.wait()


if __name__ == '__main__':
    sys.exit(main())

