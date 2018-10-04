from collections import OrderedDict


class Storage:
    name = None
    ingredient_availability = {}

    def load(self, data):
        self.name = data.get('name')
        for storage_ingredient in  data.get('ingredients'):
            ingredient =  storage_ingredient.get('name')
            availablity = storage_ingredient.get('available')
            self.ingredient_availability.update({ingredient: availablity})


storages = None


def load(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.load(storage_data)
        storages.update({storage.name: storage})
