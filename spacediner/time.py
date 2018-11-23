class Clock:
    TIME_WORK = 'work'
    TIME_OFF = 'off'

    def __init__(self):
        self.day = 0
        self.time = self.TIME_OFF
        self.callbacks = []

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