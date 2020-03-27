import argparse
from . import cli
from . import settings

# TODO: make discovered preferences available in compendium
# TODO: property matches in substring, e.g. fried = deep-fried
# TODO: toggle verbose mode on/off --> more/less info in output
# TODO: Fix output that plural is not needed
# TODO: log all commands into file on exception

parser = argparse.ArgumentParser(description='Space diner')
parser.add_argument(
    '-l', '--log',
    action='store_true',
    help='Log game input into separate file.',
)
args = vars(parser.parse_args())
settings.read_args(args)
cli.init()
cli.run()
