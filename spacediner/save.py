import os

from datetime import datetime

from . import cli
from . import levels
from . import time


def saved_games():
    files = sorted(file for file in os.listdir('saves/') if 'Space-diner' in file)
    return {slot: level_file for slot, level_file in enumerate(files, 1)}


def save_game(slot):
    files = saved_games()
    file = files.get(slot)
    if file:
        os.remove('saves/{}'.format(file))
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    file_name = 'Space-diner_{}_{}_{}'.format(slot, levels.get_name(), timestamp)
    with open('saves/{}'.format(file_name), 'wb') as f:
        save(f)


def load_game(slot):
    files = saved_games()
    file = files.get(slot)
    with open('saves/{}'.format(file), 'rb') as f:
        load(f)


def autosave_save():
    cli.print_message('Auto-saving...')
    with open('saves/Space-diner_autosave', 'wb') as f:
        save(f)


def autosave_load():
    with open('saves/Space-diner_autosave', 'rb') as f:
        load(f)


def init():
    time.register_callback(time.Calendar.TIME_MORNING, autosave_save)


def save(file):
    from . import activities
    from . import diner
    from . import food
    from . import goals
    from . import guests
    from . import kitchen
    from . import levels
    from . import ingredients
    from . import reviews
    from . import shopping
    from . import social
    from . import skills
    from . import storage
    from . import time
    from . import tutorial
    activities.save(file)
    cli.save(file)
    diner.save(file)
    food.save(file)
    goals.save(file)
    guests.save(file)
    ingredients.save(file)
    kitchen.save(file)
    levels.save(file)
    reviews.save(file)
    shopping.save(file)
    skills.save(file)
    social.save(file)
    storage.save(file)
    time.save(file)
    tutorial.save(file)
    

def load(file):
    from . import activities
    from . import diner
    from . import food
    from . import goals
    from . import guests
    from . import kitchen
    from . import levels
    from . import ingredients
    from . import reviews
    from . import shopping
    from . import social
    from . import skills
    from . import storage
    from . import time
    from . import tutorial
    activities.load(file)
    cli.load(file)
    diner.load(file)
    food.load(file)
    goals.load(file)
    guests.load(file)
    ingredients.load(file)
    kitchen.load(file)
    levels.load(file)
    reviews.load(file)
    shopping.load(file)
    skills.load(file)
    social.load(file)
    storage.load(file)
    time.load(file)
    tutorial.load(file)
    time.register_callback(time.Calendar.TIME_MORNING, autosave_save)
