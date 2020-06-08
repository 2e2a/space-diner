import argparse
from . import cli
from . import settings

# TODO: Catch Ctr+c, ask if exit
# TODO: guests: not necessarily one per group every day, two random guests instead
# TODO: shopping: consider removing "in stock" property
# TODO: skills should have an effect and influence reviews: "I was impressed by the chef's skills regarding X"
# TODO:   (X = one of the acquired subskills)
# TODO: make discovered preferences available in compendium
# TODO: toggle tutorial mode on/off (after first day)
# TODO: log all commands into file on exception
# TODO: after increasing/decreasing a skill: show bar again (#----); add "Now your knife skills include: ..."
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
