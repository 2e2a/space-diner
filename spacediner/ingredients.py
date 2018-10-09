from collections import OrderedDict


class Ingredient:
    name = None
    taste = None

    def load(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')

    def __str__(self):
        return '{} ({})'.format(self.name, self.taste)


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
