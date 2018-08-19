import sys
import logging
from Config import Config
from Brewer import Brewer


def main():
    '''
    Main app entry point
    '''

    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
            format='%(levelname)s/%(name)s: %(message)s')
    logger = logging.getLogger(__name__)

    # TODO Read configuration from command line arguments
    brewer = Brewer(Config(8080, '../app', 25.0))

    # Start application
    brewer.start()

    return brewer.wait()


if __name__ == '__main__':
    sys.exit(main())

