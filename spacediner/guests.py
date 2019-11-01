import itertools
import pickle
import random
from collections import OrderedDict

from . import cli  #  TODO: inject
from . import food
from . import generic
from . import levels
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


class GuestOutput:
    is_default = True
    taste = None
    review_like = None
    review_dislike = None
    review_order_not_met = None
    review_no_food = None

    def init(self, data):
        self.is_default = data is None
        self.scale = data.get('scale') if data and 'scale' in data else ['very bad', 'bad', 'ok', 'good', 'very good']
        self.review_like = data.get('review_like') if data and 'review_like' in data else 'I liked the {}.'
        self.review_dislike = data.get('review_dislike') if data and 'review_dislike' in data else 'I did not like the {}.'
        self.review_taste = data.get('review_taste') if data and 'review_taste' in data else 'The taste was {}.'
        self.review_service = data.get('review_service') if data and 'review_service' in data else 'The service was {}.'
        self.review_ambience = data.get('review_ambience') if data and 'review_ambience' in data else 'The ambience was {}.'
        self.review_order_not_met = data.get('review_order_not_met') if data and 'review_order_not_met' in data else 'I did not get what I ordered ({}).'
        self.review_no_food = data.get('review_no_food') if data and 'review_no_food' in data else 'I did not get any food.'


class Guest(generic.Thing):
    name = None
    name_factory = None
    description = None
    groups = None
    budget = 0
    available = False
    reactions = None
    orders = None
    output = None

    order = None
    chatted_today = False
    served = False

    ambience = 2
    first_review_choices = None
    second_review_choices = None

    def reset(self):
        self.available = True
        self.chatted_today = False
        self.first_review_choices = []
        self.second_review_choices = []
        self.second_review_choices.append(self.output.review_ambience.format(self.output.scale[self.ambience]))

    @property
    def group_name(self):
        return ' '.join(group.name for group in self.groups) if self.groups else self.name

    def take_order(self):
        if self.order:
            return self.order
        if not self.orders:
            return None
        self.order = random.SystemRandom().choice(self.orders)
        return self.order

    def add_review(self, aggregate_rating):
        review = '{} ({}):'.format(self.name, self.group_name) if self.groups else '{}:'.format(self.name)
        review += ' ' + random.SystemRandom().choice(self.first_review_choices)
        review += ' ' + random.SystemRandom().choice(self.second_review_choices)
        review += ' (Rating: {})'.format(aggregate_rating)
        reviews.add_review(review)

    def serve(self, food_name):
        self.served = True
        dish = food.take(food_name)
        taste = 2
        service = 2
        for reaction in self.reactions:
            if set(reaction.properties).issubset(dish.properties):
                taste += reaction.taste
                if reaction.taste > 0:
                    cli.print_dialog_with_info(
                        self.name,
                        'likes something ({})'.format(', '.join(reaction.properties)),
                        reaction.output
                    )
                    reviews.add_likes(self.group_name, reaction.properties)
                    self.first_review_choices.append(self.output.review_like.format(' '.join(reaction.properties)))
                else:
                    cli.print_dialog_with_info(
                        self.name,
                        'does not like something ({})'.format(', '.join(reaction.properties)),
                        reaction.output
                    )
                    reviews.add_dislikes(self.group_name, reaction.properties)
                    self.first_review_choices.append(self.output.review_dislike.format(' '.join(reaction.properties)))
        if self.orders:
            if self.order in dish.properties:
                cli.print_message('{} received what they ordered ({}).'.format(self.name, self.order))
            else:
                service -= 1
                self.second_review_choices.append(self.output.review_order_not_met.format(self.order))
                cli.print_message('{} did not receive what they ordered ({}).'.format(self.name, self.order))
        taste = min(4, max(0, taste))
        cli.print_dialog(self.name, self.output.review_taste.format(self.output.scale[taste]))
        self.first_review_choices.append(self.output.review_taste.format(self.output.scale[taste]))
        self.second_review_choices.append(self.output.review_service.format(self.output.scale[service]))
        aggregate_rating = reviews.add_rating(self.group_name, taste, service, self.ambience)
        self.add_review(aggregate_rating)
        payment = int(self.budget/5 * aggregate_rating)
        levels.level.money += payment
        cli.print_text('{} paid {} space dollars.'.format(self.name, payment))
        if taste == 4:
            social.unlock_friendship(self.group_name)
        return taste

    def has_chatted_today(self):
        return self.chatted_today

    def set_chatted_today(self):
        self.chatted_today = True

    def has_chat_available(self):
        return not self.chatted_today and social.has_chats(self.group_name) and social.chat(self.group_name)

    def send_home(self):
        aggregate_rating = reviews.add_rating(self.group_name, 0, 0, self.ambience)
        self.first_review_choices.append(self.output.review_no_food)
        self.add_review(aggregate_rating)

    def init(self, data):
        self.name = data.get('name')
        self.name_factory = data.get('name_factory')
        self.description = data.get('description')
        self.budget = data.get('budget')
        self.available = data.get('available')
        self.reactions = []
        for reaction_data in data.get('reactions', []):
            reaction = Reaction()
            reaction.init(reaction_data)
            self.reactions.append(reaction)
        self.orders = data.get('orders', [])
        output_data = data.get('output', None)
        output = GuestOutput()
        output.init(output_data)
        self.output = output


class GuestGroup(Guest):
    pass


class NameFactory:
    names = None

    def init(self, data):
        self.names = data

    def create(self):
        return ' '.join(random.SystemRandom().choice(part) for part in self.names)


class GuestFactory(generic.Thing):
    groups = None

    def init(self, data):
        self.groups = []
        for groups in data:
            self.groups.append(groups)

    def _guest_name(self, groups, existing=None):
        global name_factories
        group = None
        for group in reversed(groups):
            if group.name_factory:
                break
        while True:
            name = name_factories.get(group.name_factory).create()
            if not existing or not any(guest.name == name for guest in existing):
                return name

    def create(self, existing=None):
        global guest_groups
        num = random.SystemRandom().randint(0, len(self.groups) - 1)
        guest = Guest()
        groups = [guest_groups.get(name) for name in self.groups[num]]
        guest.name = self._guest_name(groups, existing)
        guest.groups = groups
        guest.reactions = list(itertools.chain.from_iterable(group.reactions for group in groups))
        guest.budget = max([group.budget for group in groups if group.budget])
        guest.orders = list(itertools.chain.from_iterable(group.orders for group in groups))
        guest.output = groups[0].output
        for group in groups:
            if group.output.is_default:
                guest.output = group.output
                break
        guest.reset()
        return guest


guests = None
regulars = None
guest_groups = None
name_factories = None
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


def get_group_name(name):
    return get(name).group_name


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


def unlock(name):
    global regulars
    global guest_factory
    guest = regulars.get(name)
    if not guest:
        guest = guest_factory.get(name)
    if guest:
        guest.available = True
    reviews.add([name])


def new_workday():
    global guests
    global regulars
    global guest_factory
    guests = [regular for regular in regulars.values() if regular.available]
    for regular in guests:
        regular.order = None
        regular.chatted_today = False
    new_guests =  []
    for i in range(3):  # TODO: guest max
        guest = guest_factory.create(existing=guests)
        guests.append(guest)
        new_guests.append(guest.group_name)
    reviews.add(new_guests)


def init(data):
    global regulars
    regulars = OrderedDict()
    for guest_data in data.get('regulars'):
        guest = Guest()
        guest.init(guest_data)
        guest.reset()
        regulars.update({guest.name: guest})

    global guest_groups
    guest_groups = OrderedDict()
    for group_data in data.get('groups'):
        group = GuestGroup()
        group.init(group_data)
        guest_groups.update({group.name: group})

    global name_factories
    name_factories = {}
    for name_data in data.get('names'):
        name = name_data.get('name')
        name_factory = NameFactory()
        name_factory.init(name_data.get('factory'))
        name_factories.update({name: name_factory})

    global guest_factory
    guest_factory = GuestFactory()
    guest_factory.init(data.get('factory'))

    reviews.init([regular.name for regular in regulars.values() if regular.available])

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
