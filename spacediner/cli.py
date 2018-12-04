import readline

from . import actions
from . import food
from . import guests
from . import kitchen
from . import merchants
from . import levels
from . import settings
from . import social
from . import storage
from . import time


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


def print_time(t):
    print('')
    if t == time.Clock.TIME_OFF:
        print('"Finally off..."')
    else:
        print('"A new day... work... work... work"')


class CommandCompleter:
    commands = None
    matches = []

    def __init__(self, commands):
        self.commands = commands
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

    def match_arg(self, arg_type, arg):
        if isinstance(arg_type, list):
            return arg in arg_type
        if arg_type == int:
            try:
                int(arg)
                return True
            except ValueError:
                return False

    def matching_commands(self, input):
        matching_commands = []
        for cmd in self.commands:
            arg_type_match = True
            for arg_type, arg in zip(cmd, input):
                if not self.match_arg(arg_type, arg):
                    arg_type_match = False
                    break
            if arg_type_match:
                matching_commands.append(cmd)
        return matching_commands

    def match_command(self, input):
        matching_commands = self.matching_commands(input)
        if len(matching_commands) != 1:
            return None
        command = matching_commands[0]
        if len(command) != len(input):
            return None
        return self.commands.index(command) + 1

    def _get_completed_args(self):
        buffer = readline.get_line_buffer()
        if not buffer:
            return []
        args = buffer.split()
        if buffer.endswith(' '):
            return args
        return args[:-1]

    def _suggestions(self, matching_commands, pos):
        suggestions = []
        for cmd in matching_commands:
            next_arg = cmd[pos]
            if isinstance(next_arg, list):
                suggestions.extend(next_arg)
            elif next_arg == int:
                suggestions.extend(['<num>'])
        return suggestions

    def complete(self, text, state):
        if state == 0:
            args = self._get_completed_args()
            matching_cmds = self.matching_commands(args)
            suggestions = self._suggestions(matching_cmds, len(args))
            if text:
                self.matches = [cmd for cmd in suggestions if cmd.startswith(text)]
            else:
                self.matches =  suggestions
        try:
            return self.matches[state] + ' '
        except IndexError:
            return None


class Mode:
    commands = None
    prompt = None
    names = {}
    completer = None
    no_input = False

    def __init__(self):
        self.update_commands()

    def update_commands(self):
        if not self.no_input:
            self.completer = CommandCompleter(self.commands)

    def print_info(self):
        raise NotImplemented()

    def print_help(self):
        raise NotImplemented()

    def exec(self, cmd, input):
        raise  NotImplemented()

    def parse(self, input):
        if input:
            input_list = input.split()
            matching_command = self.completer.match_command(input_list)
            if matching_command:
                return self.exec(matching_command, input_list)
        self.print_help()
        return None

    def name_for_command(self, name):
        cmd_name = name.replace(' ', '_').lower()
        self.names.update({cmd_name: name})
        return cmd_name

    def original_name(self, cmd_name):
        return self.names.get(cmd_name)


class DinerMode(Mode):
    CMD_COOKING = 1
    CMD_SERVICE = 2
    CMD_SHOPPING = 3
    CMD_CLOSE_UP = 4
    CMD_EXIT = 5
    commands = [
        (['cooking'],),
        (['service'],),
        (['shopping'],),
        (['close_up'],),
        (['exit'],),
    ]
    prompt = 'diner'

    def print_info(self):
        print_value('Level', levels.level.name)
        print_value('Day', time.now())
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
        if cmd == self.CMD_CLOSE_UP:
            time.tick()
            return AfterWorkMode()
        if cmd == self.CMD_EXIT:
            exit()


class ServiceMode(Mode):
    CMD_SERVE = 1
    CMD_TALK = 2
    CMD_DONE = 3
    commands = [
        (['serve'], [], ['to'], []),
        (['talk'], ['to'], []),
        (['done'], ),
    ]
    prompt = 'service'

    def update_commands(self):
        cooked_food = [self.name_for_command(f) for f in food.plated()]
        available_guests = [self.name_for_command(g) for g in guests.available_guests()]
        self.commands[self.CMD_SERVE - 1] = (['serve'], cooked_food, ['to'], available_guests)
        self.commands[self.CMD_TALK - 1] = (['talk'],['to'], available_guests)
        super().update_commands()

    def print_info(self):
        print_title('Food:')
        print_list(food.plated())
        print_title('Guests:')
        print_list(guests.available_guests())

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == self.CMD_SERVE:
            food = self.original_name(input[1])
            guest = self.original_name(input[3])
            action = actions.Serve(food, guest)
            action.perform()
            return self
        if cmd == self.CMD_TALK:
            guest = self.original_name(input[2])
            return TalkMode(guest)
        if cmd == self.CMD_DONE:
            return DinerMode()


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
        print_list(list(food.plated()))

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
            return DinerMode()


class ShoppingMode(Mode):
    CMD_BUY_STORAGE = 1
    CMD_BUY_INGREDIENT = 2
    CMD_DONE = 3
    commands = [
        (['buy'], []),
        (['buy'], int, [], ['from'], []),
        (['done'], ),
    ]
    prompt = 'shopping'
    storages_for_sale = None
    available_ingredients = None
    ingredients_for_sale = None

    def __init__(self):
        self.storages_for_sale = storage.for_sale()
        self.available_ingredients = storage.available_ingredients()
        self.ingredients_for_sale = merchants.ingredients_for_sale()
        super().__init__()

    def update_commands(self):
        available_storages = []
        for storage in self.storages_for_sale.values():
            if storage.cost < levels.level.money:
                available_storages.append(self.name_for_command(storage.name))
        self.commands[0] = (['buy'], available_storages)

        merchants = [self.name_for_command(m) for m in self.ingredients_for_sale.keys()]
        ingredients = []
        for mi in self.ingredients_for_sale.values():
            ingredients.extend([self.name_for_command(i) for i in mi.keys()])
        self.commands[1] = (['buy'], int, ingredients, ['from'], merchants,)

        super().update_commands()

    def print_info(self):
        print_value('Money', levels.level.money, 'space dollars')
        print('')
        print_title('Available Ingredients:')
        print_list(['{} {}s'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Igredients for sale:')
        for merchant, ingredients in  self.ingredients_for_sale.items():
            print('')
            print('Merchant: {}'.format(merchant))
            print_list(['{}: {} space dollars, {} in stock, {} required'.format(i, c, a, s)
                        for i, (a, c, s) in ingredients.items()])
        print_title('Storages for sale:')
        print_list(['{}: {} space dollars'.format(s.name, s.cost) for s in self.storages_for_sale.values()])


    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == self.CMD_BUY_STORAGE:
            storage = self.original_name(input[1])
            action = actions.BuyStorage(storage)
            action.perform()
            self.storages_for_sale.pop(storage)
            self.update_commands()
            return self
        if cmd == self.CMD_BUY_INGREDIENT:
            amount = int(input[1])
            ingredient = self.original_name(input[2])
            merchant = self.original_name(input[4])
            action = actions.BuyIngredients(merchant, ingredient, amount)
            try:
                action.perform()
                self.update_commands()
                merchant_ingredients = self.ingredients_for_sale.get(merchant)
                ingredient_amount, ingredient_cost, ingredient_storage = merchant_ingredients.get(ingredient)
                merchant_ingredients.update({ingredient: (ingredient_amount - amount, ingredient_cost, ingredient_storage)})
                self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient, 0) + amount})
            except RuntimeError as e:
                print(e)
            return self
        if cmd == self.CMD_DONE:
            return DinerMode()


class TalkMode(Mode):
    CMD_CHOICE = 1
    CMD_DONE = 2
    commands = [
        (int,),
        (['done'], ),
    ]
    prompt = 'talk'
    guest = None

    def __init__(self, guest):
        super().__init__()
        self.guest = guest

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print('"Hey, {}?"'.format(self.guest))
        print_list(['1: take order', '2: chat'])

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == self.CMD_CHOICE:
            choice = int(input[0])
            if choice > 2 or choice < 1:
                print('Invalid reply number.')
                return self
            if choice == 1:
                order = guests.get_order(self.guest)
                if order:
                    print('{}: I\'ll have something {}-ish.'.format(self.guest, order))
                else:
                    print('{}: Surprise me.'.format(self.guest))
            else:
                if not self.guest in social.chats_available():
                    print('"What\'s up, {}?"'.format(self.guest))
                    print('{}: "Breakfast is up.".'.format(self.guest))
                    return self
                chat = social.next_chat(self.guest)
                if not chat.replies:
                    print('"What\'s up, {}?"'.format(self.guest))
                    print('{}: "{}"'.format(self.guest, chat.question))
                    return self
                return ChatMode(self.guest, chat)
            return self
        if cmd == self.CMD_DONE:
            return ServiceMode()


class ChatMode(Mode):
    commands = [
        (int,),
    ]
    prompt = 'chat'
    guest = None
    chat = None

    def __init__(self, guest, chat):
        super().__init__()
        self.guest = guest
        self.chat = chat

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print('"What\'s up, {}?"'.format(self.guest))
        print('{}: "{}"'.format(self.guest, self.chat.question))
        print_list(['{}: "{}"'.format(i, reply) for i, reply in enumerate(self.chat.replies)])

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        reply = int(input[0])
        if reply > len(self.chat.replies) or reply < 0:
            print('Invalid reply number.')
            return self
        action = actions.Talk(self.guest, reply)
        action.perform()
        return ServiceMode()


class AfterWorkMode(Mode):
    CMD_WATCH_TV = 1
    CMD_SLEEP = 2
    commands = [
        (['watch_tv'],),
        (['sleep'],),
    ]
    prompt = 'after work'
    activities_done = 0

    def __init__(self):
        super().__init__()
        self.activities_done = 0

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print_title('TODO')

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        self.activities_done += 1
        if self.activities_done > 1 and cmd != self.CMD_SLEEP:
            print('')
            print('Let\'s not do this today.')
            return self
        if cmd == self.CMD_WATCH_TV:
            print('')
            print('You watched some TV...')
            return self
        if cmd == self.CMD_SLEEP:
            time.tick()
            return DinerMode()


mode = None
time_ticked = None


def run():
    global mode
    global time_ticked
    mode = DinerMode()
    print_info = True
    print('################################  SPACE  DINER  ################################')
    while True:
        if settings.DEBUG:
            levels.debug()
        if print_info:
            if time_ticked:
                print_time(time_ticked)
                time_ticked = None
            print('')
            mode.print_info()
        if not mode.no_input:
            prompt = '({}) '.format(mode.prompt) if mode.prompt else ''
            cmd = input('{}>> '.format(prompt))
            next_mode = mode.parse(cmd)
        else:
            next_mode = mode.exec(None, None)
        if next_mode:
            mode = next_mode
            print_info = True
        else:
            print_info = False


def worktime_callback():
    global time_ticked
    time_ticked = time.Clock.TIME_WORK


def offtime_callback():
    global time_ticked
    time_ticked = time.Clock.TIME_OFF


def init():
    time.register_callback(time.Clock.TIME_WORK, worktime_callback)
    time.register_callback(time.Clock.TIME_OFF, offtime_callback)
