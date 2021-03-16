import os
import yaml
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from datetime import datetime


from levels import LEVELS
from . import activities
from . import cli
from . import diner
from . import food
from . import goals
from . import guests
from . import kitchen
from . import ingredients
from . import shopping
from . import social
from . import skills
from . import storage
from . import time


TYPE_LOCAL = 'local'
TYPE_PACKAGE = 'pkg'


class Level:
    name = None
    intro = None
    outro = None
    money = 0
    tutorial = False

    def init(self, filename, typ):
        if typ == TYPE_LOCAL:
            path = 'levels/{}'.format(filename)
            stream = open(path, 'r')
        else:
            stream = pkg_resources.open_text('levels', filename)
        data = yaml.load(stream, Loader=yaml.FullLoader)
        self.name = data.get('name')
        self.intro = data.get('intro')
        self.outro = data.get('outro')
        self.money = data.get('money')
        self.tutorial = data.get('tutorial')
        diner.init(data.get('diner'))
        goals.init(data.get('goals'))
        time.init(data.get('calendar'))
        skills.init(data.get('skills', []))
        ingredients.init(data.get('ingredients', []))
        storage.init(data.get('storage', []))
        kitchen.init(data.get('kitchen', []))
        shopping.init(data.get('shopping', []))
        food.init(data.get('food'))
        guests.init(data.get('guests', []))
        social.init(data.get('social', []))
        activities.init(data.get('activities', []))
        stream.close()


levels = None
level = None


def get():
    global levels
    return list(levels.keys())


def get_name():
    global level
    return level.name if level else None


def get_intro():
    global level
    return level.intro


def get_outro():
    global level
    return level.outro


def is_tutorial_enabled():
    global level
    return level.tutorial if level else False


def get_money():
    global level
    return level.money

def add_money(diff):
    global level
    level.money += diff
    return level.money


def init_level(name):
    global levels
    global level
    level = Level()
    file, typ = levels[name]
    level.init(file, typ)
    #time.register_callback(time.Calendar.TIME_MORNING, autosave_save)


def saved_games():
    files = [file for file in os.listdir('saves/') if 'yaml' in file]
    return {slot: level_file for slot, level_file in enumerate(files, 1)}


def save_game(slot):
    global level
    files = saved_games()
    file = files.get(slot)
    if file:
        os.remove('saves/{}'.format(file))
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    file_name = '{}_{}_{}'.format(slot, level.name, timestamp)
    with open('saves/{}'.format(file_name), 'wb') as f:
        save(f)


def load_game(slot):
    global level
    files = saved_games()
    file = files.get(slot)
    with open('saves/{}'.format(file), 'rb') as f:
        load(f)


def autosave_save():
    cli.print_message('Auto-saving...')
    with open('saves/auto.yaml', 'wb') as f:
        save(f)


def autosave_load():
    with open('saves/auto.yaml', 'rb') as f:
        load(f)


def init(dev=False):
    global levels
    levels = {}
    if dev:
        files = [level_file for level_file in os.listdir('levels/')]
        files = filter(lambda f: f.startswith('level'), files)
        files = sorted(files)
        typ = TYPE_LOCAL
    else:
        files = LEVELS
        typ = TYPE_PACKAGE
    for level_file in files:
        _, num, name = os.path.splitext(level_file)[0].split('_')
        levels[name] = (level_file, typ)


def save(file):
    pass


def load(file):
    pass
