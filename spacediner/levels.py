import yaml

from . import food
from . import storage
from . import ingredients


class Level:
    name = None

    def load(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            ingredients.load(data.get('ingredients'))
            storage.load(data.get('storage'))
            food.load(data.get('recipes'))


level = None


def load():
    global level
    level = Level()
    level.load('levels/test.yaml')
