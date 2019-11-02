import pickle


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

    def get_greeting(self):
        if self.time == self.TIME_WORK:
            return self.morning_greeting
        else:
            return self.evening_greeting

    def tick(self):
        if self.time == self.TIME_WORK:
            self.time = self.TIME_OFF
        else:
            self.time = self.TIME_WORK
            self.day += 1
            self.weekday
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
