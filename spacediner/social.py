from collections import OrderedDict

from . import guests


class Reward:
    TYP_UNLOCK_GUEST = 'unlock_guest'

    typ = None
    level = None


class RewardUnlockGuest(Reward):
    guest = None

    def __init__(self):
        self.typ = self.TYP_UNLOCK_GUEST

    def load(self, data):
        self.level = data.get('level')
        self.guest = data.get('guest')

    def apply(self):
        print('*** New guest unlocked. ***' )
        guests.unlock(self.guest)


class Chat:
    question = None
    replies = None
    reactions = None
    effects = None

    def load(self, data):
        self.question = data.get('question')
        self.effects = []
        self.replies = []
        self.reactions = []
        for reply_data in data.get('replies', []):
            self.effects.append(reply_data[0])
            self.replies.append(reply_data[1])
            self.reactions.append(reply_data[2])

    def effect(self, reply):
        return self.effects[reply] if self.replies else None

    def reaction(self, reply):
        return self.reactions[reply] if self.reactions else None


class Relation:
    name = None
    chats = None
    chats_done = None
    level = 0
    rewards = None

    def load(self, data):
        self.name = data.get('name')
        self.chats = []
        self.chats_done = 0
        self.level = 0
        for chat_data in data.get('chats'):
            chat = Chat()
            chat.load(chat_data)
            self.chats.append(chat)
        self.rewards = {}
        for reward_data in data.get('rewards', []):
            typ = reward_data.get('typ')
            if typ == Reward.TYP_UNLOCK_GUEST:
                reward = RewardUnlockGuest()
                reward.load(reward_data)
            self.rewards.update({reward.level: reward})

    def level_up(self):
        self.level += 1
        reward = self.rewards.get(self.level)
        if reward:
            reward.apply()

    def level_down(self):
        self.level -= 1

    def chat(self, reply):
        chat = self.chats[self.chats_done]
        effect = chat.effect(reply)
        reaction = chat.reaction(reply)
        if effect > 0:
            self.level_up()
        elif effect < 0:
            self.level_down()
        self.chats_done += 1
        if self.chats_done >= len(self.chats):
            self.chats_done = 0
        return effect, reaction

    def taste(self, taste):
        if taste >= 5:
            self.level_up()
        elif taste <= 0:
            self.level_down()



relations = None


def get(name):
    global relations
    return relations.get(name)


def chats_available():
    global relations
    return list(relations.keys())


def next_chat(name):
    global relations
    guest_relations = relations.get(name)
    chat = guest_relations.chats[guest_relations.chats_done]
    return chat


def chat(name, reply):
    global relations
    guest_relation = relations.get(name)
    return guest_relation.chat(reply)


def taste(name, taste):
    global relations
    relation = relations.get(name)
    relation.taste(taste)


def level(name):
    global relations
    guest_relation = relations.get(name)
    return guest_relation.level


def load(data):
    global relations
    relations = OrderedDict()
    for relation_data in data:
        relation = Relation()
        relation.load(relation_data)
        relations.update({relation.name: relation})


def debug():
    global relations
    for relation in relations.values():
        relation.debug()
