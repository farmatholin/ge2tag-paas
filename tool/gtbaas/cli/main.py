import argparse

import sys
import logging

from gtbaas.gt_tool import GtTool

"""
Main function

# todo: cli dispatcher
# todo: runner cmd
#
"""

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


def main():
    try:
        dispatch()
    except KeyboardInterrupt:
        sys.exit(1)
    except AttributeError as e:
        log.error("command '{}' exist".format(sys.argv[1:2][0]))
        sys.exit(1)
    sys.exit(0)


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

    # Disable requests logging
    logging.getLogger("requests").propagate = False


def dispatch():
    setup_logging()
    dispatcher = Dispatcher()
    command, options = dispatcher.parse(sys.argv[1:])

    return command(options)


class Dispatcher(object):
    def __init__(self):
        self.tool = GtTool()

    """
    Parse commands from args and return command to start
    """

    def parse(self, args):
        cmd = args[0]

        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--ports')

        res = parser.parse_args(args[1:])

        return getattr(self, cmd), vars(res)

    """
    Start this app as server
    """

    def server(self, options):
        pass

    """
    Create docker-compose config and user folders
    """

    def create(self, options):
        self.tool.create(options['user'])

    """
    Start user geo2tag instance
    """

    def start(self, options):
        pass

    """
    Change user geo2tag instance
    """

    def change_settings(self, options):
        pass
