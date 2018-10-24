from collections import OrderedDict

from . import food
from . import generic


class Reaction(generic.Thing):
    properties = None
    taste = 1
    output = None

    def perform(self, *args, **kwargs):
        pass

    def load(self, data):
        self.properties = data.get('properties')
        self.taste = int(data.get('taste'))
        self.output = data.get('output')

    def __str__(self):
        return '{} -> {}'.format(str(self.properties), str(self.taste))


class Guest(generic.Thing):
    name = None
    available = False
    taste = None # TODO: tuple taste x reaction sentence
    reactions = None

    def react(self, reaction):
        print(reaction.output)

    def serve(self, food_name):
        dish = food.take(food_name)
        for reaction in self.reactions:
            if set(reaction.properties).intersection(dish.properties):
                self.react(reaction)

    def load(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.reactions = []
        for reaction_data in data.get('reactions'):
            reaction = Reaction()
            reaction.load(reaction_data)
            self.reactions.append(reaction)


guests = None


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
    global guests
    guests = OrderedDict()
    for guest_data in data:
        guest = Guest()
        guest.load(guest_data)
        guests.update({guest.name: guest})


def debug():
    global guests
    for guest in guests.values():
        guest.debug()

