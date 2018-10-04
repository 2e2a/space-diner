import os
import yaml

from . import storage


class Level:
    name = None
    storages = {}

    def load(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream)
            self.name = data.get('name')
            self.storages = storage.load(data.get('storage'))
            print(self.name)


def load():
    for level_file_name in os.listdir('levels/'):
        level_file_relative = 'levels/' + level_file_name
        level = Level()
        level.load(level_file_relative)
