import os
import yaml

from datetime import datetime


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


class Level:
    name = None
    intro = None
    money = 0

    def init(self, filename):
        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)
            self.name = data.get('name')
            self.intro = data.get('intro')
            self.money = data.get('money')
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
    #time.register_callback(time.Calendar.TIME_MORNING, autosave_save)


def save(file):
    pass


def load(file):
    pass
