settings = {
    'log': False,
    'text_only': False,
}


def text_only():
    return settings.get('text_only')


def read_args(args):
    global settings
    settings.update(**args)
    for k, v in settings.items():
        globals()[k.upper()] = v
