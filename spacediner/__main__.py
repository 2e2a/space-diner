import argparse
from . import cli
from . import settings

# TODO: dishes with 2 identical ingredients and one other not distinguishable from 1:2
# TODO: skills should have an effect and influence reviews
# TODO: make discovered preferences available in compendium
# TODO: toggle tutorial mode on/off (after first day)
# TODO: Fix output that plural is not needed
# TODO: log all commands into file on exception
# TODO: after increasing/decreasing a skill: show bar again (#----); add "Now your knife skills include: ..."
# TODO: player can enter a name and will be addressed as "Chef [name]"
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
cli.run()
