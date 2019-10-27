import os
import pickle
import yaml

from datetime import datetime


from . import activities
from . import cli
from . import food
from . import generic
from . import goals
from . import guests
from . import kitchen
from . import ingredients
from . import merchants
from . import social
from . import skills
from . import storage
from . import time


class Level(generic.Thing):
    name = None
    diner = None
    money = 0
    intro = None

    def init(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            self.diner = data.get('diner')
            self.money = data.get('money')
            self.intro = data.get('intro')
            goals.init(data.get('goals'))
            time.init(data.get('time'))
            skills.init(data.get('skills', []))
            ingredients.init(data.get('ingredients', []))
            storage.init(data.get('storage', []))
            kitchen.init(data.get('kitchen', []))
            merchants.init(data.get('merchants', []))
            food.init(data.get('recipes', []))
            guests.init(data.get('guests', []))
            social.init(data.get('social', []))
            activities.init(data.get('activities', []))


level = None


def list():
    return sorted([level_file for level_file in os.listdir('levels/')])


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


def init(name):
    global level
    level = Level()
    file_name = 'levels/{}'.format(name)
    level.init(file_name)
    cli.print_title(level.name)
    cli.print_text(level.intro)
    time.register_callback(time.Clock.TIME_WORK, autosave_save)


def save(file):
    # TODO: missing rewards? goals?
    global level
    pickle.dump(level, file)
    time.save(file)
    skills.save(file)
    ingredients.save(file)
    storage.save(file)
    kitchen.save(file)
    merchants.save(file)
    food.save(file)
    guests.save(file)
    social.save(file)
    activities.save(file)


def load(file):
    global level
    level = pickle.load(file)
    time.load(file)
    skills.load(file)
    ingredients.load(file)
    storage.load(file)
    kitchen.load(file)
    merchants.load(file)
    food.load(file)
    guests.load(file)
    social.load(file)
    activities.load(file)


def debug():
    global level
    level.debug()
    ingredients.debug()
    storage.debug()
    kitchen.debug()
    merchants.debug()
    food.debug()
    guests.debug()
    social.debug()
