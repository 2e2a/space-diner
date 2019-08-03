import itertools
import pickle
import random
from collections import OrderedDict

from . import food
from . import generic
from . import levels
from . import social
from . import time


class Reaction(generic.Thing):
    properties = None
    taste = 0
    output = None

    def init(self, data):
        self.properties = data.get('properties')
        self.taste = data.get('taste')
        self.output = data.get('output')

    def __str__(self):
        return '{} -> {}'.format(str(self.properties), str(self.taste))


class Guest(generic.Thing):
    name = None
    budget = 0
    available = False
    reactions = None
    taste = None
    orders = None
    order = None
    chatted_today = False

    def react(self, reaction, properties):
        print('{}: "{}, {}"'.format(
            self.name,
            ', '.join(properties),
            reaction.output
        ))

    def get_order(self):
        if self.order:
            return self.order
        if not self.orders:
            return None
        self.order = random.SystemRandom().choice(self.orders)
        return self.order

    def serve(self, food_name):
        dish = food.take(food_name)
        taste = 2
        for reaction in self.reactions:
            matching_properties = set(reaction.properties).intersection(dish.properties)
            if matching_properties:
                self.react(reaction, matching_properties)
                taste += reaction.taste
        if self.orders:
            if not self.order:
                print('{}: "You could have taken my order first."'.format(self.name))
                taste -= 1
            elif self.order in dish.properties:
                print('{}: "Mhh... {}-ish, like ordered."'.format(self.name, self.order))
                taste += 2
            else:
                print('{}: "Not really {}-ish..."'.format(self.name, self.order))
                taste -= 2
        if taste > 4: taste = 4
        elif taste < 0: taste = 0
        payment = int(self.budget/5 * taste)
        levels.level.money += payment
        print('{}: "{}"'.format(self.name, self.taste[taste]))
        print('{} payed {} space dollars.'.format(self.name, payment))
        print('{} left.'.format(self.name))
        return taste

    def init(self, data):
        self.name = data.get('name')
        self.budget = data.get('budget')
        self.available = data.get('available')
        self.reactions = []
        for reaction_data in data.get('reactions'):
            reaction = Reaction()
            reaction.init(reaction_data)
            self.reactions.append(reaction)
        self.taste = data.get('taste', ['Very Bad', 'Bad', 'OK', 'Good', 'Very Good' ])
        self.orders = data.get('orders', [])


class GuestGroup(Guest):
    pass


class GuestFactory(generic.Thing):
    groups = None
    names = {}

    def init(self, data):
        self.groups = []
        self.names = []
        for groups in data:
            self.groups.append(groups)
            self.names.append(' '.join(group for group in groups))

    def create(self):
        global guest_groups
        num = random.SystemRandom().randint(0, len(self.groups) - 1)
        guest = Guest()
        guest.name = self.names[num]
        groups = [guest_groups.get(name) for name in self.groups[num]]
        guest.reactions = list(itertools.chain.from_iterable(group.reactions for group in groups))
        guest.budget = max([group.budget for group in groups])
        guest.available = True
        guest.taste = []
        for i in range(5):
            group = random.SystemRandom().randint(0, len(groups) - 1)
            guest.taste.append(groups[group].taste[i])
        guest.orders = list(itertools.chain.from_iterable(group.orders for group in groups))
        return guest


guests = None
regulars = None
guest_groups = None
guest_factory = None


def get_names():
    global regulars
    global guest_factory
    names = [name for name in regulars.keys()]
    names.extend(guest_factory.names)
    return names


def available_guests():
    global guests
    return [guest.name for guest in guests]


def get(name):
    global guests
    for guest in guests:
        if guest.name == name:
            return guest
    return None


def get_order(name):
    guest = get(name)
    return guest.get_order()


def serve(name, food):
    global guests
    guest = get(name)
    if guest and guest.available:
        taste = guest.serve(food)
        guests.remove(guest)
    return taste


def new_workday():
    global guests
    global regulars
    global guest_factory
    guests = [regular for regular in regulars.values() if regular.available]
    for regular in guests:
        regular.order = None
        regular.chatted_today = False
    for i in range(2):  # TODO: guest max
        guest = guest_factory.create()
        guests.append(guest)


def unlock(name):
    global regulars
    global guest_factory
    guest = regulars.get(name)
    if not guest:
        guest = guest_factory.get(name)
    if guest:
        guest.available = True


def init(data):
    global regulars
    regulars = OrderedDict()
    for guest_data in data.get('regulars'):
        guest = Guest()
        guest.init(guest_data)
        regulars.update({guest.name: guest})

    global guest_groups
    guest_groups = OrderedDict()
    for group_data in data.get('groups'):
        group = GuestGroup()
        group.init(group_data)
        guest_groups.update({group.name: group})

    global guest_factory
    guest_factory = GuestFactory()
    guest_factory.init(data.get('factory'))

    time.register_callback(time.Clock.TIME_WORK, new_workday)


def save(file):
    global guests
    global regulars
    global guest_groups
    global guest_factory
    pickle.dump(guests, file)
    pickle.dump(regulars, file)
    pickle.dump(guest_groups, file)
    pickle.dump(guest_factory, file)


def load(file):
    global guests
    global regulars
    global guest_groups
    global guest_factory
    guests = pickle.load(file)
    regulars = pickle.load(file)
    guest_groups = pickle.load(file)
    guest_factory = pickle.load(file)


def debug():
    global guests
    for guest in guests:
        guest.debug()
    global guest_groups
    for guest_group in guest_groups.values():
        guest_group.debug()
    global guest_factory
    guest_factory.debug()
