import pickle

from collections import OrderedDict

from . import kitchen
from . import storage


class Food:
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

    def ingredient_properties(self, num):
        if num < len(self.ingredients):
            _, ingredient = self.ingredients[num]
            return list(ingredient.properties)

    @property
    def default_name(self):
        ingredient_names = [
            '{} {}'.format(preparation, ingredient.name) for preparation, ingredient in self.ingredients
        ]
        unique_ingredients = list(set(ingredient_names))
        if len(unique_ingredients) == 1:
            return 'plain {}'.format(unique_ingredients[0])
        elif len(unique_ingredients) == 2:
            main_ingredient = unique_ingredients[0]
            second_ingredient = unique_ingredients[1]
            if ingredient_names.count(main_ingredient) == 1:
                main_ingredient = unique_ingredients[1]
                second_ingredient = unique_ingredients[0]
            return '{} with some {}'.format(main_ingredient, second_ingredient)
        return' with '.join(ingredient_names)

    def set_default_name(self):
        self.name = self.default_name

    def set_custom_name(self, name):
        self.name = '{} ({})'.format(name, self.default_name)

    def plate(self):
        global cooked
        self.properties = set()
        recipe_ingredients = []
        for preparation, ingredient in self.ingredients:
            self.properties.update(ingredient.properties)
            recipe_ingredients.append((preparation, ingredient))
        recipe = match_recipe(recipe_ingredients)
        if recipe:
            self.properties.update(recipe.properties)
            self.set_custom_name(recipe.name)
        else:
            self.set_default_name()
        cooked.append(self)

    def get_prepared_ingredients(self):
        return ['{} {}'.format(preparation, ingredient) for preparation, ingredient in self.ingredients]


class Recipe:
    name = None
    available = True
    ingredient_properties = None
    properties = None

    def _properties_match(self, recipe_ingredient_properties, ingredients):
        if not recipe_ingredient_properties:
            return True
        for recipe_properties in recipe_ingredient_properties:
            for i, (preparation, ingredient) in enumerate(ingredients):
                if set(recipe_properties).issubset(ingredient.properties):
                    remaining_recipe_ingredient_properties = recipe_ingredient_properties.copy()
                    remaining_recipe_ingredient_properties.remove(recipe_properties)
                    remaining_ingredients = ingredients.copy()
                    del remaining_ingredients[i]
                    if self._properties_match(remaining_recipe_ingredient_properties, remaining_ingredients):
                        return True
        return False

    def consists_of(self, ingredients):
        return self._properties_match(self.ingredient_properties, ingredients)

    def new(self, name, ingredient_properties):
        self.name = name
        self.ingredient_properties = ingredient_properties
        self.properties = []

    def init(self, data):
        self.name = data.get('name')
        self.available = data.get('available', self.available)
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
            self.ingredient_properties.append([preparation, ingredient.name])

    def get_ingredients(self):
        return [ingredient.name for preparation, ingredient in self.ingredients]

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
cooked = []
menu = []
dishes = []


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


def save_as_recipe(name, ingredient_properties):
    global recipes
    recipe = Recipe()
    recipe.new(name, ingredient_properties)
    recipes[recipe.name] = recipe
    update_plated()


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


def get_menu():
    global menu
    return menu


def update_menu(item, name):
    global menu
    menu[item - 1] = name


def not_on_menu():
    return list(set(get_recipes()) - set(get_menu()))


def update_plated():
    global cooked
    global recipes
    for food in cooked:
        recipe = match_recipe(food.ingredients)
        if recipe:
            food.set_custom_name(recipe.name)


def save_dish(name, new_name):
    global dishes
    global cooked
    if name in dishes:
        dishes.remove(name)
    cooked_dish = get(name)
    recipe = SavedDish(new_name, cooked_dish)
    dishes.append(recipe)


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
    global menu
    recipes = OrderedDict()
    for recipe_data in data.get('recipes'):
        recipe = Recipe()
        recipe.init(recipe_data)
        recipes.update({recipe.name: recipe})
    menu = data.get('menu', [])
    assert len(set(menu)) == 5
    for menu_item in menu:
        assert get_recipe(menu_item) is not None


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
