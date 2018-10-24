settings = {
    'debug': False,
}


def read_args(args):
    global settings
    settings.update(**args)

    for k, v in settings.items():
        globals()[k.upper()] = v
