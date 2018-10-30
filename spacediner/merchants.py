from collections import OrderedDict

from . import generic
from . import ingredients
from . import storage


class Merchant(generic.Thing):
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

    def load(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.ingredients = OrderedDict()
        for merchant_ingredient in  data.get('ingredients'):
            ingredient =  merchant_ingredient.get('name')
            availability = merchant_ingredient.get('available')
            cost = merchant_ingredient.get('cost', 0)
            self.ingredients.update({ingredient: (availability, cost, )})

    def __str__(self):
        ingredients = ', '.join(['{}[{} in stock] [{} $$$]'.format(i, a, c) for (i, a, c) in self.ingredients.items()])
        return '{}: {}'.format(self.name, ingredients)


merchants = None


def get(name):
    global merchants
    return merchants.get(name)


def ingredients_for_sale():
    global merchants
    return OrderedDict({merchant.name: merchant.for_sale() for merchant in merchants.values()})


def load(data):
    global merchants
    merchants = OrderedDict()
    for merchant_data in data:
        merchant = Merchant()
        merchant.load(merchant_data)
        merchants.update({merchant.name: merchant})


def debug():
    global merchants
    for merchant in merchants.values():
        merchant.debug()
