from . import cli
from . import levels
from . import time


class Reward:
    TYPE_MONEY = 'money'

    message = None
    typ = None

    def init(self, data):
        self.message = data.get('message')

    def reached(self):
        cli.print_text(self.message)
        cli.print_message('Congratulations! You have won!')

    def check(self):
        raise NotImplemented()


class MoneyGoal(Reward):
    amount = None

    def init(self, data):
        super().init(data)
        self.amount = data.get('amount')

    def reached(self):
        cli.print_message('Reached {} space dollars.'.format(self.amount))
        super().reached()

    def check(self):
        if levels.level.money >= self.amount:
            self.reached()



goals = None


def new_workday():
    pass


def after_work():
   global goals
   for goal in goals:
       goal.check()


def init(data):
    global goals
    goals = []
    for goal_data in data:
        typ = goal_data.get('type')
        goal = None
        if typ == Reward.TYPE_MONEY:
            goal = MoneyGoal()
        goal.init(goal_data)
        goals.append(goal)
    time.register_callback(time.Calendar.TIME_WORK, new_workday)
    time.register_callback(time.Calendar.TIME_OFF, after_work)
    return goals
