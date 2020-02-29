import pickle

from collections import OrderedDict

# TODO: cooking skills influence rating (like ambience and service) and reviews ("It was seasoned perfectly.")
# TODO: define skills independently from activities
# TODO: optionally define texts for each skill level which is shown when the skill level changes ("Your seasoning skill is now medium.")

SKILLS = [
    'seasoning',
    'knife'
]


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
        value = data.get(skill) if data else 1.0
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
