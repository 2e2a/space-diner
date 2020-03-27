import pickle
from collections import OrderedDict

from . import time


class Rating:
    name = None
    count = 0
    positive_count = 0
    aggregate = 0
    taste = 0
    service = 0
    ambience = 0


    TASTE_MULTIPLIER = 3

    def __init__(self, name):
        self.name = name

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


ratings = None
reviews = None
likes = None


def get_ratings():
    global ratings
    return ratings


def get_rating(name):
    return get_ratings().get(name)


def get_reviews():
    global reviews
    return reviews


def get_likes():
    global likes
    return likes


def add_rating(name, taste, service, ambience):
    global ratings
    return ratings.get(name).add(taste + 1, service + 1, ambience + 1)


def add_review(review):
    global reviews
    reviews.append(review)


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


def add(guests):
    global ratings
    global reviews
    global likes
    for guest in guests:
        if guest not in ratings:
            ratings.update({guest: Rating(guest)})
        if guest not in likes:
            likes.update({guest: (set(), set())})


def init(guests):
    # TODO: consider group/guest availability
    global ratings
    global reviews
    global likes
    ratings = OrderedDict()
    likes = OrderedDict()
    reviews = []
    add(guests)
    time.register_callback(time.Calendar.TIME_DAYTIME, daytime)


def save(file):
    global ratings
    global reviews
    global likes
    pickle.dump(ratings, file)
    pickle.dump(reviews, file)
    pickle.dump(likes, file)


def load(file):
    global ratings
    global reviews
    global likes
    pickle.load(ratings, file)
    pickle.load(reviews, file)
    pickle.load(likes, file)
