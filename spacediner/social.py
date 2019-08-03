import pickle

from collections import OrderedDict

from . import guests
from . import rewards


class Chat:
    question = None
    replies = None
    reactions = None
    effects = None

    def init(self, data):
        self.question = data.get('question')
        self.effects = []
        self.replies = []
        self.reactions = []
        for reply_data in data.get('replies', []):
            self.effects.append(reply_data[0])
            if len(reply_data) > 1:
                self.replies.append(reply_data[1])
            if len(reply_data) > 2:
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

    def init(self, data):
        self.name = data.get('name')
        self.chats = []
        self.chats_done = 0
        self.level = 0
        if 'chats' in data:
            for chat_data in data.get('chats'):
                chat = Chat()
                chat.init(chat_data)
                self.chats.append(chat)
        if 'rewards' in data:
            self.rewards = {reward.level: reward for reward in rewards.init_list(data.get('rewards'))}

    def level_up(self):
        self.level += 1
        reward = self.rewards.get(self.level)
        if reward:
            reward.apply()
        return self.level

    def level_down(self):
        self.level -= 1
        return self.level

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
        if taste >= 4:
            self.level_up()
        elif taste <= 0:
            self.level_down()


relations = None


def get(name):
    global relations
    return relations.get(name)


def chats_available():
    global relations
    chats = [guest for guest, relation in relations.items() if relation.chats]
    return chats


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


def level_up(name):
    global relations
    guest_relation = relations.get(name)
    return guest_relation.level_up()


def level_down(name):
    global relations
    guest_relation = relations.get(name)
    return guest_relation.level_down()


def init(data):
    global relations
    relations = OrderedDict()
    for relation_data in data:
        relation = Relation()
        relation.init(relation_data)
        relations.update({relation.name: relation})
    for guest in guests.get_names():
        if guest not in relations:
            relation = Relation()
            relation.name = guest
            relations.update({guest: relation})


def save(file):
    global relations
    pickle.dump(relations, file)


def load(file):
    global relations
    relations = pickle.load(file)


def debug():
    global relations
    for relation in relations.values():
        relation.debug()
