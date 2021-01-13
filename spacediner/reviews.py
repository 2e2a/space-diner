import random
from collections import OrderedDict

from . import cli
from . import diner
from . import time


class Rating:
    name = None
    groups = None
    count = 0
    positive_count = 0
    aggregate = 0
    taste = 0
    service = 0
    ambience = 0

    TASTE_MULTIPLIER = 3

    def __init__(self, name, groups):
        self.name = name
        self.groups = groups

    def add(self, taste, service, ambience):
        self.taste = (self.count * self.taste + taste) / (self.count + 1)
        self.service = (self.count * self.service + service) / (self.count + 1)
        self.ambience = (self.count * self.ambience + ambience) / (self.count + 1)
        aggregate = (self.TASTE_MULTIPLIER * taste + service + ambience) / (self.TASTE_MULTIPLIER + 2)
        self.aggregate = round((self.count * self.aggregate + aggregate) / (self.count + 1))
        self.count += 1
        if self.aggregate > 3:
            self.positive_count += 1
        return aggregate


class Review:

    name = None
    group_name = None

    first_choices = None
    second_choices = None

    scale = ['very bad', 'bad', 'ok', 'good', 'very good']
    like = 'I liked {}.'
    dislike = 'I did not like {}.'
    taste = 'The taste was {}.'
    service = 'The service was {}.'
    ambience = 'The ambience was {}.'
    decoration = 'The interior design was nice, especially the {}.'
    order_not_met = 'I did not get what I ordered ({}).'
    no_food = 'I did not get any food.'
    chatted = 'I had a nice chat with {}.'
    diner_clean = 'Very clean diner.'
    diner_dirty = 'Very dirty diner.'
    skill = 'I was impressed by the chef\'s {}, especially {}.'

    def __init__(self, name, group_name):
        self.name = name
        self.group_name = group_name
        self.first_choices = []
        self.second_choices = []
        self.chatted = self.chatted.format(diner.diner.chef)

    def get(self, name, *args):
        if len(args) > 0 and isinstance(args[0], int):
            message = getattr(self, name).format(self.scale[args[0]])
        else:
            message = getattr(self, name).format(*args)
        return message

    def add(self, prio, name, *args, **kwargs):
        choices = self.first_choices if prio == 1 else self.second_choices
        message = self.get(name, *args)
        choices.append(message)
        if kwargs.get('print', False):
            cli.print_dialog(self.name, message)

    def add_message(self, prio, message):
        choices = self.first_choices if prio == 1 else self.second_choices
        choices.append(message)

    def generate(self, taste, service, ambience, positive_phrases, neutral_phrases, negative_phrases):
        global reviews
        self.add(2, 'ambience', ambience)
        self.add(2, 'service', service)
        aggregate_rating = add_rating(self.group_name, taste, service, ambience)
        message = ''
        random.seed()
        if self.group_name != self.name:
            message += '{} ({}):'.format(self.name, self.group_name)
        else:
            message += '{}:'.format(self.name)
        if negative_phrases and aggregate_rating <= 2:
            message += ' ' + random.choice(negative_phrases)
        elif positive_phrases and aggregate_rating >= 4:
            message += ' ' + random.choice(positive_phrases)
        elif neutral_phrases:
            message += ' ' + random.choice(neutral_phrases)
        if self.first_choices:
            message += ' ' + random.choice(self.first_choices)
        if self.second_choices:
            message += ' ' + random.choice(self.second_choices)
        message += ' (Rating: {})'.format(round(aggregate_rating))
        self.message = message
        reviews.append(self)
        return aggregate_rating


ratings = None
reviews = None
likes = None


def get_ratings():
    global ratings
    return ratings


def get_rating(name):
    return get_ratings().get(name)


def group_rating_positive_count(group):
    positive_count = 0
    ratings = get_ratings()
    for rating in ratings.values():
        if group in rating.groups:
            positive_count += rating.positive_count
    return positive_count


def get_reviews():
    global reviews
    return [review.message for review in reviews]


def get_likes():
    global likes
    return likes


def add_rating(name, taste, service, ambience):
    global ratings
    return ratings.get(name).add(taste + 1, service + 1, ambience + 1)


def add_likes(name, new_likes):
    global likes
    guest_likes, guest_dislikes = likes.get(name)
    guest_likes.add(' '.join(new_likes))
    likes.update({name: (guest_likes, guest_dislikes)})


def add_dislikes(name, new_dislikes):
    global likes
    guest_likes, guest_dislikes = likes.get(name)
    guest_dislikes.add(' '.join(new_dislikes))
    likes.update({name: (guest_likes, guest_dislikes)})


def daytime():
    global reviews
    reviews = []


def add(guest, groups):
    global ratings
    global reviews
    global likes
    if guest not in ratings:
        ratings.update({guest: Rating(guest, groups)})
    if guest not in likes:
        likes.update({guest: (set(), set())})


def init():
    # TODO: consider group/guest availability
    global ratings
    global reviews
    global likes
    ratings = OrderedDict()
    likes = OrderedDict()
    reviews = []
    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)


def save(file):
    pass


def load(file):
    pass
