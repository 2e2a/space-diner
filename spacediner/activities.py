import pickle

from collections import OrderedDict

from . import cli
from . import rewards


class Activity:
    name = None
    available = False
    message = None
    rewards = None

    def init(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.message = data.get('message')
        self.rewards = rewards.init_list(data.get('rewards'))

    def can_do(self):
        return any(reward.can_apply() for reward in self.rewards)

    def do(self):
        cli.print_text(self.message)
        for reward in self.rewards:
            reward.apply()


activities = None


def available_activities():
    global activities
    return [activity.name for activity in activities.values() if activity.available and activity.can_do()]


def do(name):
    global activities
    activity = activities.get(name)
    activity.do()


def init(data):
    global activities
    activities = OrderedDict()
    for activity_data in data:
        activity = Activity()
        activity.init(activity_data)
        activities.update({activity.name: activity})


def save(file):
    global activities
    pickle.dump(activities, file)


def load(file):
    global activities
    activities = pickle.load(file)
