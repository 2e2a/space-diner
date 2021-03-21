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
    cleaned = False

    def init(self, data):
        self.name = data.get('name')
        self.seats = data.get('seats')
        self.decoration = data.get('decoration', [])
        self.available_decoration = data.get('available decoration', [])

    @property
    def is_dirty(self):
        return self.sanitation < 5

    @property
    def is_very_dirty(self):
        return self.sanitation < 3

    def clean(self):
        self.sanitation = 5
        self.cleaned = True


diner = None


def add_decoration(name):
    global diner
    diner.available_decoration.append(name)


def new_morning():
    global diner
    if not diner.cleaned and diner.sanitation > 0:
        diner.sanitation -= 1
    diner.cleaned = False


def init(data):
    global diner
    diner = Diner()
    diner.init(data)
    time.register_callback(time.Calendar.TIME_MORNING, new_morning)


def save(file):
    global diner
    pickle.dump(diner, file)


def load(file):
    global diner
    diner = pickle.load(file)
    time.register_callback(time.Calendar.TIME_MORNING, new_morning)
