import argparse
from . import cli
from . import settings

# TODO: Trash food on close-up
# TODO: Do not allow to serve without taking the order first
# TODO: Remove bonding from groups
# TODO: Chatting with regulars: chat after serving; only available if satisfied...
# TODO: ...chatting always increases bonding, good answers only speed it up...
# TODO: ...reward level specifies necessary number of good answers...
# TODO: ...otherwise reward is triggered after all questions have been asked.
# TODO: personalize review texts per group
# TODO: not matching order -> max rating ok(2)
# TODO: toggle verbose mode on/off --> more/less info in output
# TODO: Plural of ingredients, food, etc.
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
