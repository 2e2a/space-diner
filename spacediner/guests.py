import itertools
import pickle
import random
from collections import OrderedDict

from . import cli  #  TODO: inject
from . import food
from . import generic
from . import levels
from . import languages
from . import reviews
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



    def init(self, data):
        self.is_default = data is None


class Guest(generic.Thing):
    name = None
    description = None
    groups = None
    main_group = None
    budget = 0
    available = False
    reactions = None
    orders = None
    language = None

    order = None
    chatted_today = False
    served = False

    def take_order(self):
        if self.order:
            return self.order
        if not self.orders:
            return None
        self.order = random.SystemRandom().choice(self.orders)
        return self.order

    def serve(self, food_name):
        # TODO: split in sub-functions
        self.served = True
        dish = food.take(food_name)
        taste = 2
        review = '{}:'.format(self.name)
        for reaction in self.reactions:
            matching_properties = set(reaction.properties).intersection(dish.properties)
            if matching_properties:
                taste += reaction.taste
                if reaction.taste > 0:
                    cli.print_dialog_with_info(
                        self.name,
                        'likes something ({})'.format(', '.join(matching_properties)),
                        reaction.output
                    )
                    reviews.add_likes(self.name, matching_properties)
                    review += ' ' + self.output.review_like.format('and '.join(matching_properties))
        if self.orders:
            if self.order in dish.properties:
                taste += 2
                cli.print_message('{} received what they ordered ({}).'.format(self.name, self.order))
                review += ' ' + self.output.review_order_met.format(self.order)
            else:
                taste = min(2, taste - 1)
                cli.print_message('{} did not receive what they ordered ({}).'.format(self.name, self.order))
                review += ' ' + self.output.review_order_not_met.format(self.order)
        if taste > 4: taste = 4
        elif taste < 0: taste = 0
        review += ' {} (Rating: {})'.format(self.output.taste[taste], taste)
        reviews.add_rating(self.name, taste)
        reviews.add_review(review)
        cli.print_dialog(self.name, self.output.taste[taste])
        payment = int(self.budget/5 * taste)
        levels.level.money += payment
        cli.print_text('{} paid {} space dollars.'.format(self.name, payment))
        return taste

    def has_chatted_today(self):
        return self.chatted_today

    def set_chatted_today(self):
        self.chatted_today = True

    def has_chat_available(self):
        return not self.chatted_today and social.chat(self.name)

    def send_home(self):
        reviews.add_rating(self.name, 0)
        reviews.add_review('{}: {}'.format(self.name, self.output.review_no_food))

    def init(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.language = data.get('language')
        self.budget = data.get('budget')
        self.available = data.get('available')
        self.reactions = []
        for reaction_data in data.get('reactions', []):
            reaction = Reaction()
            reaction.init(reaction_data)
            self.reactions.append(reaction)
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

    def _unique_name(self, group, existing=None):
        while True:
            name = languages.get(group.language).name_factory.create()
            if not existing or not any(guest.name == name for guest in existing):
                return name

    def create(self, existing=None):
        global guest_groups
        num = random.SystemRandom().randint(0, len(self.groups) - 1)
        groups = [guest_groups.get(name) for name in self.groups[num]]
        guest = Guest()
        guest.groups = groups
        guest.main_group = groups[0].name
        guest.name = '{} ({})'.format(self._unique_name(groups[0], existing), guest.main_group)
        guest.reactions = list(itertools.chain.from_iterable(group.reactions for group in groups))
        guest.budget = max([group.budget for group in groups])
        guest.orders = list(itertools.chain.from_iterable(group.orders for group in groups))
        guest.available = True
        return guest


guests = None
regulars = None
guest_groups = None
guest_factory = None


def get_available_groups():
    global guest_groups
    return [group.name for group in guest_groups.values() if group.available]


def get_group(name):
    global guest_groups
    return guest_groups.get(name)


def get_names():
    global regulars
    global guest_factory
    names = [name for name in regulars]
    names.extend(guest_factory.names)
    return names


def available_guests():
    global guests
    return [guest.name for guest in guests]


def guests_with_orders():
    global guests
    return [guest.name for guest in filter(lambda guest: guest.order, guests)]


def guests_without_orders():
    global guests
    return [guest.name for guest in filter(lambda guest: not guest.order, guests)]


def guests_with_chats():
    global guests
    return [guest.name for guest in filter(lambda guest: guest.has_chat_available(), guests)]


def get(name):
    global guests
    for guest in guests:
        if guest.name == name:
            return guest
    return None


def get_main_group(name):
    global guests
    return get(name).main_group


def take_order(name):
    guest = get(name)
    return guest.take_order()


def get_ordered(name):
    guest = get(name)
    return guest.ordered()


def ordered():
    global guests
    return {guest.name: guest.order for guest in guests if guest.order}


def serve(name, food):
    global guests
    guest = get(name)
    if guest and guest.available:
        taste = guest.serve(food)
    return taste


def leave(name):
    global guests
    guest = get(name)
    guests.remove(guest)


def send_home(name):
    global guests
    guest = get(name)
    guest.send_home()
    guests.remove(guest)


def new_workday():
    global guests
    global regulars
    global guest_factory
    guests = [regular for regular in regulars.values() if regular.available]
    for regular in guests:
        regular.order = None
        regular.chatted_today = False
    for i in range(3):  # TODO: guest max
        guest = guest_factory.create(existing=guests)
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

    reviewing_guests = list(regulars.keys()) + list(guest_groups.keys())
    reviews.init(reviewing_guests)

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
