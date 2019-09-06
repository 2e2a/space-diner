from . import cli  # TODO: inject
from . import food
from . import guests
from . import ingredients
from . import levels
from . import merchants
from . import social
from . import storage


class Action:

    def perform(self, *args, **kwargs):
        raise NotImplemented

    def abort(self, *args, **kwargs):
        raise NotImplemented


class Cook(Action):
    food = None

    def __init__(self, ingredients=None):
        self.food = food.Food(ingredients)

    def add_ingredients(self, ingredients):
        for _, ingredient in ingredients:
           if not storage.is_ingredient_available(ingredient):
                raise RuntimeError('Ingredient not available')
        self.food.prepare_ingredients(ingredients)

    def perform(self):
        self.food.plate()

    def abort(self):
        cli.print_message('throw away {}'.format(', '.join(self.food.get_prepared_ingredients())))
        self.food = None


class Serve(Action):
    food = None
    guest = None

    def __init__(self, food, guest):
        self.food = food
        self.guest = guest

    def perform(self):
        guests.serve(self.guest, self.food)
        guests.leave(self.guest)
        cli.print_text('{} left.'.format(self.guest))


class SendHome(Action):
    guest = None

    def __init__(self, guest):
        self.guest = guest

    def perform(self):
        cli.print_text('{} left.'.format(self.guest))
        cli.print_message('{} bonding level is {}'.format(self.guest, social.level(self.guest)))
        guests.send_home(self.guest)


class CloseUp(Action):

    def perform(self):
        for guest in guests.available_guests():
            send_home = SendHome(guest)
            send_home.perform()


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


class Chat(Action):
    guest = None

    def __init__(self, guest, reply):
        self.guest = guest
        self.reply = reply

    def perform(self):
        effect, reaction = social.chat(self.guest, self.reply)
        if reaction:
            cli.print_dialog(self.guest, reaction)
        if effect > 0:
            cli.print_text('{} liked your reply.'.format(self.guest))
        elif effect < 0:
            cli.print_text('{} did not like your reply.'.format(self.guest))
        else:
            cli.print_text('{} does not care.'.format(self.guest))
        cli.print_message('{} bonding level is {}'.format(self.guest, social.level(self.guest)))


class SaveDish(Action):
    dish = None
    name = None

    def __init__(self, dish, new_name=None):
        self.dish = dish
        self.name = new_name if new_name else dish

    def perform(self):
        food.save_dish(self.dish, self.name)
