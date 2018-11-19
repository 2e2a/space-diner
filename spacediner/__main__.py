import argparse
from . import cli
from . import levels
from . import settings
from . import time


parser = argparse.ArgumentParser(description='Space diner')
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Enable debug mode',
)
args = vars(parser.parse_args())
settings.read_args(args)
cli.init()
levels.load()
time.tick()
cli.run()
