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
        self.review_phrase = data.get('review_phrase', 'something')

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

    def from_menu(self, wish):
        self.wish = wish
        self.text = 'I\'ll have the {} from the menu.'.format(self.wish)


class Guest:
    is_regular = False
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
    chatted = False

    taste = 2
    service = 2
    ambience = 2
    review = None

    def __init__(self, is_regular=False):
        self.is_regular = is_regular
        self.groups = []
        self.reactions = []
        self.orders = []
        self.positive_phrases = []
        self.neutral_phrases = []
        self.negative_phrases = []

    def name_with_groups(self):
        pass

    @property
    def group(self):
        return ' '.join(group.name for group in self.groups)

    @property
    def group_name(self):
        return self.group if not self.is_regular else self.name

    @property
    def review_names(self):
        names = [group.name for group in self.groups]
        if self.is_regular:
            names.append(self.name)
        return names

    @property
    def is_in_factory(self):
        global guest_factory
        return self.group in guest_factory.get_groups()

    def apply_groups(self):
        self.reactions += list(itertools.chain.from_iterable(group.reactions for group in self.groups))
        if not self.budget:
            self.budget = max([group.budget for group in self.groups if group.budget])
        self.orders += list(itertools.chain.from_iterable(group.orders for group in self.groups))
        for group in self.groups:
            self.positive_phrases += group.positive_phrases
            self.neutral_phrases += group.neutral_phrases
            self.negative_phrases += group.negative_phrases

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
        self.chatted = False
        if not self.is_regular:
            self.review = reviews.Review(self.name, self.group_name)
        else:
            regular_group_name = self.group if self.is_in_factory else None
            self.review = reviews.Review(self.name, self.group_name, regular_group_name)
        self.served = False
        self.taste = 2
        self.service = 2
        self.ambience = 2
        self.init_service()
        self.init_ambience()

    def _reaction_properties(self, filter_func):
        properties = set()
        positive_reactions = filter(filter_func, self.reactions)
        for reaction in positive_reactions:
            properties.update(reaction.properties)
        return properties

    @property
    def positive_reaction_properties(self):
        return self._reaction_properties(lambda reaction: reaction.taste > 0)

    @property
    def negative_reaction_properties(self):
        return self._reaction_properties(lambda reaction: reaction.taste <= -1)

    def select_from_menu(self):
        wish = None
        menu = food.get_menu()
        acceptable_food = []
        for menu_item in menu:
            recipe = food.get_recipe(menu_item)
            if not self.negative_reaction_properties.intersection(recipe.all_properties()):
                acceptable_food.append(menu_item)
        if acceptable_food:
            wish = random.choice(acceptable_food)
        return wish

    def take_order(self):
        if self.order:
            return self.order.text
        random.seed()
        menu_wish = self.select_from_menu()
        if menu_wish and self.orders:
            order_from_menu = random.choice([True, False])
            if order_from_menu:
                self.order = Order()
                self.order.from_menu(menu_wish)
            else:
                self.order = random.choice(self.orders)
        elif menu_wish:
            self.order = Order()
            self.order.from_menu(menu_wish)
        elif self.orders:
            self.order = random.choice(self.orders)
        return self.order.text if self.order else None

    def add_review(self):
        return self.review.generate(
            self.taste,
            self.service,
            self.ambience,
            review_phrases=(self.positive_phrases, self.neutral_phrases, self.negative_phrases),
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
                cli.print_text('{} received what they ordered ({}).'.format(self.name, self.order.wish))
            else:
                self.service -= 2
                self.review.add(2, 'order_not_met', self.order.wish)
                cli.print_message('{} did not receive what they ordered ({}).'.format(self.name, self.order.wish))
        self.taste = min(4, max(0, self.taste))
        self.review.add(1, 'taste', self.taste, print=True)
        self.add_skill_review()
        final_rating = self.add_review()
        payment = int(self.budget/5 * final_rating)
        levels.level.money += payment
        cli.print_text('{} paid {} space dollars.'.format(self.name, payment))
        return self.taste

    def has_chat_available(self):
        return not self.chatted and social.has_chats(self.name, self.group_name) and social.next_chat(self.group_name)

    def chat(self):
        self.chatted = True
        self.service += 1
        self.review.add(2, 'chatted')
        return social.greet_and_chat(self.name, self.group_name)

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
        if self.is_regular:
            self.groups = [get_group(group_name) for group_name in data.get('groups', [])]


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

    def get_available_subgroups(self):
        available_groups = get_available_groups()
        return [group for group in self.groups if all(subgroup in available_groups for subgroup in group)]

    def get_groups(self):
        return [' '.join(group) for group in self.get_available_subgroups()]

    def create_guest(self, name, existing=None):
        guest = Guest()
        groups = [get_group(group_name) for group_name in name.split(' ')]
        guest.name = self._guest_name(groups, existing)
        guest.groups = groups
        guest.apply_groups()
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

def is_group_available(group):
    global guest_groups
    subgroups = group.split(' ')
    available_groups = get_available_groups()
    return all(subgroup in available_groups for subgroup in subgroups)

def get_group(name):
    global guest_groups
    return guest_groups.get(name)

def get_guests():
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
    guests_with_chats = list(filter(lambda guest: guest.has_chat_available(), guests))
    return [guest.name for guest in guests_with_chats]


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
        guest = get_group(name)
    if guest:
        guest.available = True


FULL_AFTER_RATINGS = 10
RANDOM_GUESTS = 2


def _new_guests(seats):
    global guest_factory
    # TODO: numbers are not completely right: e.g., 4 colonists and 2 tourists when 6 seats are available?
    wait_for_input = False
    seats_remaining = seats
    new_guests = []
    groups = guest_factory.get_groups()
    if seats_remaining < len(groups):
        groups = random.sample(groups, seats_remaining)
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
                seats_by_rating = round((available_seats * rating.get_ratings_above(3)) / FULL_AFTER_RATINGS)
                seats_taken = min(available_seats, seats_by_rating)
            if seats_taken == 0:
                empty_groups.append(name)
        else:
            cli.print_message('It\'s somebody\'s birthday: {}'.format(name))
            wait_for_input = True
            seats_taken = available_seats
        new_guests.extend(seats_taken * [name])
        seats_remaining -= seats_taken
    holidays = time.get_holidays_for(groups)
    seats_per_holiday = round(seats_remaining / len(holidays)) if holidays else 0
    for holiday in holidays:
        holiday_groups = set(holiday.groups).intersection(groups)
        seats_per_group = round(seats_per_holiday / len(holiday_groups))
        for group in holiday_groups:
            seats_per_group = min(seats_per_group, seats_remaining)
            new_guests.extend(seats_per_group * [group])
            seats_remaining -= seats_per_group
    for _ in range(RANDOM_GUESTS):
        if empty_groups and seats_remaining > 0:
            random_group = random.choice(empty_groups)
            new_guests.append(random_group)
            empty_groups.remove(random_group)
            seats_remaining -= 1
    random.shuffle(new_guests)
    if wait_for_input:
        cli.wait_for_input()
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
    for name in new_guests:
        guest = guest_factory.create_guest(name, existing=guests)
        reviews.add(guest.group_name, guest.review_names)
        guests.append(guest)
    for regular in regulars_today:
        regular.reset()


def init(data):
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

    global regulars
    regulars = OrderedDict()
    for guest_data in data.get('regulars', []):
        guest = Guest(is_regular=True)
        guest.init(guest_data)
        guest.apply_groups()
        guest.reset()
        regulars.update({guest.name: guest})

    reviews.init()
    for regular in regulars.values():
        reviews.add(regular.name, regular.review_names)

    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)


def save(file):
    global guests
    global regulars
    global guest_groups
    global guest_factory
    global name_factories
    pickle.dump(guests, file)
    pickle.dump(regulars, file)
    pickle.dump(guest_groups, file)
    pickle.dump(guest_factory, file)
    pickle.dump(name_factories, file)


def load(file):
    global guests
    global regulars
    global guest_groups
    global guest_factory
    global name_factories
    guests = pickle.load(file)
    regulars = pickle.load(file)
    guest_groups = pickle.load(file)
    guest_factory = pickle.load(file)
    name_factories = pickle.load(file)
    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)

