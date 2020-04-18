import argparse
from . import cli
from . import settings

# TODO: make discovered preferences available in compendium
# TODO: property matches in substring, e.g. fried = deep-fried
# TODO: toggle tutorial mode on/off (after first day)
# TODO: Fix output that plural is not needed
# TODO: log all commands into file on exception
# TODO: enable saving recipes again
# TODO: introduce menu: select recipes for menu, guests will sometimes order something from the menu
# TODO: weekly menu, can be edited on first day of the week
# TODO: after increasing/decreasing a skill: show bar again (#----); add "Now your knife skills include: ..."
# TODO: player can enter a name and will be addressed as "Chef [name]"
# TODO: make defining regulars optional
# TODO: sometimes broken: NameFactory create (some names cause a problem?)
# TODO: make skills available on specific days
# TODO: special weekend day (last day of the week) with two activities instead of work and one activity
# TODO: think about menu: are all/some initial menu items fixed?
# TODO: (diner) temperature can be adjusted - some guests like it cold/medium/hot (affects ambience)
# TODO: interior design mode: buying new furniture, pleases some customers (matched by name or properties like fancy)

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
