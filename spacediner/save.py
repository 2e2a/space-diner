import os

from datetime import datetime

from . import cli
from . import diner
from . import levels
from . import time

path = None


def has_save_path():
    global path
    return path is not None


def set_save_path():
    global path
    while True:
        cli.print_text('Select folder for saving/loading of Space Diner savegames:')
        default = os.path.join(os.getcwd(), 'SpaceDinerSaves')
        path = cli.input_with_default(default)
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                break
            except FileNotFoundError:
                cli.print_message('Selected path not found.')
        elif not os.path.isdir(path):
            cli.print_message('Selected path is not a directory.')
        else:
            break
    return path


def saved_games():
    global path
    files = sorted(file for file in os.listdir(path) if 'Space-Diner' in file)
    return {slot: level_file for slot, level_file in enumerate(files, 1)}


def save_game(slot):
    global path
    files = saved_games()
    file = files.get(slot)
    if file:
        os.remove(os.path.join(path, file))
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    file_name = 'Space-diner_{}_{}_{}'.format(slot, levels.get_name(), timestamp)
    with open(os.path.join(path, file_name), 'wb') as f:
        save(f)


def load_game(slot):
    global path
    files = saved_games()
    file = files.get(slot)
    with open(os.path.join(path, file), 'rb') as f:
        load(f)


def autosave_save():
    global path
    if not diner.diner:
        return
    level = 'Space-Diner_{}_{}_{}'.format(levels.get_number(), levels.get_name(), diner.diner.name.replace(' ', '-'))
    cli.print_message('Auto-saving to {}...'.format(level))
    cli.wait_for_input()
    file = os.path.join(path, level)
    with open(file, 'wb') as f:
        save(f)


def init():
    time.register_callback(time.Calendar.TIME_DAYTIME, autosave_save)


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
    time.register_callback(time.Calendar.TIME_DAYTIME, autosave_save)
