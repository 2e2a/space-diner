from collections import OrderedDict


class Talk:
    question = None
    replies = None
    effects = None

    def load(self, data):
        self.question = data.get('question')
        self.effects = []
        self.replies = []
        self.reactions = []
        for reply_data in data.get('replies'):
            self.effects.append(reply_data[0])
            self.replies.append(reply_data[1])
            self.reactions.append(reply_data[2])

    def effect(self, reply):
        return self.effects[reply]

    def reaction(self, reply):
        return self.reactions[reply]


class Relation:
    name = None
    talks = None
    talks_done = None
    level = 0

    def load(self, data):
        self.name = data.get('name')
        self.talks = []
        self.talks_done = 0
        self.level = 0
        for talk_data in data.get('talks'):
            talk = Talk()
            talk.load(talk_data)
            self.talks.append(talk)

    def talk(self, reply):
        talk = self.talks[self.talks_done]
        effect = talk.effect(reply)
        reaction = talk.reaction(reply)
        self.level += effect
        self.talks_done += 1
        if self.talks_done >= len(self.talks):
            self.talks_done = 0
        return (effect, reaction)


relations = None


def get(name):
    global relations
    return relations.get(name)


def talks_available():
    global relations
    return list(relations.keys())


def next_talk(name):
    global relations
    guest_relations = relations.get(name)
    talk = guest_relations.talks[guest_relations.talks_done]
    return talk


def talk(name, reply):
    global relations
    guest_relation = relations.get(name)
    return guest_relation.talk(reply)


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
