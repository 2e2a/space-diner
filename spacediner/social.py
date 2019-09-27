import pickle
from collections import OrderedDict

from . import guests
from . import rewards


class Chats:
    chats = None
    done = 0

    def init(self, data):
        if data:
            self.chats = []
            for chat in data:
                self.chats.append(chat)

    def chat(self):
        if self.chats:
            return self.chats[self.done]

    def next(self):
        if self.chats:
            self.done += 1
            return self.chat()


class Meeting:
    question = None
    replies = None
    reactions = None
    effects = None

    def init(self, data):
        return
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


class Social:
    name = None
    level = 0
    chats = None
    meetings = None
    meetings_done = None
    rewards = None

    def init(self, data):
        self.name = data.get('name')
        self.level = 0
        if 'chats' in data:
            self.chats = Chats()
            self.chats.init(data.get('chats'))
        if 'rewards' in data:
            self.rewards = {reward.level: reward for reward in rewards.init_list(data.get('rewards'))}

    def level_up(self):
        self.level += 1
        if self.rewards:
            reward = self.rewards.get(self.level)
            if reward:
                reward.apply()
        return self.level

    def level_down(self):
        self.level -= 1
        return self.level

    def chat(self):
        return self.chats.chat() if self.chats else None

    def next_chat(self):
        return self.chats.next() if self.chats else None

    def next_meeting(self):
        chat = self.chats[self.chats_done]
        self.chats_done += 1
        if self.chats_done >= len(self.chats):
            self.chats_done = 0
        return chat

    def meet(self, reply):
        chat = self.chats[self.chats_done]
        effect = chat.effect(reply)
        reaction = chat.reaction(reply)
        if effect > 0:
            self.level_up()
        elif effect < 0:
            self.level_down()
        return effect, reaction


social = None


def get(name):
    global social
    guest_social = social.get(name)
    if guest_social:
        return guest_social
    base_name = guests.get_base_name(name)
    return social.get(base_name)


def chats_available():
    global social
    chats = [guest for guest, social in social.items() if social.chats.chat()]
    return chats


def chat(name):
    return get(name).chat()


def next_chat(name):
    return get(name).next_chat()


def level(name):
    global social
    guest_social = get(name)
    return guest_social.level


def level_up(name):
    guest_social = get(name)
    return guest_social.level_up()


def level_down(name):
    guest_social = get(name)
    return guest_social.level_down()


def init(data):
    global social
    social = OrderedDict()
    for social_data in data:
        guest_social = Social()
        guest_social.init(social_data)
        social.update({guest_social.name: guest_social})


def save(file):
    global social
    pickle.dump(social, file)


def load(file):
    global social
    social = pickle.load(file)


def debug():
    global social
    for guest_social in social.values():
        guest_social.debug()
