from collections import OrderedDict


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

    def load(self, data):
        self.name = data.get('name')
        self.chats = []
        self.chats_done = 0
        self.level = 0
        for chat_data in data.get('chats'):
            chat = Chat()
            chat.load(chat_data)
            self.chats.append(chat)

    def chat(self, reply):
        chat = self.chats[self.chats_done]
        effect = chat.effect(reply)
        reaction = chat.reaction(reply)
        self.level += effect
        self.chats_done += 1
        if self.chats_done >= len(self.chats):
            self.chats_done = 0
        return (effect, reaction)


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
