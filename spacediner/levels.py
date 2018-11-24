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

    def load(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            self.diner = data.get('diner')
            self.money = data.get('money')
            ingredients.load(data.get('ingredients'))
            storage.load(data.get('storage'))
            kitchen.load(data.get('kitchen'))
            merchants.load(data.get('merchants'))
            food.load(data.get('recipes'))
            guests.load(data.get('guests'))
            social.load(data.get('sozial'))


level = None


def load():
    global level
    level = Level()
    level.load('levels/test.yaml')


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
