from collections import OrderedDict

from . import generic
from . import kitchen
from . import storage


class Food(generic.Thing):
    name = None
    ingredients = None
    properties = None

    def __init__(self, ingredients=None):
        self.ingredients = ingredients if ingredients else []
        if self.ingredients:
            self.plate()

    def prepare_ingredients(self, ingredients):
        for ingredient_name, device_name in ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            device = kitchen.get_device(device_name)
            preparation_participle = device.preparation_participle
            self.ingredients.append((ingredient, preparation_participle))

    def plate(self):
        global cooked
        names = []
        self.properties = set()
        for ingredient, preparation_participle in self.ingredients:
            name = '{} {}'.format(preparation_participle, ingredient.name)
            names.append(name)
            self.properties.update(ingredient.properties)
        recipe = get_recipe(names)
        if recipe:
            self.properties.update(recipe.properties)
            self.name = recipe.name
        else:
            self.name = ' with '.join(names)
        cooked.append(self)


class Recipe(generic.Thing):
    available = False
    properties = None

    def consists_of(self, ingredients):
        return set(ingredients) == set(self.ingredients)

    def init(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')
        self.available = data.get('available')
        self.ingredients = data.get('ingredients')
        self.properties = data.get('properties')
        self.properties.append(self.name)


recipes = None
cooked = []


def take(name):
    global cooked
    for dish in cooked:
        if dish.name == name:
            cooked.remove(dish)
            return dish
    return None

def plated():
    global cooked
    return [dish.name for dish in cooked]


def get_recipe(ingredients):
    global recipes
    for recipe in recipes.values():
        if recipe.consists_of(ingredients):
            return recipe
    return None


def init(data):
    global recipes
    recipes = OrderedDict()
    for recipe_data in data:
        recipe = Recipe()
        recipe.init(recipe_data)
        recipes.update({recipe.name: recipe})


def debug():
    global recipes
    global cooked
    for recipe in recipes.values():
        recipe.debug()
    for food in cooked:
        food.debug()
