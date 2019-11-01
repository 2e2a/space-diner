import pickle


class Diner:
    name = None
    seats = 0

    def init(self, data):
        self.name = data.get('name')
        self.seats = data.get('seats')


diner = None


def init(data):
    global diner
    diner = Diner()
    diner.init(data)


def save(file):
    global diner
    pickle.dump(diner, file)


def load(file):
    global diner
    diner = pickle.load(file)
