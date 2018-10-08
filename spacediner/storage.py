from collections import OrderedDict


class Storage:
    name = None
    available = False
    available_ingredients = None

    def load(self, data):
        self.name = data.get('name')
        self.available = data.get('available')
        self.available_ingredients = OrderedDict()
        for storage_ingredient in  data.get('ingredients'):
            ingredient =  storage_ingredient.get('name')
            availability = storage_ingredient.get('available')
            self.available_ingredients.update({ingredient: availability})



storages = None


def load(data):
    global storages
    storages = OrderedDict()
    for storage_data in data:
        storage = Storage()
        storage.load(storage_data)
        storages.update({storage.name: storage})
