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
        msg = 'Your {} {}. They now include: {}'.format(
            self.name,
            'increased' if diff > 0 else 'decreased',
            ', '.join(self.learned_subskills)
        )
        cli.print_message(msg)

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


def add(skill, diff):
    global skills
    skills.get(skill).add(diff)


def init(data):
    global skills
    skills = OrderedDict()
    for skill_data in data:
        skill = Skill()
        skill.init(skill_data)
        skills.update({skill.name: skill})


def save(file):
    pass


def load(file):
    pass
