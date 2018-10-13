from collections import OrderedDict

from . import storage


class Device:
    name = None
    preparation_verb = None
    preparation_participle = None
    available = False

    def __str__(self):
        return '{} ({})'.format(self.name, self.preparation_verb)

    def load(self, data):
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


def get_device(name):
    global devices
    return devices.get(name)


def load(data):
    global devices
    devices = OrderedDict()
    for device_data in data:
        device = Device()
        device.load(device_data)
        devices.update({device.name: device})

