from collections import OrderedDict


class Storage:
    name = None

    def load(self, data):
        self.name = data.get('name')
        print(self.name)

storages = None


def load(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.load(storage_data)
        storages.update({storage.name: storage})
