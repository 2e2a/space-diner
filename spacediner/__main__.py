import argparse
from . import cli
from . import settings

# TODO: only cooking+service mode, remove diner mode, most commands always available
# TODO: hygiene = number decreasing after x days, cleaning increase
# TODO: evening activities increase skills, e.g., cleaning --> ambience
# TODO: regulars do not come every day, weekdays
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
