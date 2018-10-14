from collections import OrderedDict

from . import kitchen
from . import storage


class Food:
    name = None
    taste = None
    ingredients = []

    def __init__(self, ingredients=None):
        if ingredients:
            self.plate(ingredients)

    def prepare_ingredients(self, ingredients):
        for ingredient_name, device_name in ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            device = kitchen.get_device(device_name)
            preparation_participle = device.preparation_participle
            self.ingredients.append((ingredient, preparation_participle))

    def plate(self):
        global cooked
        names = []
        taste = []
        for ingredient, preparation_participle in self.ingredients:
            name = '{} {}'.format(preparation_participle, ingredient.name)
            names.append(name)
            taste.append(ingredient.taste)
        recipe = get_recipe(names)
        if recipe:
            self.name = recipe.name
            self.taste = recipe.taste
        else:
            self.name = '_'.join(names)
            self.taste = '-'.join(taste)
        cooked.update({self.name: self})

    def __str__(self):
        return '{} ({})'.format(self.name, self.taste)


class Recipe(Food):
    available = False
    ingredients = []

    def consists_of(self, ingredients):
        return ingredients == self.ingredients

    def load(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')
        self.available = data.get('available')
        self.ingredients = data.get('ingredients')


recipes = None
cooked = OrderedDict()


def take(name):
    global cooked
    return cooked.pop(name)


def get_recipe(ingredients):
    global recipes
    for recipe in recipes.values():
        if recipe.consists_of(ingredients):
            return recipe
    return None


def load(data):
    global recipes
    recipes = OrderedDict()
    for recipe_data in data:
        recipe = Recipe()
        recipe.load(recipe_data)
        recipes.update({recipe.name: recipe})

