import argparse
import logging

import sys

from gtbaas.gt_tool import GtTool, InitError
from gtbaas.server.server import run_server, MyDaemon

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
    except CommandExistError as e:
        log.error("command '{}' exist".format(sys.argv[1:2][0]))
        sys.exit(1)
    except InitError as e:
        log.error("Run init first")
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
        parser.add_argument('-c', '--container')
        parser.add_argument('--cpu-quota', default=25000)
        parser.add_argument('--mem-limit', default='150M')
        parser.add_argument('--cpu-shares', default=50)
        parser.add_argument('-p', '--port')
        parser.add_argument('-d', '--daemon', action='store_true')
        parser.add_argument('-s', '--stop', action='store_true')

        res = parser.parse_args(args[1:])
        try:
            handler = getattr(self, cmd)
        except AttributeError:
            raise CommandExistError

        return handler, vars(res)

    """
    Start this app as server
    """

    def server(self, options):
        self.tool.init_check()
        if options['daemon']:
            daemon = MyDaemon('/tmp/gttool.pid', options['port'])
            if options['stop']:
                daemon.stop()
            else:
                daemon.start()
        else:
            run_server(options['port'])

    """
    Create docker-compose config and user folders
    """

    def create(self, options):
        self.tool.init_check()
        self.tool.create(
            options['user'],
            options['container'],
            options['cpu_shares'],
            options['cpu_quota'],
            options['mem_limit']
        )

    def remove(self, options):
        self.tool.init_check()
        self.tool.delete(options['user'], options['container'])

    """
    Start user geo2tag instance
    """

    def start(self, options):
        self.tool.init_check()
        self.tool.start(options['user'], options['container'])

    """
        Start user geo2tag instance
        """

    def stop(self, options):
        self.tool.init_check()
        self.tool.stop(options['user'], options['container'])

    """
    Change user geo2tag instance
    """

    def change_settings(self, options):
        self.tool.init_check()

    """
    Check container and folders
    """

    def init(self, options):
        self.tool.init()


class CommandExistError(Exception):
    pass
