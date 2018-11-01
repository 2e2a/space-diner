from . import food
from . import guests
from . import ingredients
from . import levels
from . import merchants
from . import storage


class Action:

    def perform(self, *args, **kwargs):
        raise NotImplemented

    def abort(self, *args, **kwargs):
        pass


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


class BuyIngredients(Action):
    merchant = None
    ingredient = None
    amount = 0

    def __init__(self, merchant, ingredient, amount):
        self.merchant = merchant
        self.ingredient = ingredient
        self.amount = amount

    def perform(self):
        if not storage.get(ingredients.get(self.ingredient).storage).available:
            raise RuntimeError('Required storage not available')
        merchant = merchants.get(self.merchant)
        if not merchant.is_ingredient_available(self.ingredient, 1):
            raise RuntimeError('Not in stock')
        if not merchant.is_ingredient_available(self.ingredient, self.amount):
            raise RuntimeError('Not enough ingredients')
        cost = merchant.cost(self.ingredient) * self.amount
        if cost > levels.level.money:
            raise RuntimeError('Not enough money')
        levels.level.money = levels.level.money - cost
        merchant.buy(self.ingredient, self.amount)
        storage.store_ingredient(self.ingredient, self.amount)

