from . import cli
from . import guests
from . import merchants
from . import skills


class Reward:
    TYPE_MERCHANT = 'merchant'
    TYPE_GUEST = 'guest'
    TYPE_SKILL = 'skill'

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
        merchants.unlock(self.merchant)


class GuestReward(Reward):
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
        if self.diff > 0:
            cli.print_message('{} increased by {}'.format(self.skill, self.diff))
        else:
            cli.print_message('{} decreased by {}'.format(self.skill, self.diff))
        skills.add(self.skill, self.diff)


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
