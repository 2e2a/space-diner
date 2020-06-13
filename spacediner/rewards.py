from . import cli
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

    typ = None
    text = None

    def apply(self):
        raise NotImplemented

    def init(self, data):
        self.text = data.get('text')


class SocialReward(Reward):
    level = None

    def init(self, data):
        super().init(data)
        self.level = data.get('level')

    def apply(self):
        raise NotImplemented


class MerchantReward(SocialReward):
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
    level = None
    guest = None

    def __init__(self):
        self.typ = self.TYPE_GUEST

    def init(self, data):
        super().init(data)
        self.level = data.get('level')
        self.guest = data.get('guest')

    def apply(self):
        cli.print_message('New guest unlocked')
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
            cli.print_message('Gained {}x{}.'.format(self.diff, self.ingredient))
        else:
            cli.print_message('Lost {}x{}.'.format(abs(self.diff), self.ingredient))


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
        reward.init(reward_data)
        rewards.append(reward)
    return rewards
