import pickle

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
        for preparation_participle, ingredient_name in ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            ingredient.properties.add(preparation_participle)
            self.ingredients.append((preparation_participle, ingredient))

    def plate(self):
        global cooked
        self.properties = set()
        names = []
        for preparation_participle, ingredient in self.ingredients:
            name = '{} {}'.format(preparation_participle, ingredient.name)
            names.append(name)
            self.properties.update(ingredient.properties)
        recipe = match_recipe([ingredient for _, ingredient in self.ingredients])
        if recipe:
            self.properties.update(recipe.properties)
            self.name = '{} ({})'.format(recipe.name, ' with '.join(names))
        else:
            self.name = ' with '.join(names)
        cooked.append(self)


class Recipe(generic.Thing):
    available = False
    ingredient_properties = None
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


def get_recipes():
    global recipes
    return [recipe.name for recipe in recipes.values() if recipe.available]


def get_recipe(name):
    global recipes
    return recipes.get(name)


def match_recipe(ingredients):
    global recipes
    for recipe in recipes.values():
        if recipe.consists_of(ingredients):
            return recipe
    return None


def create_recipe(name, prepared_ingredients):
    global recipes
    recipe = Recipe()
    recipe.name = name
    recipe.available = True
    recipe.ingredient_properties = []
    recipe.properties = set()
    for preparation, ingredient in prepared_ingredients:
        recipe.ingredient_properties.append(set([preparation, ingredient.name]))
        recipe.properties.update(ingredient.properties)
    recipes.update({name: recipe})


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
