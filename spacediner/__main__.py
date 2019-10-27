import argparse
from . import cli
from . import settings

# TODO: evening activities increase skills, e.g., cleaning --> ambience
# TODO: ratings depend on more than one value: e.g. taste + service + ambience
#       taste = whether they liked the food
#       service = whether they got what they ordered
#       ambience = how clean the diner is, decoration, etc.
# TODO: regulars do not come every day
# TODO: level intro text
# TODO: player can enter a diner name when starting a level
# TODO: output text when a reward is unlocked
# TODO: info-mode: <press ENTER>
# TODO: trash broken
# TODO: remove debug
# TODO: toggle verbose mode on/off --> more/less info in output
# TODO: Fix output that plural is not needed
# TODO: log all commands into file on exception
# TODO: customer distribution should depend on popularity (minimum 1 customer per group every day)

parser = argparse.ArgumentParser(description='Space diner')
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Enable debug mode',
)
args = vars(parser.parse_args())
settings.read_args(args)
cli.init()
cli.run()
