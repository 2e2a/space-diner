from collections import OrderedDict


class Ingredient:
    name = None
    taste = None

    def load(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')


ingredients = None


def load(data):
    global ingredients
    ingredients = OrderedDict()
    for ingredient_data in data:
        ingredient = Ingredient()
        ingredient.load(ingredient_data)
        ingredients.update({ingredient.name: ingredient})
