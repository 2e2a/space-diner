import pickle

from collections import OrderedDict

from . import cli

# TODO: cooking skills influence rating (like ambience and service) and reviews ("It was seasoned perfectly.")
# TODO: optionally define texts for each skill level which is shown when the skill level changes ("Your seasoning skill is now medium.")

MAX_SKILL_LEVEL = 5


class Skill:
    TYPE_COOKING = 'cooking'
    TYPE_SERVICE = 'service'
    TYPE_AMBIENCE = 'ambience'
    TYPE_OTHER = 'other'
    TYPES = [TYPE_COOKING, TYPE_SERVICE, TYPE_AMBIENCE, TYPE_OTHER]

    typ = None
    name = None
    level = 0
    subskills = [None] * MAX_SKILL_LEVEL

    @property
    def learned_subskills(self):
        return self.subskills[:self.level]

    def is_learned(self, subskill):
        return self.level > self.subskills.index(subskill)

    def add(self, diff):
        self.level += diff
        self.level = max(min(self.level, MAX_SKILL_LEVEL), 0)
        msg = 'Your {} {}. They now include: {}'.format(
            self.name,
            'increased' if diff > 0 else 'decreased',
            ', '.join(self.learned_subskills)
        )
        cli.print_message(msg)
        cli.print_newline()

    def init(self, data):
        self.typ = data.get('type')
        assert self.typ in self.TYPES
        self.name = data.get('name')
        self.level = data.get('level', 0)
        self.subskills = data.get('subskills')


skills = None


def get(name):
    global skills
    return skills.get(name)


def get_levels():
    global skills
    return [(skill.name, skill.level) for skill in skills.values()]


def get_skills():
    global skills
    return skills.values()


def get_subskills(name):
    skill = get(name)
    return skill.learned_subskills


def learned():
    global skills
    return [skill.name for skill in skills.values() if skill.level > 0]


def can_add(skill, diff):
    skill = get(skill)
    if diff > 0 and skill.level < MAX_SKILL_LEVEL:
        return True
    if diff < 0 and skill.level > 0:
        return True
    return False

def add(skill, diff):
    get(skill).add(diff)


def init(data):
    global skills
    skills = OrderedDict()
    for skill_data in data:
        skill = Skill()
        skill.init(skill_data)
        skills.update({skill.name: skill})


def save(file):
    global skills
    pickle.dump(skills, file)


def load(file):
    global skills
    skills = pickle.load(file)
