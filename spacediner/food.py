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
        self.ingredients = []
        if ingredients:
            self.prepare_ingredients(ingredients)

    def prepare_ingredients(self, ingredients):
        for preparation, ingredient_name in ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            device = kitchen.preparation_device(preparation)
            ingredient.properties.add(device.result)
            ingredient.properties.update(device.properties)
            self.ingredients.append((preparation, ingredient))

    def plate(self):
        global cooked
        self.properties = set()
        names = set()
        recipe_ingredients = []
        for preparation, ingredient in self.ingredients:
            name = '{} {}'.format(preparation, ingredient.name)
            names.add(name)
            self.properties.update(ingredient.properties)
            recipe_ingredients.append(ingredient)
        recipe = match_recipe(recipe_ingredients)
        default_name = ' with '.join(names)
        if recipe:
            self.properties.update(recipe.properties)
            self.name = '{} ({})'.format(recipe.name, default_name)
        else:
            self.name = default_name
        cooked.append(self)

    def get_prepared_ingredients(self):
        return ['{} {}'.format(preparation, ingredient) for preparation, ingredient in self.ingredients]


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
        if len(data.get('ingredients')) != 3:
            raise RuntimeError('Recipes must consist of 3 ingredients')
        for ingredient_property_data in data.get('ingredients'):
            self.ingredient_properties.append(set(ingredient_property_data))
        self.properties = data.get('properties')
        self.properties.append(self.name.lower())


class SavedDish(Recipe):
    ingredients = None

    def __init__(self, name, food):
        self.name = name
        self.ingredients = food.ingredients
        self.ingredient_properties = []
        self.properties = []
        for preparation, ingredient in self.ingredients:
            self.ingredient_properties.append({preparation, ingredient.name})

    def get_ingredients(self):
        return [ingredient.name for preparation, ingredient in self.ingredients]

    def get_prepared_ingredients(self):
        return [(preparation, ingredient.name) for preparation, ingredient in self.ingredients]

    def can_be_cooked(self):
        available_ingredients = storage.available_ingredients()
        available_preparations = kitchen.available_preparation_results()
        for preparation, ingredient in self.ingredients:
            if preparation not in available_preparations:
                return False
            amount = available_ingredients.get(ingredient.name, 0)
            if amount < 1:
                return False
            available_ingredients.update({ingredient.name: amount - 1})
        return True


recipes = None
dishes = []
cooked = []


def get(name):
    global cooked
    for dish in cooked:
        if dish.name == name:
            return dish
    return None


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
    global dishes
    global recipes
    for recipe in dishes + list(recipes.values()):
        if recipe.consists_of(ingredients):
            return recipe
    return None


def save_dish(name, new_name):
    global dishes
    global cooked
    if name in dishes: dishes.remove(name)
    cooked_dish = get(name)
    recipe = SavedDish(new_name, cooked_dish)
    dishes.append(recipe)
    for dish in cooked:
        if dish.name == name:
            ingredients =  {'{} {}'.format(
                preparation, ingredient) for preparation, ingredient in recipe.get_prepared_ingredients()}
            dish.name = '{} ({})'.format(new_name, ' with '.join(ingredients))


def get_dishes():
    global dishes
    return [dish.name for dish in dishes]


def get_dish(name):
    global dishes
    for dish in dishes:
        if dish.name == name:
            return dish
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
    global dishes
    global cooked
    pickle.dump(recipes, file)
    pickle.dump(dishes, file)
    pickle.dump(cooked, file)


def load(file):
    global recipes
    global dishes
    global cooked
    recipes = pickle.load(file)
    dishes = pickle.load(file)
    cooked = pickle.load(file)


def debug():
    global recipes
    global cooked
    for recipe in recipes.values():
        recipe.debug()
    for food in cooked:
        food.debug()
