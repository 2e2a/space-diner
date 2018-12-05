import os
import yaml

from . import food
from . import generic
from . import guests
from . import kitchen
from . import ingredients
from . import merchants
from . import social
from . import storage


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


def init(name):
    global level
    level = Level()
    file_name = 'levels/{}'.format(name)
    level.init(file_name)


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
