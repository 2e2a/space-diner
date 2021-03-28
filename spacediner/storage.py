import copy
import pickle

from collections import OrderedDict

from . import cli
from . import ingredients
from . import time


class Storage:
    name = None
    available = False
    cost = 0
    ingredients = None

    def is_ingredient_available(self, name):
        if name in self.ingredients and self.ingredients.get(name) > 0:
            return True
        return False

    def available_ingredients(self):
        return {
            ingredient: amount
            for ingredient, amount in self.ingredients.items() if self.ingredients.get(ingredient) > 0
        }

    def ingredient_amount_available(self, name):
        return self.ingredients.get(name) if name in self.ingredients else 0

    def take_ingredient(self, name, amount=1):
        if name in self.ingredients:
            availability = max(0, self.ingredients.get(name) - amount)
            self.ingredients.update({name: availability})
            ingredient = ingredients.get(name)
            return copy.deepcopy(ingredient)
        return None

    def store_ingredient(self, name, amount):
        availability = self.ingredients.get(name, 0)
        availability += amount
        availability = min(availability, 100)
        self.ingredients.update({name: availability})

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
            ingredients.update(storage.available_ingredients())
    return ingredients


def is_ingredient_available(name):
    global storages
    for storage in storages.values():
        if storage.available and storage.is_ingredient_available(name):
            return True
    return False


def take_ingredient(name, amount=1):
    global storages
    for storage in storages.values():
        if storage.available:
            ingredient = storage.take_ingredient(name, amount)
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
    storage = storages.get(ingredient.storage, None)
    if storage and storage.available:
        storage.store_ingredient(name, amount)
        return True
    return False


def get(name):
    global storages
    return storages.get(name)


def daytime():
    global storages
    ingredients_lost = {}
    for ingredient, amount in time.get_ingredients_lost().items():
        for storage in storages.values():
            if storage.is_ingredient_available(ingredient):
                lost_amount = min(storage.ingredient_amount_available(ingredient), amount)
                ingredients_lost.update({ingredient: lost_amount})
                storage.take_ingredient(ingredient, amount)
    if ingredients_lost:
        ingredient_list = ['{} x {}'.format(amount, ingredient) for ingredient, amount in ingredients_lost.items()]
        cli.print_message('Ingredients lost: {}'.format(', '.join(ingredient_list)))
        cli.print_newline()

    ingredients_won = time.get_ingredients_won()
    if ingredients_won:
        # TODO: Check if storage available
        ingredient_list = ['{} x {}'.format(amount, ingredient) for ingredient, amount in ingredients_won.items()]
        cli.print_message('Ingredients won: {}'.format(', '.join(ingredient_list)))
        cli.print_newline()
    for ingredient, amount in ingredients_won.items():
        store_ingredient(ingredient, amount)


def init(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.init(storage_data)
        storages.update({storage.name: storage})
    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)


def save(file):
    global storages
    pickle.dump(storages, file)


def load(file):
    global storages
    storages = pickle.load(file)
    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)
