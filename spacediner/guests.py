import itertools
import random
from collections import OrderedDict

from . import food
from . import generic
from . import levels


class Reaction(generic.Thing):
    properties = None
    taste = 0
    output = None

    def load(self, data):
        self.properties = data.get('properties')
        self.taste = data.get('taste')
        self.output = data.get('output')

    def __str__(self):
        return '{} -> {}'.format(str(self.properties), str(self.taste))


class Guest(generic.Thing):
    name = None
    budget = 0
    available = False
    taste = None # TODO: tuple taste x reaction sentence
    reactions = None

    def react(self, reaction):
        print('{}: ""'.format(self.name, reaction.output))

    def serve(self, food_name):
        dish = food.take(food_name)
        taste = 0
        for reaction in self.reactions:
            if set(reaction.properties).intersection(dish.properties):
                self.react(reaction)
                taste += reaction.taste
        # TODO: print overall reaction
        payment = int(self.budget/5 * taste)
        levels.level.money += payment
        print('{} payed {} space dollars.'.format(self.name, payment))



    def load(self, data):
        self.name = data.get('name')
        self.budget = data.get('budget')
        self.available = data.get('available')
        self.reactions = []
        for reaction_data in data.get('reactions'):
            reaction = Reaction()
            reaction.load(reaction_data)
            self.reactions.append(reaction)


class GuestGroup(Guest):
    pass


class GuestFactory(generic.Thing):
    groups = None

    def load(self, data):
        self.groups = []
        for groups in data:
            self.groups.append(groups)

    def create(self):
        global guest_groups
        num = random.SystemRandom().randint(0, len(self.groups) - 1)
        guest = Guest()
        groups = [guest_groups.get(name) for name in self.groups[num]]
        guest.name = ' '.join(group.name for group in groups)
        guest.reactions = list(itertools.chain.from_iterable(group.reactions for group in groups))
        guest.budget = max([group.budget for group in groups])
        guest.available = True
        return guest


guests = None
regulars = None
guest_groups = None
guest_factory = None


def available_guests():
    global guests
    available_guests = {}
    for available_guest in filter(lambda g: g.available, guests.values()):
        available_guests.update({available_guest.name: available_guest})
    return available_guests


def serve(name, food):
    global guests
    guest = guests.get(name)
    if guest and guest.available:
        guest.serve(food)


def load(data):
    global regulars
    regulars = OrderedDict()
    for guest_data in data.get('regulars'):
        guest = Guest()
        guest.load(guest_data)
        regulars.update({guest.name: guest})

    global guest_groups
    guest_groups = OrderedDict()
    for group_data in data.get('groups'):
        group = GuestGroup()
        group.load(group_data)
        guest_groups.update({group.name: group})

    global guest_factory
    guest_factory = GuestFactory()
    guest_factory.load(data.get('factory'))

    # TODO: move somewhere else
    new_day()


def new_day():
    global guests
    global regulars
    global guest_factory
    guests = OrderedDict(regulars)
    for i in range(4):
        guest = guest_factory.create()
        guests.update({guest.name: guest})


def debug():
    global guests
    for guest in guests.values():
        guest.debug()
    global guest_groups
    for guest_group in guest_groups.values():
        guest_group.debug()
    global guest_factory
    guest_factory.debug()
