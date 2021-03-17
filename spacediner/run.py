import argparse

from spacediner import cli, levels, settings


def run(dev=False):
    parser = argparse.ArgumentParser(description='Space diner')
    parser.add_argument(
        '-l', '--log',
        action='store_true',
        help='Log game input into separate file.',
    )
    args = vars(parser.parse_args())
    settings.read_args(args)
    levels.init()
    cli.init()
    cli.run(args)