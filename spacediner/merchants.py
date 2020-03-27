import pickle

from collections import OrderedDict

from . import ingredients


class Merchant:
    name = None
    available = False
    ingredients = None

    def is_ingredient_available(self, name, amount):
        if name in self.ingredients and self.ingredients.get(name)[0] >= amount:
            return True
        return False

    def for_sale(self):
        for_sale = {}
        for ingredient_name, (availability, cost) in self.ingredients.items():
            ingredient = ingredients.get(ingredient_name)
            for_sale.update({ingredient_name: (availability, cost, ingredient.storage)})
        return for_sale

    def cost(self, name):
        return self.ingredients.get(name)[1]

    def buy(self, name, amount):
        if name in self.ingredients:
            availability, cost = self.ingredients.get(name)
            if availability > 0:
                self.ingredients.update({name: (availability - amount, cost)})
                return ingredients.get(name)
        return None

    STOCK_AVAILABILITY_UNLIMITED = 99

    def init(self, data):
        self.name = data.get('name')
        self.available = data.get('available', True)
        self.ingredients = OrderedDict()
        for merchant_ingredient in  data.get('ingredients'):
            ingredient =  merchant_ingredient.get('name')
            availability = merchant_ingredient.get('available', self.STOCK_AVAILABILITY_UNLIMITED)
            cost = merchant_ingredient.get('cost', 0)
            self.ingredients.update({ingredient: (availability, cost, )})

    def __str__(self):
        ingredients = ', '.join(['{}[{} in stock] [{} $$$]'.format(i, a, c) for (i, (a, c)) in self.ingredients.items()])
        return '{}: {}'.format(self.name, ingredients)


merchants = None


def get(name):
    global merchants
    return merchants.get(name)


def ingredients_for_sale():
    global merchants
    return OrderedDict({merchant.name: merchant.for_sale() for merchant in merchants.values() if merchant.available})


def available_ingredients():
    global merchants
    available_ingredients = []
    for merchant in merchants.values():
        if merchant.available:
            available_ingredients.extend(merchant.ingredients.keys())
    return available_ingredients


def unlock(name):
    global merchants
    merchant = merchants.get(name)
    merchant.available = True


def init(data):
    global merchants
    merchants = OrderedDict()
    for merchant_data in data:
        merchant = Merchant()
        merchant.init(merchant_data)
        merchants.update({merchant.name: merchant})


def save(file):
    global merchants
    pickle.dump(merchants, file)


def load(file):
    global merchants
    merchants = pickle.load(file)
