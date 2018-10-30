from collections import OrderedDict

from . import generic


class Ingredient(generic.Thing):
    name = None
    storage = None
    properties = None

    def load(self, data):
        self.name = data.get('name')
        self.storage = data.get('storage')
        self.properties = data.get('properties')
        self.properties.append(self.name)


ingredients = None


def get(name):
    global ingredients
    return ingredients.get(name)


def load(data):
    global ingredients
    ingredients = OrderedDict()
    for ingredient_data in data:
        ingredient = Ingredient()
        ingredient.load(ingredient_data)
        ingredients.update({ingredient.name: ingredient})


def debug():
    global ingredients
    for ingredient in ingredients.values():
        ingredient.debug()
