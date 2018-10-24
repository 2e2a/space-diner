from collections import OrderedDict

from . import food


class Guest(generic.Thing):
    name = None
    available = False

    def serve(self, food_name):
        dish = food.take(food_name)
        print('')
        print('*** {}: "Tasted {}!" ***'.format(self.name, dish.taste))
        print('')

    def load(self, data):
        self.name = data.get('name')
        self.available = data.get('available')


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
