import pickle

from collections import OrderedDict

from . import generic
from . import ingredients
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
            ingredient.properties.add(preparation_participle)
            self.ingredients.append((ingredient, preparation_participle))

    def plate(self):
        global cooked
        self.properties = set()
        names = []
        for ingredient, preparation_participle in self.ingredients:
            name = '{} {}'.format(preparation_participle, ingredient.name)
            names.append(name)
            self.properties.update(ingredient.properties)
            self.properties.update(preparation_participle)
        recipe = get_recipe([ingredient for ingredient, _ in self.ingredients])
        if recipe:
            self.properties.update(recipe.properties)
            self.name = '{} ({})'.format(recipe.name, ' with '.join(names))
        else:
            self.name = ' with '.join(names)
        cooked.append(self)


class Recipe(generic.Thing):
    available = False
    properties = None

    def  _properties_match(self, recipe_ingredient_property_list, ingredient_list):
        if not recipe_ingredient_property_list:
            return True
        for recipe_ingredient_properties in recipe_ingredient_property_list:
            for ingredient in ingredient_list:
                if recipe_ingredient_properties.issubset(ingredient.properties):
                    remaining_recipe_ingredient_property_list = recipe_ingredient_property_list.copy()
                    remaining_recipe_ingredient_property_list.remove(recipe_ingredient_properties)
                    remaining_ingredient_list = ingredient_list.copy()
                    remaining_ingredient_list.remove(ingredient)
                    if self._properties_match(remaining_recipe_ingredient_property_list, remaining_ingredient_list):
                        return True
        return False

    def consists_of(self, ingredient_list):
        return self._properties_match(self.ingredient_properties, ingredient_list)

    def init(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')
        self.available = data.get('available')
        self.ingredient_properties = []
        for ingredient_property_data in data.get('ingredients'):
            self.ingredient_properties.append(set(ingredient_property_data))
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


def save(file):
    global recipes
    global cooked
    pickle.dump(recipes, file)
    pickle.dump(cooked, file)


def load(file):
    global recipes
    global cooked
    recipes = pickle.load(file)
    cooked = pickle.load(file)


def debug():
    global recipes
    global cooked
    for recipe in recipes.values():
        recipe.debug()
    for food in cooked:
        food.debug()
