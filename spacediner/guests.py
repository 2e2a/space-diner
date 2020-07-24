import itertools
import pickle
import random
from collections import OrderedDict

from . import cli
from . import diner
from . import food
from . import levels
from . import reviews
from . import skills
from . import social
from . import time


class Reaction:
    properties = None
    taste = 0
    output = None
    review_phrase = None

    def init(self, data):
        self.properties = data.get('properties')
        self.taste = data.get('taste')
        self.output = data.get('output')
        self.review_phrase = data.get('review_phrase')

    def __str__(self):
        return '{} -> {}'.format(str(self.properties), str(self.taste))


class Order:
    wish = None
    text = None

    @property
    def wish_property(self):
        return self.wish.lower()

    def init(self, data):
        self.wish = data.get('wish')
        self.text = data.get('text', 'I\'ll have something {}-ish.'.format(self.wish))

    def from_menu(self):
        self.wish = random.choice(food.get_menu())
        self.text = 'I\'ll have the {} from the menu.'.format(self.wish)


class Guest:
    name = None
    name_factory = None
    description = None
    groups = None
    budget = 0
    available = False
    days = None
    reactions = None
    orders = None
    positive_phrases = None
    neutral_phrases = None
    negative_phrases = None

    order = None
    served = False

    taste = 2
    service = 2
    ambience = 2
    review = None

    def __init__(self):
        self.positive_phrases = []
        self.neutral_phrases = []
        self.negative_phrases = []

    @property
    def group_name(self):
        return ' '.join(group.name for group in self.groups) if self.groups else self.name

    def add_decoration_review(self):
        all_decoration = diner.diner.decoration
        available_decoration = diner.diner.available_decoration
        random_decoration = random.choice(all_decoration)
        if random_decoration in available_decoration:
            self.ambience += 1
            self.review.add(2, 'decoration', random_decoration)

    def init_service(self):
        pass

    def init_ambience(self):
        if not diner.diner.is_dirty:
            self.ambience += 1
            self.review.add(2, 'diner_clean')
        elif diner.diner.is_very_dirty:
            self.ambience -= 1
            self.review.add(2, 'diner_dirty')
        self.add_decoration_review()

    def reset(self):
        self.available = True
        self.order = None
        self.review = reviews.Review(self.name, self.group_name)
        self.served = False
        self.taste = 2
        self.service = 2
        self.ambience = 2
        self.init_service()
        self.init_ambience()

    def take_order(self):
        if self.order:
            return self.order.text
        random.seed()
        custom_order = random.choice([True, False])
        if custom_order and self.orders:
            self.order = random.choice(self.orders)
        else:
            self.order = Order()
            self.order.from_menu()
        return self.order.text

    def add_review(self):
        return self.review.generate(
            self.taste,
            self.service,
            self.ambience,
            self.positive_phrases,
            self.neutral_phrases,
            self.negative_phrases,
        )

    def add_skill_review(self):
        all_skills = skills.get_skills()
        all_subskills_with_skills = []
        for skill in all_skills:
            all_subskills_with_skills.extend(
                (skill, subskill) for subskill in skill.subskills
            )
        random_skill, random_subskill = random.choice(all_subskills_with_skills)
        if random_skill.is_learned(random_subskill):
            if random_skill.typ == random_skill.TYPE_COOKING:
                self.taste += 1
            elif random_skill.typ == random_skill.TYPE_SERVICE:
                self.service += 1
            elif random_skill.typ == random_skill.TYPE_AMBIENCE:
                self.ambience += 1
            self.review.add(2, 'skill', random_skill.name, random_subskill)

    def serve(self, food_name):
        self.served = True
        served_food = food.take(food_name)
        for reaction in self.reactions:
            if served_food.has_properties(reaction.properties):
                self.taste += reaction.taste
                if reaction.taste > 0:
                    cli.print_dialog_with_info(
                        self.name,
                        'likes something ({})'.format(', '.join(reaction.properties)),
                        reaction.output
                    )
                    reviews.add_likes(self.group_name, reaction.properties)
                    self.review.add(1, 'like', reaction.review_phrase)
                else:
                    cli.print_dialog_with_info(
                        self.name,
                        'does not like something ({})'.format(', '.join(reaction.properties)),
                        reaction.output
                    )
                    reviews.add_dislikes(self.group_name, reaction.properties)
                    self.review.add(1, 'dislike', reaction.review_phrase)
        if self.orders:
            if served_food.has_properties([self.order.wish_property]):
                cli.print_message('{} received what they ordered ({}).'.format(self.name, self.order.wish))
            else:
                self.service -= 1
                self.review.add(2, 'order_not_met', self.order.wish)
                cli.print_message('{} did not receive what they ordered ({}).'.format(self.name, self.order.wish))
        self.taste = min(4, max(0, self.taste))
        self.review.add(1, 'taste', self.taste, print=True)
        self.add_skill_review()
        aggregate_rating = self.add_review()
        payment = int(self.budget/5 * aggregate_rating)
        levels.level.money += payment
        cli.print_text('{} paid {} space dollars.'.format(self.name, payment))
        if self.taste == 4:
            social.unlock_friendship(self.group_name)
        return self.taste

    def has_chat_available(self):
        return social.has_chats(self.group_name) and social.next_chat(self.group_name)

    def chat(self):
        self.service += 1
        self.review.add(2, 'chatted')
        return social.greet_and_chat(self.group_name)

    def send_home(self):
        self.taste = 0
        self.service = 0
        self.review.add(1, 'no_food')
        self.add_review()

    def init(self, data):
        self.name = data.get('name')
        self.name_factory = data.get('name_factory')
        self.description = data.get('description')
        self.budget = data.get('budget')
        self.available = data.get('available')
        self.days = data.get('days', None)
        self.reactions = []
        for reaction_data in data.get('reactions', []):
            reaction = Reaction()
            reaction.init(reaction_data)
            self.reactions.append(reaction)
        self.orders = []
        for order_data in data.get('orders', []):
            order = Order()
            order.init(order_data)
            self.orders.append(order)
        self.positive_phrases = data.get('positive_phrases', [])
        self.neutral_phrases = data.get('neutral_phrases', [])
        self.negative_phrases = data.get('negative_phrases', [])


class GuestGroup(Guest):
    pass


class NameFactory:
    names = None

    def init(self, data):
        self.names = data

    def create(self):
        random.seed()
        return ''.join(str(random.choice(part)) for part in self.names)


class GuestFactory:
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

    def get_names(self):
        return [' '.join(group) for group in self.groups]

    def create(self, name, existing=None):
        global guest_groups
        guest = Guest()
        groups = [guest_groups.get(group_name) for group_name in name.split(' ')]
        guest.name = self._guest_name(groups, existing)
        guest.groups = groups
        guest.reactions = list(itertools.chain.from_iterable(group.reactions for group in groups))
        guest.budget = max([group.budget for group in groups if group.budget])
        guest.orders = list(itertools.chain.from_iterable(group.orders for group in groups))
        for group in groups:
            guest.positive_phrases += group.positive_phrases
            guest.neutral_phrases += group.neutral_phrases
            guest.negative_phrases += group.negative_phrases
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


def chat(name):
    guest = get(name)
    return guest.chat()


def take_order(name):
    guest = get(name)
    return guest.take_order()


def get_ordered(name):
    guest = get(name)
    return guest.ordered()


def ordered():
    global guests
    return {guest.name: guest.order.wish for guest in guests if guest.order}


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


FULL_AFTER_RATINGS = 10
RANDOM_GUESTS = 2


def _new_guests(seats):
    # TODO: numbers are not completely right: e.g., 4 colonists and 2 tourists when 6 seats are available?
    seats_remaining = seats
    new_guests = []
    groups = guest_factory.get_names()
    seats_per_group = int(seats/len(groups))
    extra_seats = seats - (seats_per_group * len(groups))
    ratings = reviews.get_ratings()
    empty_groups = []
    random.seed()
    random.shuffle(groups)
    for name in groups:
        available_seats = seats_per_group
        if extra_seats > 0:
            available_seats += 1
            extra_seats -= 1
        birthday = time.get_birthdays_for(name)
        if not birthday:
            rating = ratings.get(name)
            seats_taken = 0
            if rating:
                seats_by_rating = round((available_seats * rating.positive_count) / FULL_AFTER_RATINGS)
                seats_taken = min(available_seats, seats_by_rating)
            if seats_taken == 0:
                empty_groups.append(name)
        else:
            cli.print_message('It\'s somebody\'s birthday: {}'.format(name))
            seats_taken = available_seats
        new_guests.extend(seats_taken * [name])
        seats_remaining -= seats_taken
    holidays = time.get_holidays_for(groups)
    seats_per_holiday = round(seats_remaining / len(holidays)) if holidays else 0
    for holiday in holidays:
        holiday_groups = set(holiday.groups).intersection(groups)
        cli.print_message('Today is a holiday for: {}.'.format(', '.join(holiday_groups)))
        seats_taken = round(seats_per_holiday / len(holiday_groups))
        for group in holiday_groups:
            new_guests.extend(seats_taken * [group])
        seats_remaining -= seats_taken
    for _ in range(RANDOM_GUESTS):
        if empty_groups and seats_remaining > 0:
            random_group = random.choice(empty_groups)
            new_guests.append(random_group)
            empty_groups.remove(random_group)
            seats_remaining -= 1
    random.shuffle(new_guests)
    return new_guests


def daytime():
    global guests
    global regulars
    global guest_factory
    guests = []
    regulars_today = list(filter(
        lambda regular: regular.available and not regular.days or time.weekday() in regular.days,
        regulars.values()
    ))
    guests.extend(regulars_today)
    seats = diner.diner.seats - len(guests)
    new_guests = _new_guests(seats)
    reviews.add(set(new_guests))
    for name in new_guests:
        guest = guest_factory.create(name, existing=guests)
        guests.append(guest)
    for regular in regulars_today:
        regular.reset()


def init(data):
    global regulars
    regulars = OrderedDict()
    for guest_data in data.get('regulars', []):
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

    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)


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
