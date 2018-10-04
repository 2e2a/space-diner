import yaml

from . import storage
from . import ingredients


class Level:
    name = None

    def load(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            storage.load(data.get('storage'))
            ingredients.load(data.get('ingredients'))


level = None


def load():
    global level
    level = Level()
    level.load('levels/test.yaml')
