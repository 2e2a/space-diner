settings = {
    'debug': False,
}


def read_args(args):
    global settings
    settings.update(**args)
