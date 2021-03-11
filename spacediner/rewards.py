from . import cli
from . import diner
from . import food
from . import guests
from . import levels
from . import shopping
from . import skills
from . import storage


class Reward:
    TYPE_MERCHANT = 'merchant'
    TYPE_GUEST = 'guest'
    TYPE_SKILL = 'skill'
    TYPE_INGREDIENT = 'ingredient'
    TYPE_MONEY = 'money'
    TYPE_DECORATION = 'decoration'
    TYPE_RECIPE = 'recipe'

    typ = None
    text = None

    def init(self, data):
        self.text = data.get('text')

    def can_apply(self):
        return True

    def apply(self):
        raise NotImplemented


class MerchantReward(Reward):
    merchant = None

    def __init__(self):
        self.typ = self.TYPE_MERCHANT

    def init(self, data):
        super().init(data)
        self.merchant = data.get('merchant')

    def apply(self):
        cli.print_message('New merchant unlocked')
        shopping.unlock(self.merchant)


class GuestReward(Reward):
    guest = None

    def __init__(self):
        self.typ = self.TYPE_GUEST

    def init(self, data):
        super().init(data)
        self.guest = data.get('guest')

    def apply(self):
        cli.print_message('New type of guest unlocked')
        guests.unlock(self.guest)


class SkillReward(Reward):
    skill = None
    diff = None

    def __init__(self):
        self.typ = self.TYPE_SKILL

    def init(self, data):
        super().init(data)
        self.skill = data.get('skill')
        self.diff = data.get('diff')

    def can_apply(self):
        return skills.can_add(self.skill, self.diff)

    def apply(self):
        skills.add(self.skill, self.diff)


class IngredientReward(Reward):
    ingredient = None
    diff = None

    def __init__(self):
        self.typ = self.TYPE_INGREDIENT

    def init(self, data):
        super().init(data)
        self.ingredient = data.get('ingredient')
        self.diff = data.get('diff')

    def apply(self):
        if self.diff > 0 and storage.store_ingredient(self.ingredient, self.diff):
            cli.print_message('Gained {} x {}.'.format(self.diff, self.ingredient))
        else:
            cli.print_message('Lost {} x {}.'.format(abs(self.diff), self.ingredient))


class MoneyReward(Reward):
    money = None
    diff = None

    def __init__(self):
        self.typ = self.TYPE_MONEY

    def init(self, data):
        super().init(data)
        self.money = data.get('money')
        self.diff = data.get('diff')

    def apply(self):
        levels.level.money += self.diff
        if self.diff > 0:
            cli.print_message('Gained {} space dollars.'.format(self.money))
        else:
            cli.print_message('Lost {} space dollars.'.format(abs(self.diff)))


class DecorationReward(Reward):
    decoration = None

    def __init__(self):
        self.typ = self.TYPE_DECORATION

    def init(self, data):
        super().init(data)
        self.decoration = data.get('decoration')

    def apply(self):
        diner.add_decoration(self.decoration)
        cli.print_message('You received a gift: {}.'.format(self.decoration))


class RecipeReward(Reward):
    recipe = None

    def __init__(self):
        self.typ = self.TYPE_RECIPE

    def init(self, data):
        super().init(data)
        self.recipe = data.get('recipe')

    def apply(self):
        cli.print_message('New recipe unlocked')
        food.unlock_recipe(self.recipe)

def init_list(data):
    rewards = []
    for reward_data in data:
        typ = reward_data.get('type')
        reward = None
        if typ == Reward.TYPE_MERCHANT:
            reward = MerchantReward()
        elif typ == Reward.TYPE_GUEST:
            reward = GuestReward()
        elif typ == Reward.TYPE_SKILL:
            reward = SkillReward()
        elif typ == Reward.TYPE_MONEY:
            reward = MoneyReward()
        elif typ == Reward.TYPE_INGREDIENT:
            reward = IngredientReward()
        elif typ == Reward.TYPE_DECORATION:
            reward = DecorationReward()
        elif typ == Reward.TYPE_RECIPE:
            reward = RecipeReward()
        reward.init(reward_data)
        rewards.append(reward)
    return rewards
