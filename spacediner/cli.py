import readline

from . import actions
from . import food
from . import guests
from . import kitchen
from . import levels
from . import storage


def print_title(str):
    print(str)
    print('-'*(len(str)))


def print_list(list):
    if list:
        for e in list:
            print('- {}'.format(e))
    else:
        print('-')
    print('')


def print_value(key, *values):
    value = ' '.join([str(v) for v in values])
    print('{}: {}'.format(key, value))


class CommandCompleter:
    commands = None
    matches = []

    def __init__(self, commands):
        self.commands = commands
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

    def _get_completed_args(self):
        buffer = readline.get_line_buffer()
        if not buffer:
            return []
        args = buffer.split()
        if buffer.endswith(' '):
            return args
        return args[:-1]

    def _matching_cmds(self, args):
        commands = []
        for cmd in self.commands:
            cmd_match = True
            for cmd_args, arg in zip(cmd, args):
                if not arg in cmd_args:
                    cmd_match = False
                    break
            if cmd_match:
                commands.append(cmd)
        return commands

    def complete(self, text, state):
        if state == 0:
            commands = []
            args = self._get_completed_args()
            matching_cmds = self._matching_cmds(args)
            for cmd in matching_cmds: commands.extend(cmd[len(args)])
            if text:
                self.matches = [cmd for cmd in commands if cmd.startswith(text)]
            else:
                self.matches =  commands
        try:
            return self.matches[state] + ' '
        except IndexError:
            return None


class Mode:
    commands = None
    prompt = None
    names = {}
    completer = None

    def __init__(self):
        self.update_commands()

    def update_commands(self):
        self.completer = CommandCompleter(self.commands)

    def print_info(self):
        raise NotImplemented()

    def print_help(self):
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
        return None

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
        print_value('Level', levels.level.name)
        print_value('Money', levels.level.money, 'space dollars')
        print('')

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

    def update_commands(self):
        cooked_food = [self.name_for_command(f) for f in food.cooked.keys()]
        available_guests = [self.name_for_command(g) for g in guests.available_guests()]
        self.commands[0] = (['serve'], cooked_food, ['to'], available_guests)
        super().update_commands()

    def print_info(self):
        print_title('Food:')
        print_list(food.cooked.values())
        print_title('Guests:')
        print_list(guests.available_guests())

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
    CMD_ABORT = 3
    CMD_DONE = 4
    commands = [
        (['cook'], [], ),
        (['plate'], ),
        (['abort'], ),
        (['done'], ),
    ]
    prompt = 'cooking'
    action = None
    available_ingredients = None
    available_devices = None
    prepared_components = None
    plated_dished = []

    def __init__(self):
        self.prepared_components = []
        self.available_ingredients = storage.available_ingredients()
        self.available_devices = kitchen.available_devices()
        self.action = actions.Cook()
        super().__init__()

    def update_commands(self):
        ingredients = []
        for ingredient, available in self.available_ingredients.items():
            if available: ingredients.append(self.name_for_command(ingredient))
        preparations = [d.preparation_verb for d in self.available_devices.values()]
        self.commands[0] = (preparations, ingredients)
        super().update_commands()

    def print_info(self):
        print_title('Available Ingredients:')
        print_list(['{} {}s'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Kitchen:')
        print_list(['{} for {}ing'.format(d.name, d.preparation_verb) for d in self.available_devices.values()])
        print_title('Prepared:')
        print_list(self.prepared_components)
        print_title('Plated:')
        print_list(list(food.cooked.keys()))

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
            self.action = actions.Cook()
            self.prepared_components = []
            return self
        if cmd == self.CMD_ABORT:
            self.action = actions.Cook()
            self.prepared_components = []
            return self
        if cmd == self.CMD_DONE:
            return ActionMode()


class ShoppingMode(Mode):
    CMD_BUY_STORAGE = 1
    CMD_DONE = 2
    commands = [
        (['buy'], ['storage'], []),
        (['done'], ),
    ]
    prompt = 'shopping'
    storages_for_sale = None

    def __init__(self):
        self.storages_for_sale = storage.for_sale()
        super().__init__()

    def update_commands(self):
        available_storages = []
        for storage in self.storages_for_sale.values():
            if storage.cost < levels.level.money:
                available_storages.append(self.name_for_command(storage.name))
        self.commands[0] = (['buy'], ['storage'], available_storages)
        super().update_commands()


    def print_info(self):
        print_value('Money', levels.level.money, 'space dollars')
        print('')
        print_title('Storages for sale:')
        print_list(['{}: {} space dollars'.format(s.name, s.cost) for s in self.storages_for_sale.values()])


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
        if cmd == self.CMD_DONE:
            return ActionMode()


mode = None


def run():
    global mode
    mode = ActionMode()
    print_info = True
    while True:
        if print_info:
            print('')
            mode.print_info()
            print('################################  SPACE  DINER  ################################')
        prompt = '({}) '.format(mode.prompt) if mode.prompt else ''
        cmd = input('{}>> '.format(prompt))
        next_mode = mode.parse(cmd)
        if next_mode:
            mode = next_mode
            print_info = True
        else:
            print_info = False

