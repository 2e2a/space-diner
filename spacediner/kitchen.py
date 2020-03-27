import pickle

from collections import OrderedDict


class Device:
    name = None
    available = False
    preparation = None
    command = None
    result = None
    properties = None

    def __str__(self):
        return '{} ({})'.format(self.name, ', '.join())

    def init(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.preparation = data.get('preparation')
        self.command = data.get('command')
        self.result = data.get('result')
        self.properties = data.get('properties')


devices = None


def available_devices():
    global devices
    available_devices = {}
    for device in devices.values():
        if device.available:
            available_devices.update({device.name: device})
    return available_devices


def available_preparation_results():
    global devices
    return [device.result for device in devices.values() if device.available ]


def preparation_device(preparation_result):
    global devices
    for device in devices.values():
        if device.available and device.result == preparation_result:
            return device
    return  None


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

