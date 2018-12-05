from collections import OrderedDict

from . import generic
from . import ingredients


class Storage(generic.Thing):
    name = None
    available = False
    cost = 0
    ingredients = None

    def is_ingredient_available(self, name):
        if name in self.ingredients and self.ingredients.get(name) > 0:
            return True
        return False

    def take_ingredient(self, name):
        if name in self.ingredients:
            availability = self.ingredients.get(name)
            if availability > 0:
                self.ingredients.update({name: availability - 1})
                return ingredients.get(name)
        return None

    def store_ingredient(self, name, amount):
        availability = self.ingredients.get(name, 0)
        self.ingredients.update({name: availability + amount})

    def init(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.cost = data.get('cost', 0)
        self.ingredients = OrderedDict()
        for storage_ingredient in  data.get('ingredients'):
            ingredient =  storage_ingredient.get('name')
            availability = storage_ingredient.get('available')
            self.ingredients.update({ingredient: availability})

    def __str__(self):
        ingredients = ', '.join(['{}[{}]'.format(i, c) for (i, c) in self.ingredients.items()])
        return '{}: {}'.format(self.name, ingredients)



storages = None


def available_storages():
    global storages
    return [s.name for s in storages.values() if s.available]


def available_ingredients():
    global storages
    ingredients = {}
    for storage in storages.values():
        if storage.available:
            ingredients.update(storage.ingredients)
    return ingredients


def is_ingredient_available(name):
    global storages
    for storage in storages.values():
        if storage.available and storage.is_ingredient_available(name):
            return True
    return False


def take_ingredient(name):
    global storages
    for storage in storages.values():
        if storage.available:
            ingredient = storage.take_ingredient(name)
            if ingredient:
                return ingredient
    return None


def for_sale():
    global storages
    storages_for_sale = {}
    for storage in storages.values():
        if not storage.available:
            storages_for_sale.update({storage.name : storage})
    return storages_for_sale


def buy(name):
    global storages
    storage = storages.get(name)
    storage.available = True


def store_ingredient(name, amount):
    ingredient = ingredients.get(name)
    storage = storages.get(ingredient.storage)
    storage.store_ingredient(name, amount)


def get(name):
    global storages
    return storages.get(name)


def init(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.init(storage_data)
        storages.update({storage.name: storage})


def debug():
    global storages
    for storage in storages.values():
        storage.debug()
