import pickle
from collections import OrderedDict

from . import time


ratings = None
reviews = None
likes = None


def get_ratings():
    global ratings
    return ratings


def get_reviews():
    global reviews
    return reviews


def get_likes():
    global likes
    return likes


def add_rating(name, taste):
    global ratings
    rating, count = ratings.get(name)
    if not rating:
        ratings.update({name: (taste, 1)})
    else:
        rating = (count*rating + taste)/(count + 1)
        ratings.update({name: (rating, count + 1)})


def add_review(review):
    global reviews
    reviews.append(review)


def add_likes(name, new_likes):
    global likes
    guest_likes, guest_dislikes = likes.get(name)
    guest_likes.extend(new_likes)
    likes.update({name: (guest_likes, guest_dislikes)})


def add_dislikes(name, new_dislikes):
    global likes
    guest_likes, guest_dislikes = likes.get(name)
    guest_likes.extend(new_dislikes)
    likes.update({name: (guest_likes, guest_dislikes)})


def new_workday():
    global reviews
    reviews = []



def init(guests):
    # TODO: consider group/guest availability
    global ratings
    global reviews
    global likes
    ratings = OrderedDict()
    likes = OrderedDict()
    reviews = []
    for guest in guests:
        ratings.update({guest: (None, 0)})
        likes.update({guest: ([], [])})
    time.register_callback(time.Clock.TIME_WORK, new_workday)


def save(file):
    global ratings
    global reviews
    global likes
    pickle.dump(skills, file)
    pickle.dump(reviews, file)
    pickle.dump(likes, file)


def load(file):
    global ratings
    global reviews
    global likes
    pickle.load(skills, file)
    pickle.load(reviews, file)
    pickle.load(likes, file)


def debug():
    global skills
    for skill in skills.values():
        skill.debug()
