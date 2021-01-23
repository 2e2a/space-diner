import argparse
from . import cli
from . import settings

# TODO: rewards/trophies for achievements, e.g., served 10/50/100 dishes, received 10/50/100 positive reviews...
# TODO: bug: skill level can exceed maximum
# TODO: show ingredient properties in the kitchen, e.g., cow milk [milk, animal product]
#
# TODO: check if rewards by normal guests are possible
# TODO: bug: sometimes prepared ingredients appear in the kitchen although they were already served
# TODO: toggle tutorial mode on/off (after first day)
# TODO: check non-ascii characters in name factories
# TODO: sometimes broken: NameFactory create (some names cause a problem?)
# TODO: make activities available on specific days
# TODO: special weekend day (last day of the week) with two activities instead of work and one activity
# TODO: think about menu: are all/some initial menu items fixed?

parser = argparse.ArgumentParser(description='Space diner')
parser.add_argument(
    '-l', '--log',
    action='store_true',
    help='Log game input into separate file.',
)
args = vars(parser.parse_args())
settings.read_args(args)
cli.init()
cli.run(args)
