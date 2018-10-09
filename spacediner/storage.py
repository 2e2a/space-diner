from collections import OrderedDict

from . import ingredients


class Storage:
    name = None
    available = False
    available_ingredients = None

    def get_ingredient(self, name):
        if name in self.available_ingredients:
            availability = self.available_ingredients.get(name)
            if availability > 0:
                self.available_ingredients.update({name: availability - 1})
                return ingredients.get(name)
        return None

    def take_ingredient(self, name):
        if name in self.available_ingredients:
            availability = self.available_ingredients.get(name)
            if availability > 0:
                self.available_ingredients.update({name: availability - 1})
                return ingredients.get(name)
        return None

    def load(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.available_ingredients = OrderedDict()
        for storage_ingredient in  data.get('ingredients'):
            ingredient =  storage_ingredient.get('name')
            availability = storage_ingredient.get('available')
            self.available_ingredients.update({ingredient: availability})

    def __str__(self):
        ingredients = ', '.join(['{}[{}]'.format(i, c) for (i, c) in self.available_ingredients.items()])
        return '{}: {}'.format(self.name, ingredients)



storages = None


def available_ingredients():
    global storages
    available_ingredients = {}
    for storage in storages.values():
        if storage.available:
            available_ingredients.update(storage.available_ingredients)
    return available_ingredients


def take_ingredient(name):
    global storages
    for storage in storages.values():
        if storage.available:
            ingredient = storage.take_ingredient(name)
            if ingredient:
                return ingredient
    return None


def load(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.load(storage_data)
        storages.update({storage.name: storage})
