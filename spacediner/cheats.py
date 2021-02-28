from . import ingredients
from . import levels
from . import storage


def plenty():
    for ingredient in ingredients.ingredients:
        storage.store_ingredient(ingredient, 100)


def rich():
    levels.level.money = 1000000


def cheat(cmd):
    if cmd == '!plenty':
        plenty()
    elif cmd == '!rich':
        rich()

