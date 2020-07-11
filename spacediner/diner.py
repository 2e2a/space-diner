import pickle

from . import cli
from . import time


class Diner:
    name = None
    chef = 'Chef'
    seats = 0
    decoration = None
    available_decoration = None

    sanitation = 5

    def init(self, data):
        self.name = data.get('name')
        self.seats = data.get('seats')
        self.decoration = data.get('decoration', [])
        self.available_decoration = []

    @property
    def is_dirty(self):
        return self.sanitation < 5

    @property
    def is_very_dirty(self):
        return self.sanitation < 3

    def clean(self):
        self.sanitation = 5


diner = None


def add_decoration(name):
    global diner
    diner.available_decoration.append(name)


def new_evening():
    global diner
    if diner.sanitation > 0:
        diner.sanitation -= 1
    cli.print_message('Sanitation status of your diner: {}/5'.format(diner.sanitation))


def init(data):
    global diner
    diner = Diner()
    diner.init(data)
    time.register_callback(time.Calendar.TIME_EVENING, new_evening)


def save(file):
    global diner
    pickle.dump(diner, file)


def load(file):
    global diner
    diner = pickle.load(file)
