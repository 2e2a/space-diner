import pickle

from . import cli


class Event:
    TYPE_HOLIDAY = 'holiday'
    TYPE_BIRTHDAY = 'birthday'
    TYPE_RATS = 'rats'

    GROUP_EVENT_TYPES = [TYPE_HOLIDAY, TYPE_BIRTHDAY]
    STORAGE_EVENT_TYPES = [TYPE_RATS]

    type = None
    name = None
    day = 0
    info = None

    def init(self, data):
        self.name = data.get('event')
        self.type = data.get('type')
        self.info = data.get('info', None)
        self.day = int(data.get('day'))


    def print_message(self):
        raise NotImplementedError

class GroupEvent(Event):
    groups = None

    def init(self, data):
        super().init(data)
        self.groups = data.get('groups')

    def print_message(self):
        if self.type == self.TYPE_HOLIDAY:
            cli.print_message('Today is a holiday for: {}.'.format(', '.join(self.groups)))
        elif self.type == self.TYPE_BIRTHDAY:
            cli.print_message('Today is a birthday for: {}.'.format(', '.join(self.groups)))


class StorageEvent(Event):
    ingredients = None

    def init(self, data):
        super().init(data)
        self.ingredients = data.get('ingredients')


class Calendar:
    week = None
    cycle = 0

    TIME_WORK = 'work'
    TIME_OFF = 'off'
    day = 0
    time = TIME_OFF
    callbacks = []

    morning_greeting = None
    evening_greeting = None

    events = {}

    def tick(self):
        if self.time == self.TIME_WORK:
            self.time = self.TIME_OFF
            cli.print_message(self.evening_greeting)
        else:
            self.time = self.TIME_WORK
            self.day += 1
            cli.print_message(self.morning_greeting)
        for event in self.events.get(self.day, []):
            event.print_message()
            if event.info:
                cli.print_text(event.info)
        for time, callback in self.callbacks:
            if time == self.time:
                callback()

    @property
    def weekday(self):
        return self.week[(self.day % len(self.week) - 1)]

    @property
    def now(self):
        return '{} - {}'.format(self.day, self.weekday, self.time)

    def register_callback(self, time, callback):
        self.callbacks.append((time, callback))

    def init(self, data):
        self.week = data.get('week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.cycle = int(data.get('cycle'))
        self.morning_greeting = data.get('morning_greeting', 'A new morning...')
        self.evening_greeting = data.get('evening_greeting', 'The work\'s done...')
        for event_data in data.get('events', []):
            event_type = event_data.get('type')
            if event_type in Event.GROUP_EVENT_TYPES:
                event = GroupEvent()
            elif event_type in Event.STORAGE_EVENT_TYPES:
                event =  StorageEvent()
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


def get_rat_days():  # TODO: fix me
    global calendar
    if calendar.day in calendar.events:
        return filter(lambda event: event.type == Event.TYPE_RATS, calendar.events.get(calendar.day))
    return []


def register_callback(time, callback):
    global calendar
    calendar.register_callback(time, callback)


def init(data):
    global calendar
    calendar.init(data)


def save(file):
    global calendar
    pickle.dump(calendar, file)


def load(file):
    global calendar
    calendar = pickle.load(file)
