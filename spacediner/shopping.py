import pickle

from collections import OrderedDict

from . import ingredients
from . import social
from . import time


class Market:
    name = None
    description = None

    def init(self, data):
        self.name = data.get('name')
        self.description = data.get('description')


class Merchant:
    name = None
    description = None
    owner = None
    available = False
    ingredients = None

    def is_ingredient_available(self, name, amount):
        if name in self.ingredients and self.ingredients.get(name)[0] >= amount:
            return True
        return False

    def for_sale(self):
        for_sale = {}
        for ingredient_name, (availability, cost, _) in self.ingredients.items():
            ingredient = ingredients.get(ingredient_name)
            for_sale.update({ingredient_name: (availability, cost, ingredient.storage)})
        return for_sale

    def cost(self, name):
        return self.ingredients.get(name)[1]

    def buy(self, name, amount):
        if name in self.ingredients:
            availability, cost, in_stock = self.ingredients.get(name)
            if availability > 0:
                self.ingredients.update({name: (availability - amount, cost, in_stock)})
                return ingredients.get(name)
        return None

    def has_chat_available(self):
        return social.has_chats(self.owner, self.owner) and social.next_chat(self.owner)

    def chat(self):
        return social.greet_and_chat(self.owner, self.owner)

    def restock(self):
        for name, (availability, cost, in_stock) in self.ingredients.items():
            self.ingredients.update({name: (in_stock, cost, in_stock)})

    STOCK_AVAILABILITY_UNLIMITED = 99

    def init(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.owner = data.get('owner', self.name)
        self.available = data.get('available', True)
        self.ingredients = OrderedDict()
        for merchant_ingredient in data.get('ingredients'):
            ingredient = merchant_ingredient.get('name')
            availability = merchant_ingredient.get('available', self.STOCK_AVAILABILITY_UNLIMITED)
            cost = merchant_ingredient.get('cost', 0)
            self.ingredients.update({ingredient: (availability, cost, availability)}) # TODO: restock

    def __str__(self):
        ingredients = ', '.join(['{}[{} in stock] [{} $$$]'.format(i, a, c) for (i, (a, c, _)) in self.ingredients.items()])
        return '{}: {}'.format(self.name, ingredients)


market = None
merchants = None


def get(name):
    global merchants
    return merchants.get(name)


def owner(name):
    return get(name).owner


def get_available():
    global merchants
    return [merchant.name for merchant in merchants.values() if merchant.available]


def for_sale():
    global merchants
    ingredients_for_sale = {}
    for merchant in merchants.values():
        if merchant.available:
            ingredients_for_sale.update({
                merchant.name: merchant.for_sale().keys()
            })
    return ingredients_for_sale


def merchant_for_sale(name):
    merchant = get(name)
    return merchant.for_sale() if merchant.available else {}


def available_ingredients():
    global merchants
    available_ingredients = []
    for merchant in merchants.values():
        if merchant.available:
            available_ingredients.extend(merchant.ingredients.keys())
    return available_ingredients


def buy(name, ingregient, amount):
    merchant = get(name)
    merchant.buy(ingregient, amount)


def has_chat_available(name):
    merchant = get(name)
    return merchant.has_chat_available()


def chat(name):
    merchant = get(name)
    return merchant.chat()


def unlock(name):
    merchant = get(name)
    merchant.available = True


def morning():
    global merchants
    for merchant in merchants.values():
        merchant.restock()


def init(data):
    global market
    global merchants
    market = Market()
    market.init(data.get('market'))
    merchants = OrderedDict()
    for merchant_data in data.get('merchants'):
        merchant = Merchant()
        merchant.init(merchant_data)
        merchants.update({merchant.name: merchant})
    time.register_callback(time.Calendar.TIME_MORNING, morning)


def save(file):
    global merchants
    global market
    pickle.dump(merchants, file)
    pickle.dump(market, file)


def load(file):
    global merchants
    global market
    merchants = pickle.load(file)
    market = pickle.load(file)
    time.register_callback(time.Calendar.TIME_MORNING, morning)
