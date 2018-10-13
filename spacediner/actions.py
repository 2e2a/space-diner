from . import food
from . import guests
from . import storage


class Action:

    def perform(self, *args, **kwargs):
        raise NotImplemented


class Cook(Action):
    ingredients = None

    def __init__(self, ingredients=None):
        self.ingredients = ingredients if ingredients else []

    def add_ingredient(self, ingredient):
        if not storage.is_ingredient_available(ingredient):
            raise RuntimeError('Ingredient not available')
        self.ingredients.append(ingredient)

    def perform(self):
        food.cook(self.ingredients)


class Serve(Action):
    food = None
    guest = None

    def __init__(self, food, guest):
        self.food = food
        self.guest = guest

    def perform(self):
        guests.serve(self.guest, self.food)
