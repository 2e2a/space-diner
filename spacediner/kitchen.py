import pickle

from collections import OrderedDict

from . import generic


class Device(generic.Thing):
    name = None
    preparation_verb = None
    preparation_participle = None
    available = False

    def __str__(self):
        return '{} ({})'.format(self.name, self.preparation_verb)

    def init(self, data):
        self.name = data.get('name')
        self.preparation_verb = data.get('preparation')[0]
        self.preparation_participle = data.get('preparation')[1]
        self.available = data.get('available')


devices = None


def available_devices():
    global devices
    available_devices = {}
    for device in devices.values():
        if device.available:
            available_devices.update({device.name: device})
    return available_devices


def available_preparation_participles():
    global devices
    return [device.preparation_participle for device in devices.values() if device.available ]


def get_device(name):
    global devices
    return devices.get(name)


def init(data):
    global devices
    devices = OrderedDict()
    for device_data in data:
        device = Device()
        device.init(device_data)
        devices.update({device.name: device})


def save(file):
    global devices
    pickle.dump(devices, file)


def load(file):
    global devices
    devices = pickle.load(file)


def debug():
    global devices
    for device in devices.values():
        device.debug()

