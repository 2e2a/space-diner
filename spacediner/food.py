from collections import OrderedDict


class Food:
    name = None
    taste = None
    ingredients = {}

    def __init__(self, ingredients=None):
        if ingredients:
            self.cook(ingredients)

    def cook(self, ingredients):
        self.ingredients = ingredients
        name = []
        taste = []
        for ingredient in ingredients:
            name.append(ingredient.name)
            taste.append(ingredient.taste)
        self.name = 'cooked ' + '-'.join(name)
        self.taste = '-'.join(taste)


class Recipe(Food):
    available = False

    def load(self, data):
        self.name = data.get('name')
        self.taste = data.get('taste')
        self.available = data.get('available')


recipes = None
food = OrderedDict()


def load(data):
    global recipes
    recipes = OrderedDict()
    for recipe_data in data:
        recipe = Recipe()
        recipe.load(recipe_data)
        recipes.update({recipe.name: recipe})


def cook(ingredients):
    global food
    cooked_food = Food(ingredients)
    food.update({cooked_food.name: cooked_food})
    print(food)
