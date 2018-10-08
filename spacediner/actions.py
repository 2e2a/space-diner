from . import food
from . import storage


class Action:

    def perform(self, *args, **kwargs):
        raise NotImplemented


class Cook(Action):
    ingredients = None

    def __init__(self, ingredients=None):
        self.ingredients = ingredients if ingredients else []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def perform(self):
        ingredients = []
        for ingredient_name in self.ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            ingredients.append(ingredient)
        food.cook(ingredients)
