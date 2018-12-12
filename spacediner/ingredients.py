import pickle

from collections import OrderedDict

from . import generic


class Ingredient(generic.Thing):
    name = None
    storage = None
    properties = None

    def init(self, data):
        self.name = data.get('name')
        self.storage = data.get('storage')
        self.properties = set(data.get('properties'))
        self.properties.add(self.name)

    def __str__(self):
        return self.name


ingredients = None


def get(name):
    global ingredients
    return ingredients.get(name)


def init(data):
    global ingredients
    ingredients = OrderedDict()
    for ingredient_data in data:
        ingredient = Ingredient()
        ingredient.init(ingredient_data)
        ingredients.update({ingredient.name: ingredient})


def save(file):
    global ingredients
    pickle.dump(ingredients, file)


def load(file):
    global ingredients
    ingredients = pickle.load(file)


def debug():
    global ingredients
    for ingredient in ingredients.values():
        ingredient.debug()
