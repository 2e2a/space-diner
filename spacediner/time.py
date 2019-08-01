import pickle


class Clock:
    TIME_WORK = 'work'
    TIME_OFF = 'off'
    morning_greeting = None
    evening_greeting = None

    def __init__(self):
        self.day = 0
        self.time = self.TIME_OFF
        self.callbacks = []

    def get_greeting(self):
        if self.time == self.TIME_WORK:
            return self.morning_greeting
        else:
            return self.evening_greeting

    def tick(self):
        if self.time == self.TIME_WORK:
            self.time = self.TIME_OFF
        else:
            self.day += 1
            self.time = self.TIME_WORK
        for time, callback in self.callbacks:
            if time == self.time:
                callback()

    def now(self):
        return '{} - {}'.format(self.day, self.time)

    def register_callback(self, time, callback):
        self.callbacks.append((time, callback))

    def init(self, data):
        if data:
            self.morning_greeting = data.get('morning_greeting')
            self.evening_greeting = data.get('evening_greeting')
        else:
            self.morning_greeting = 'A new morning...'
            self.evening_greeting = 'The work\'s done...'


clock = Clock()


def tick():
    global clock
    clock.tick()


def now():
    global clock
    return clock.now()


def register_callback(time, callback):
    global clock
    clock.register_callback(time, callback)


def init(data):
    global clock
    clock.init(data)


def save(file):
    global clock
    pickle.dump(clock, file)


def load(file):
    global clock
    clock = pickle.load(file)
