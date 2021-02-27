from . import storage


def plenty():
    ingredients = storage.available_ingredients()
    for ingredient in ingredients:
        storage.store_ingredient(ingredient, 100)


def cheat(cmd):
    if cmd == '!plenty':
        plenty()

