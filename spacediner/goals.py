import pickle

from . import cli
from . import levels
from . import reviews
from . import settings
from . import time

class Goal:
    TYPE_MONEY = 'money'
    TYPE_REVIEWS = 'reviews'

    text = None
    message = None
    typ = None
    is_reached = False

    def init(self, data):
        self.text = data.get('text')
        self.message = data.get('message')

    def reached(self):
        cli.print_text(self.message)
        cli.print_newline()
        cli.wait_for_input()

    def check(self):
        raise NotImplemented()

    def progress(self):
        return 0, 100


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
            return True
        return False

    def progress(self):
        return levels.level.money, self.amount


class ReviewsGoal(Goal):
    group = None
    amount = None

    def init(self, data):
        super().init(data)
        self.group = data.get('group', None)
        self.amount = data.get('amount')

    def reached(self):
        cli.print_message('Reached {} positive {} review(s).'.format(self.amount, self.group))
        super().reached()

    def check(self):
        group_rating_positive_count = reviews.group_ratings_above(self.group, 4)
        if group_rating_positive_count >= self.amount:
            if not self.is_reached:
                self.reached()
            return True
        return False

    def progress(self):
        group_rating_positive_count = reviews.group_ratings_above(self.group, 4)
        return group_rating_positive_count, self.amount


goals = None
win_message_shown = False


def get_texts():
    global goals
    return [goal.text for goal in goals]


def get_progresses():
    global goals
    progresses = []
    for goal in goals:
        progress_num, progress_of = goal.progress()
        goal_progress_prc = min(int(float(progress_num) * 10.0 / float(progress_of)), 10)
        progress_bar = '#' * goal_progress_prc + '-' * (10 - goal_progress_prc)
        if settings.text_only():
            progress_info = '{}/{} - {}'.format(progress_num, progress_of, goal.text)
        else:
            progress_info = '[{}]  {}/{} - {}'.format(progress_bar, progress_num, progress_of, goal.text)
        progresses.append(progress_info)
    return progresses


def check_goals():
    global goals
    global win_message_shown
    goals_reached = True
    for goal in goals:
        goal_reached = goal.check()
        if goal_reached:
            goal.is_reached = True
        if goals_reached and not goal_reached:
            goals_reached = False
    if goals_reached and not win_message_shown:
        win_message_shown = True
        cli.print_message('Congratulations! You have won!')
        cli.wait_for_input()
        cli.cls()
        cli.print_header()
        cli.print_text(levels.get_outro())
        cli.print_newline()
        yes = input('Exit game? (y/N) ')
        if yes in ['y', 'Y']:
            # levels.autosave_save()
            if cli.logfile:
                cli.logfile.close()
            exit()


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


def save(file):
    global goals
    global win_message_shown
    pickle.dump(goals, file)
    pickle.dump(win_message_shown, file)


def load(file):
    global goals
    global win_message_shown
    goals = pickle.load(file)
    win_message_shown = pickle.load(file)
    time.register_callback(time.Calendar.TIME_MORNING, check_goals)
    time.register_callback(time.Calendar.TIME_DAYTIME, check_goals)
    time.register_callback(time.Calendar.TIME_EVENING, check_goals)