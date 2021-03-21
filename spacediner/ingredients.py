import pickle

from collections import OrderedDict


class Ingredient:
    name = None
    description = None
    storage = None
    properties = None
    extra_properties = None

    def init(self, data):
        self.name = data.get('name')
        self.description = data.get('description', None)
        self.storage = data.get('storage')
        self.extra_properties = set(data.get('properties'))
        self.properties = self.extra_properties.copy()
        self.properties.add(self.name)

    def __str__(self):
        return self.name


ingredients = None


def get(name):
    global ingredients
    return ingredients.get(name)


def get_properties(name):
    return list(get(name).properties)


def get_extra_properties(name):
    return list(get(name).extra_properties)


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
