import os
import pickle
import yaml
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from levels import LEVELS
from . import activities
from . import diner
from . import food
from . import goals
from . import guests
from . import kitchen
from . import ingredients
from . import save as save_module
from . import shopping
from . import social
from . import skills
from . import storage
from . import time


TYPE_LOCAL = 'local'
TYPE_PACKAGE = 'pkg'


class Level:
    name = None
    number = 0
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
        self.number = data.get('level')
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


def get_number():
    global level
    return level.number if level else None


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
    save_module.init()


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
    global level
    pickle.dump(level, file)


def load(file):
    global level
    level = pickle.load(file)
