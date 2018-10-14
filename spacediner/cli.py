from . import actions
from . import food
from . import guests
from . import kitchen
from . import levels
from . import storage


class Mode:
    commands = []
    prompt = None
    names = {}

    def print_info(self):
        raise NotImplemented()

    def print_help(self):
        print('Help:')
        raise NotImplemented()

    def _match_arg(self, arg_type, arg):
        if isinstance(arg_type, list):
            return arg in arg_type
        if isinstance(arg_type, str):
            return isinstance(arg, str)
        if isinstance(arg_type, int):
            return isinstance(arg, int)

    def _get_command(self, input):
        for num, cmd in enumerate(self.commands):
            if len(cmd) == len(input):
                arg_type_match = True
                for arg_type, arg in zip(cmd, input):
                    if not self._match_arg(arg_type, arg):
                        arg_type_match = False
                        break
                if arg_type_match:
                    return num + 1
        return None

    def exec(self, cmd, input):
        raise  NotImplemented()

    def parse(self, input):
        if input:
            input_list = input.split()
            cmd = self._get_command(input_list)
            if cmd:
                return self.exec(cmd, input_list)
        self.print_help()
        return self

    def name_for_command(self, name):
        cmd_name = name.replace(' ', '_').lower()
        self.names.update({cmd_name: name})
        return cmd_name

    def original_name(self, cmd_name):
        return self.names.get(cmd_name)


class ActionMode(Mode):
    CMD_COOKING = 1
    CMD_SERVICE = 2
    CMD_SHOPPING = 3
    CMD_EXIT = 4
    commands = [
        (['cooking'],),
        (['service'],),
        (['shopping'],),
        (['exit'],),
    ]

    def print_info(self):
        print('Level: {}'.format(levels.level.name))

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == self.CMD_COOKING:
            return CookingMode()
        if cmd == self.CMD_SERVICE:
            return ServiceMode()
        if cmd == self.CMD_SHOPPING:
            return ShoppingMode()
        if cmd == self.CMD_EXIT:
            exit()


class ServiceMode(Mode):
    CMD_SERVE = 1
    CMD_DONE = 2
    commands = [
        (['serve'], [], ['to'], []),
        (['done'], ),
    ]
    prompt = 'service'

    def __init__(self):
        self.update_commands()

    def update_commands(self):
        cooked_food = [self.name_for_command(f) for f in food.cooked.keys()]
        available_guests = [self.name_for_command(g) for g in guests.available_guests()]
        self.commands[0] = (['serve'], cooked_food, ['to'], available_guests)

    def print_info(self):
        print('Food:')
        for dish in food.cooked.values():
            print(dish)
        print('Guests:')
        for guest in guests.available_guests():
            print(guest)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == 1:
            food = self.original_name(input[1])
            guest = self.original_name(input[3])
            action = actions.Serve(food, guest)
            action.perform()
            return self
        if cmd == 2:
            return ActionMode()


class CookingMode(Mode):
    CMD_COOK = 1
    CMD_PLATE = 2
    commands = [
        (['cook'], [], ),
        (['plate'], ),
        (['abort'], ),
    ]
    prompt = 'cooking'
    action = None
    available_ingredients = None
    available_devices = None
    prepared_components = []

    def __init__(self):
        self.available_ingredients = storage.available_ingredients()
        self.available_devices = kitchen.available_devices()
        self.update_commands()
        self.action = actions.Cook()

    def update_commands(self):
        ingredients = []
        for ingredient, available in self.available_ingredients.items():
            if available: ingredients.append(self.name_for_command(ingredient))
        preparations = [d.preparation_verb for d in self.available_devices.values()]
        self.commands[0] = (preparations, ingredients)

    def print_info(self):
        print('Available Ingredients:')
        print(self.available_ingredients)
        print('Kitchen:')
        print(', '.join(['{} for {}ing'.format(d.name, d.preparation_verb) for d in self.available_devices.values()]))
        print('Prepared:')
        print(self.prepared_components)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def _get_device(self, preparation_command):
        for device in self.available_devices.values():
            if device.preparation_verb == preparation_command:
                return device
        return None

    def exec(self, cmd, input):
        if cmd == self.CMD_COOK:
            preparation_command = input[0]
            device = self._get_device(preparation_command)
            ingredient = self.original_name(input[1])
            self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient) - 1})
            self.action.add_ingredients([(ingredient, device.name)])
            self.prepared_components.append('{} {}'.format(device.preparation_participle, ingredient))
            self.update_commands()
            return self
        if cmd == self.CMD_PLATE:
            self.action.perform()
            return ActionMode()
        if cmd == self.CMD_ABORT:
            return ActionMode()


class ShoppingMode(Mode):
    CMD_BUY_STORAGE = 1
    CMD_ABORT = 2
    commands = [
        (['buy'], ['storage'], []),
        (['abort'], ),
    ]
    prompt = 'shopping'
    storages_for_sale = None

    def __init__(self):
        self.storages_for_sale = storage.for_sale()
        self.update_commands()

    def update_commands(self):
        available_storages = []
        for storage in self.storages_for_sale.values():
            if storage.cost < levels.level.money:
                available_storages.append(self.name_for_command(storage.name))
        self.commands[0] = (['buy'], ['storage'], available_storages)


    def print_info(self):
        print('Money: {} space dollars'.format(levels.level.money))
        print('Storages for sale:')
        print([(s.name, s.cost) for s in self.storages_for_sale.values()])


    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == self.CMD_BUY_STORAGE:
            storage = self.original_name(input[2])
            action = actions.BuyStorage(storage)
            action.perform()
            self.storages_for_sale.pop(storage)
            self.update_commands()
            return self
        if cmd == self.CMD_ABORT:
            return ActionMode()


mode = None


def run():
    global mode
    mode = ActionMode()
    while True:
        mode.print_info()
        prompt = '({}) '.format(mode.prompt) if mode.prompt else ''
        cmd = input('space diner {}>> '.format(prompt))
        mode = mode.parse(cmd)

