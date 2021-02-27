from . import ingredients
from . import storage


def plenty():
    for ingredient in ingredients.ingredients:
        storage.store_ingredient(ingredient, 100)


def cheat(cmd):
    if cmd == '!plenty':
        plenty()

