import random

from . import cli


class Event:
    TYPE_HOLIDAY = 'holiday'
    TYPE_BIRTHDAY = 'birthday'
    TYPE_INGREDIENTS_LOSE = 'lose ingredients'
    TYPE_INGREDIENTS_WIN = 'win ingredients'

    GROUP_EVENT_TYPES = [TYPE_HOLIDAY, TYPE_BIRTHDAY]
    STORAGE_EVENT_TYPES = [TYPE_INGREDIENTS_LOSE, TYPE_INGREDIENTS_WIN]

    type = None
    day = 0
    info = None

    def __init__(self, type=None):
        self.type = type

    def init(self, data):
        self.info = data.get('info', None)
        if 'day' in data:
            self.day = int(data.get('day'))
        else:
            day_range = data.get('days').split('-')
            random.seed()
            self.day = random.randint(int(day_range[0]), int(day_range[1]))


class GroupEvent(Event):
    name = None
    groups = None

    def init(self, data):
        super().init(data)
        self.name = data.get('name')
        self.groups = data.get('groups')


class StorageEvent(Event):
    ingredients = None

    def init(self, data):
        super().init(data)
        self.ingredients = {}
        for ingredient_data in data.get('ingredients'):
            self.ingredients.update({ingredient_data.get('name'): ingredient_data.get('amount')})


class Calendar:
    week = None
    cycle = 0

    TIME_MORNING = 'morning'
    TIME_DAYTIME = 'daytime'
    TIME_EVENING = 'evening'
    day = 1
    time = TIME_MORNING
    callbacks = []

    daily_greeting = None

    events = {}

    def tick(self):
        if self.time == self.TIME_MORNING:
            self.time = self.TIME_DAYTIME
        elif self.time == self.TIME_DAYTIME:
            self.time = self.TIME_EVENING
        else:
            self.time = self.TIME_MORNING
            self.day += 1
            cli.print_text(self.daily_greeting)
            cli.print_newline()
            for event in self.events.get(self.day, []):
                if event.info:
                    cli.print_text(event.info)
                    if event.type == Event.TYPE_HOLIDAY:
                        cli.print_message('Today is "{}", a holiday for: {}.'.format(event.name, ', '.join(event.groups)))
            cli.wait_for_input()
        for time, callback in self.callbacks:
            if time == self.time:
                callback()

    @property
    def weekday(self):
        return self.week[(self.day % len(self.week) - 1)]

    @property
    def is_week_start(self):
        return (self.day % len(self.week) - 1) == 0

    @property
    def is_first_day(self):
        return self.day == 1 or (self.day == 2 and self.time == self.TIME_MORNING)

    @property
    def now(self):
        return 'day {}, {}, {}'.format(self.day, self.weekday, self.time)

    def register_callback(self, time, callback):
        self.callbacks.append((time, callback))

    def init(self, data):
        self.week = data.get('week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.cycle = int(data.get('cycle'))
        self.daily_greeting = data.get('daily_greeting', 'A new morning...')
        for event_data in data.get('events', []):
            event_type = event_data.get('event')
            if event_type in Event.GROUP_EVENT_TYPES:
                event = GroupEvent(event_type)
            elif event_type in Event.STORAGE_EVENT_TYPES:
                event = StorageEvent(event_type)
            else:
                raise AssertionError('Unknown event type: {}'.format(event_type))
            event.init(event_data)
            if event.day in self.events:
                self.events.get(event.day).append(event)
            else:
                self.events.update({event.day: [event]})


calendar = Calendar()


def tick():
    global calendar
    calendar.tick()


def now():
    global calendar
    return calendar.now


def weekday():
    global calendar
    return calendar.weekday


def get_holidays():
    global calendar
    if calendar.day in calendar.events:
        return list(filter(lambda event: event.type == Event.TYPE_HOLIDAY, calendar.events.get(calendar.day)))
    return []


def get_holidays_for(names):
    global calendar
    if not isinstance(names, list):
        names = [names]
    if calendar.day in calendar.events:
        return list(filter(
            lambda event: event.type == Event.TYPE_HOLIDAY and set(event.groups).intersection(names),
            calendar.events.get(calendar.day)
        ))
    return []


def get_birthdays():
    global calendar
    if calendar.day in calendar.events:
        return list(filter(lambda event: event.type == Event.TYPE_BIRTHDAY, calendar.events.get(calendar.day)))
    return []


def get_birthdays_for(names):
    global calendar
    if not isinstance(names, list):
        names = [names]
    if calendar.day in calendar.events:
        return list(filter(
            lambda event: event.type == Event.TYPE_BIRTHDAY and set(event.groups).intersection(names),
            calendar.events.get(calendar.day)
        ))
    return []


def get_ingredients_lost():
    global calendar
    ingredients = {}
    if calendar.day in calendar.events:
        events = filter(lambda event: event.type == Event.TYPE_INGREDIENTS_LOSE, calendar.events.get(calendar.day))
        for event in events:
            ingredients.update(event.ingredients)
    return ingredients


def get_ingredients_won():
    global calendar
    ingredients = {}
    if calendar.day in calendar.events:
        events = filter(lambda event: event.type == Event.TYPE_INGREDIENTS_WIN, calendar.events.get(calendar.day))
        for event in events:
            ingredients.update(event.ingredients)
    return ingredients


def register_callback(time, callback):
    global calendar
    calendar.register_callback(time, callback)


def init(data):
    global calendar
    calendar.init(data)


def save(file):
    pass


def load(file):
    pass
