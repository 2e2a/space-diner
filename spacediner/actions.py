from . import food
from . import guests
from . import levels
from . import storage


class Action:

    def perform(self, *args, **kwargs):
        raise NotImplemented


class Cook(Action):
    food = None

    def __init__(self, ingredients=None):
        self.food = food.Food(ingredients)

    def add_ingredients(self, ingredients):
        for ingredient, device in ingredients:
           if not storage.is_ingredient_available(ingredient):
                raise RuntimeError('Ingredient not available')
        self.food.prepare_ingredients(ingredients)

    def perform(self):
        self.food.plate()


class Serve(Action):
    food = None
    guest = None

    def __init__(self, food, guest):
        self.food = food
        self.guest = guest

    def perform(self):
        guests.serve(self.guest, self.food)


class BuyStorage(Action):
    storage = None

    def __init__(self, storage):
        self.storage = storage

    def perform(self):
        new_storage = storage.get(self.storage)
        if new_storage.cost > levels.level.money:
            raise RuntimeError('Not enough money')
        levels.level.money = levels.level.money - new_storage.cost
        storage.buy(self.storage)

