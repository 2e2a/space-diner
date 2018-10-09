from collections import OrderedDict

from . import storage


class Food:
    name = None
    taste = None
    ingredients = []

    def __init__(self, ingredients=None):
        if ingredients:
            self.cook(ingredients)

    def cook(self, ingredients):
        self.ingredients = ingredients
        name = []
        taste = []
        for ingredient_name in ingredients:
            ingredient = storage.take_ingredient(ingredient_name)
            name.append(ingredient.name)
            taste.append(ingredient.taste)
        recipe = get_recipe(ingredients)
        if recipe:
            self.name = recipe.name
            self.taste = recipe.taste
        else:
            self.name = 'cooked ' + '-'.join(name)
            self.taste = '-'.join(taste)

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


def cook(ingredients):
    global cooked
    food = Food(ingredients)
    cooked.update({food.name: food})
