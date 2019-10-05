import pickle
import random

from collections import OrderedDict


class Language:
    name = None
    name_factory = None
    taste = None
    reviews = None

    def init(self, data):
        self.name = data.get('name')
        self.name_factory = NameFactory()
        self.name_factory.init(data.get('name factory'))
        self.taste = data.get('taste') if data and 'taste' in data else ['Very bad.', 'Bad.', 'OK.', 'Good.', 'Very good.']
        self.reviews = Reviews()
        self.reviews.init(data.get('reviews'))


class NameFactory:
    names = None

    def init(self, data):
        self.names = data

    def create(self):
        return ' '.join(random.SystemRandom().choice(part) for part in self.names)


class Reviews:
    is_default = True
    like = None
    dislike = None
    order_met = None
    order_not_met = None
    no_food = None

    def init(self, data):
        self.like = data.get('like') if data and 'like' in data else 'I liked the {}.'
        self.dislike = data.get('dislike') if data and 'dislike' in data else 'I did not like the {}.'
        self.order_met = data.get('order_met') if data and 'order_met' in data else 'I got what I ordered ({}).'
        self.order_not_met = data.get('order_not_met') if data and 'order_not_met' in data else 'I got not what I ordered ({}).'
        self.no_food = data.get('no_food') if data and 'no_food' in data else 'I did not get any food.'

languages = None


def get(name):
    global languages
    return languages.get(name)


def init(data):
    global languages
    languages = OrderedDict()
    for language_data in data:
        language = Language()
        language.init(language_data)
        languages.update({language.name: language})


def save(file):
    global languages
    pickle.dump(languages, file)


def load(file):
    global languages
    languages = pickle.load(file)


def debug():
    global guests
    for guest in guests:
        guest.debug()
    global guest_groups
    for guest_group in guest_groups.values():
        guest_group.debug()
    global guest_factory
    guest_factory.debug()
