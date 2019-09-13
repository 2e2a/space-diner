import argparse
from . import cli
from . import settings

# TODO: Use separate command for chat and take_order
# TODO: Show bonding somewhere?
# TODO: Socializing with regulars: they propose meeting (evening activity) when satisfied
# TODO: ...meeting always increases bonding, good answers only speed it up...
# TODO: ...reward level specifies necessary number of good answers...
# TODO: ...otherwise reward is triggered after all questions have been asked.
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
