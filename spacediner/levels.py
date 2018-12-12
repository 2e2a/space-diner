import os
import pickle
import yaml

from datetime import datetime

from . import food
from . import generic
from . import guests
from . import kitchen
from . import ingredients
from . import merchants
from . import social
from . import storage
from . import time


class Level(generic.Thing):
    name = None
    diner = None
    money = 0

    def init(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            self.diner = data.get('diner')
            self.money = data.get('money')
            ingredients.init(data.get('ingredients'))
            storage.init(data.get('storage'))
            kitchen.init(data.get('kitchen'))
            merchants.init(data.get('merchants'))
            food.init(data.get('recipes'))
            guests.init(data.get('guests'))
            social.init(data.get('sozial'))


level = None


def list():
    return [level_file for level_file in os.listdir('levels/')]


def saved_games():
    return {slot: level_file for slot, level_file in enumerate(os.listdir('saves/'), 1)}


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


def init(name):
    global level
    level = Level()
    file_name = 'levels/{}'.format(name)
    level.init(file_name)


def save(file):
    global level
    pickle.dump(level, file)
    ingredients.save(file)
    storage.save(file)
    kitchen.save(file)
    merchants.save(file)
    food.save(file)
    guests.save(file)
    social.save(file)
    time.save(file)


def load(file):
    global level
    level = pickle.load(file)
    ingredients.load(file)
    storage.load(file)
    kitchen.load(file)
    merchants.load(file)
    food.load(file)
    guests.load(file)
    social.load(file)
    time.load(file)


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
