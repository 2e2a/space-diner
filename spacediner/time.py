import pickle

from . import cli


class Event:
    name = None
    day = 0
    info = None
    groups = None

    def init(self, data):
        self.name = data.get('holiday')
        self.info = data.get('info')
        self.day = int(data.get('day'))
        self.groups = data.get('groups')


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
            cli.print_message('Today is "{}" for: {}.'.format(event.name, ', '.join(event.groups)))
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
        for holiday_data in data.get('holidays', []):
            holiday = Event()
            holiday.init(holiday_data)
            if holiday.day in self.events:
                self.events.get(holiday.day).append(holiday)
            else:
                self.events.update({holiday.day: [holiday]})


calendar = Calendar()


def tick():
    global calendar
    calendar.tick()


def now():
    global calendar
    return calendar.now


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
