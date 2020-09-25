import argparse
from . import cli
from . import settings

# TODO: bug: in reviews: "I liked None" / "I disliked None" (sth wrong with properties)
# TODO: bug: showing recipe crashes (sth wrong with properties)
# TODO: completer: remove underscore, use separate command parts instead
# TODO: completer: support simple string command parts
# TODO: completer: ignore capitalization and special characters before matching (see name_for_command)
# TODO: get rid of actions :(
# TODO: enter should do nothing instead of printing help
# TODO: check if rewards by normal guests are possible
# TODO: bug: sometimes prepared ingredients appear in the kitchen although they were already served
# TODO: make discovered preferences available in compendium
# TODO: toggle tutorial mode on/off (after first day)
# TODO: log all commands into file on exception
# TODO: check non-ascii characters in name factories
# TODO: sometimes broken: NameFactory create (some names cause a problem?)
# TODO: make activities available on specific days
# TODO: special weekend day (last day of the week) with two activities instead of work and one activity
# TODO: think about menu: are all/some initial menu items fixed?
# TODO: rewards/trophies for achievements, e.g., served 100 dishes, received 100 reviews

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
