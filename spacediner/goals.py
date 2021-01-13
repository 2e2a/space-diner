from . import cli
from . import levels
from . import time
from . import reviews


class Goal:
    TYPE_MONEY = 'money'
    TYPE_REVIEWS = 'reviews'

    message = None
    typ = None

    def init(self, data):
        self.message = data.get('message')

    def reached(self):
        cli.print_text(self.message)
        cli.print_newline()
        cli.print_message('Congratulations! You have won!')

    def check(self):
        raise NotImplemented()


class MoneyGoal(Goal):
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


class ReviewsGoal(Goal):
    group = None
    amount = None

    def init(self, data):
        super().init(data)
        self.group = data.get('group', None)
        self.amount = data.get('amount')

    def reached(self):
        cli.print_message('Reached {} positive {} reviews.'.format(self.amount, self.group))
        super().reached()
        input('{} '.format('<press ENTER to continue>'))

    def check(self):
        import pdb;pdb.set_trace()
        group_rating_positive_count = reviews.group_rating_positive_count(self.group)
        if group_rating_positive_count >= self.amount:
            self.reached()


goals = None


def check_goals():
   global goals
   for goal in goals:
       goal.check()


def init(data):
    global goals
    goals = []
    for goal_data in data:
        typ = goal_data.get('type')
        goal = None
        if typ == Goal.TYPE_MONEY:
            goal = MoneyGoal()
        elif typ == Goal.TYPE_REVIEWS:
            goal = ReviewsGoal()
        goal.init(goal_data)
        goals.append(goal)
    time.register_callback(time.Calendar.TIME_MORNING, check_goals)
    time.register_callback(time.Calendar.TIME_DAYTIME, check_goals)
    time.register_callback(time.Calendar.TIME_EVENING, check_goals)
    return goals
