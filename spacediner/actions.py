from . import activities
from . import cli  # TODO: inject
from . import diner
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
        prepared_ingredients = self.food.get_prepared_ingredients()
        if prepared_ingredients:
            cli.print_message('throw away {}'.format(', '.join(prepared_ingredients)))
        self.food = food.Food()


class TakeOrder(Action):

    def __init__(self, guest):
        self.guest = guest

    def perform(self):
        order = guests.take_order(self.guest)
        cli.print_dialog(self.guest, order)


class Serve(Action):

    def __init__(self, food, guest):
        self.food = food
        self.guest = guest

    def perform(self):
        guests.serve(self.guest, self.food)
        guests.leave(self.guest)
        cli.print_text('{} left.'.format(self.guest))


class SendHome(Action):

    def __init__(self, guest):
        self.guest = guest

    def perform(self):
        cli.print_text('{} left.'.format(self.guest))
        guests.send_home(self.guest)


class CloseUp(Action):

    def perform(self):
        for plated_food in food.plated():
            cli.print_message('throw away {}'.format(plated_food))
        cli.print_newline()
        for guest in guests.available_guests():
            send_home = SendHome(guest)
            send_home.perform()
        cli.print_newline()


class BuyStorage(Action):

    def __init__(self, storage):
        self.storage = storage

    def perform(self):
        new_storage = storage.get(self.storage)
        if new_storage.cost > levels.level.money:
            raise RuntimeError('Not enough money')
        levels.level.money = levels.level.money - new_storage.cost
        storage.buy(self.storage)


class BuyIngredients(Action):

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

    def __init__(self, guest):
        self.guest = guest

    def perform(self):
        chat = guests.chat(self.guest)
        cli.print_dialog(self.guest, chat)


class Meet(Action):

    def __init__(self, guest, reply):
        self.guest = guest
        self.reply = reply

    def perform(self):
        reply, liked = social.meet(self.guest, self.reply)
        cli.print_dialog(self.guest, reply)
        if liked:
            social.level_up(self.guest)
        if social.was_last_meeting(self.guest):
            social.unlock_all_rewards(self.guest)
        social.lock_friendship(self.guest)


class DoActivity(Action):

    def __init__(self, activity):
        self.activity = activity

    def perform(self):
        activities.do(self.activity)


class CleanDiner(Action):

    def perform(self):
        diner.diner.clean()
        cli.print_message('Diner cleaned.')


class SaveDish(Action):

    def __init__(self, dish, new_name=None):
        self.dish = dish
        self.name = new_name if new_name else dish

    def perform(self):
        food.save_dish(self.dish, self.name)


class SaveRecipe(Action):

    def __init__(self, name, ingredient_properties):
        self.name = name
        self.ingredient_properties = ingredient_properties

    def perform(self):
        food.save_as_recipe(self.name, self.ingredient_properties)
