import pickle

from collections import OrderedDict


SKILLS = ['proficiency']


skills = None


def get():
    global skills
    return skills


def add(skill, diff):
    value = skills.get(skill)
    skills.update({skill: value + diff})


def init(data):
    global skills
    skills = OrderedDict()
    for skill in SKILLS:
        value = data.get(skill, 0.0)
        skills.update({skill: value})


def save(file):
    global slice
    pickle.dump(skills, file)


def load(file):
    global skills
    skills = pickle.load(file)


def debug():
    global skills
    for skill in skills.values():
        skill.debug()
