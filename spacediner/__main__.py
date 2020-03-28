import argparse
from . import cli
from . import settings

# TODO: make discovered preferences available in compendium
# TODO: property matches in substring, e.g. fried = deep-fried
# TODO: toggle verbose mode on/off --> more/less info in output
# TODO: Fix output that plural is not needed
# TODO: log all commands into file on exception
# TODO: enable saving recipes again
# TODO: allow to edit which properties are part of the recipe (e.g., ingredient, preparation)
# TODO: introduce menu: select recipes for menu, guests will sometimes order something from the menu
# TODO: (diner) temperature can be adjusted - some guests like it cold/medium/hot (affects ambience)
# TODO: furniture shopping --> affects ambience

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
