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
    print('')
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
    print('')


def print_message(msg):
    print('*** {} ***'.format(msg))


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

    def matching_commands(self, cmd_input):
        matching_commands = []
        for cmd in self.commands:
            arg_type_match = True
            for arg_type, arg in zip(cmd, cmd_input):
                if not self.match_arg(arg_type, arg):
                    arg_type_match = False
                    break
            if arg_type_match:
                matching_commands.append(cmd)
        return matching_commands

    def match_command(self, cmd_input):
        matching_commands = self.matching_commands(cmd_input)
        if len(matching_commands) != 1:
            return None
        command = matching_commands[0]
        if len(command) != len(cmd_input):
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

    def exec(self, cmd, cmd_input):
        raise  NotImplemented()

    def parse(self, cmd_input):
        if cmd_input:
            cmd_input_list = cmd_input.split()
            matching_command = self.completer.match_command(cmd_input_list)
            if matching_command:
                return self.exec(matching_command, cmd_input_list)
        self.print_help()
        return None

    def name_for_command(self, name):
        cmd_name = name.replace(' ', '_').lower()
        self.names.update({cmd_name: name})
        return cmd_name

    def original_name(self, cmd_name):
        return self.names.get(cmd_name)


class ChoiceMode(Mode):
    CMD_CHOICE = 1
    commands = [
        (int,),
    ]
    size = 0
    choice_info = []
    back_label = 'Back'

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec_choice(self, choice):
        raise  NotImplemented

    def back(self):
        raise NotImplemented

    def print_info(self):
        choice_info = self.choice_info + ['0: {}'.format(self.back_label)]
        print_list(choice_info)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_CHOICE:
            choice = int(cmd_input[0])
            if choice < 0 or choice > (self.size + 1):
                print('Invalid choice.')
                return self
            if choice == 0:
                return self.back()
            return self.exec_choice(choice)


class MenuMode(ChoiceMode):
    prompt = 'menu #'
    size = 3
    choice_info = ['1: Continue', '2: New game', '3: Load game']
    back_label = 'Exit'

    def print_info(self):
        print_title('Menu')
        super().print_info()

    def exec_choice(self, choice):
        if choice == 1:
            levels.autosave_load()
            return DinerMode()
        elif choice == 2:
            return NewGameMode()
        elif choice == 3:
            return LoadGameMode()

    def back(self):
        exit()


class NewGameMode(ChoiceMode):
    prompt = 'new game #'
    levels = None
    choice_info = None

    def __init__(self):
        super().__init__()
        self.levels = levels.list()
        self.size = len(self.levels)

    def print_info(self):
        print_title('Select level')
        self.choice_info = ['{}: {}'.format(i, level) for i, level in enumerate(self.levels, 1)]
        super().print_info()

    def exec_choice(self, choice):
        levels.init(self.levels[choice - 1])
        time.tick()
        return DinerMode()

    def back(self):
        return MenuMode()


class SaveGameMode(ChoiceMode):
    prompt = 'save #'
    saved_games = None
    size = 9
    choice_info = None

    def __init__(self):
        super().__init__()
        self.saved_games = levels.saved_games()

    def print_info(self):
        print_title('Select slot')
        self.choice_info = []
        for slot in range(1,self.size + 1):
            file = self.saved_games.get(slot)
            if file:
                self.choice_info.append('{}: {}'.format(slot, file))
            else:
                self.choice_info.append('{}: <empty>'.format(slot))
        super().print_info()

    def exec_choice(self, choice):
        levels.save_game(choice)
        return DinerMode()

    def back(self):
        return DinerMode()


class LoadGameMode(ChoiceMode):
    prompt = 'load #'
    size = 9
    choice_info = None

    def __init__(self):
        super().__init__()
        self.saved_games = levels.saved_games()

    def print_info(self):
        print_title('Select saved game')
        self.choice_info = ['{}: {}'.format(slot, file) for slot, file in self.saved_games.items()]
        super().print_info()

    def exec_choice(self, choice):
        levels.load_game(choice)
        return DinerMode()

    def back(self):
        return MenuMode()


class DinerMode(Mode):
    CMD_COOKING = 1
    CMD_SERVICE = 2
    CMD_SHOPPING = 3
    CMD_CLOSE_UP = 4
    CMD_SAVE = 5
    CMD_EXIT = 6
    commands = [
        (['cooking'],),
        (['service'],),
        (['shopping'],),
        (['close_up'],),
        (['save'],),
        (['exit'],),
    ]
    prompt = 'diner >>'

    def print_info(self):
        print_value('Level', levels.level.name)
        print_value('Day', time.now())
        print_value('Money', levels.level.money, 'space dollars')

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_COOKING:
            return CookingMode()
        if cmd == self.CMD_SERVICE:
            return ServiceMode()
        if cmd == self.CMD_SHOPPING:
            return ShoppingMode()
        if cmd == self.CMD_CLOSE_UP:
            time.tick()
            return AfterWorkMode()
        if cmd == self.CMD_SAVE:
            return SaveGameMode()
        if cmd == self.CMD_EXIT:
            levels.autosave_save()
            return MenuMode()


class ServiceMode(Mode):
    CMD_SERVE = 1
    CMD_TALK = 2
    CMD_DONE = 3
    commands = [
        (['serve'], [], ['to'], []),
        (['talk'], ['to'], []),
        (['done'], ),
    ]
    prompt = 'service >>'

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

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_SERVE:
            food = self.original_name(cmd_input[1])
            guest = self.original_name(cmd_input[3])
            action = actions.Serve(food, guest)
            action.perform()
            return self
        if cmd == self.CMD_TALK:
            guest = self.original_name(cmd_input[2])
            return TalkMode(guest)
        if cmd == self.CMD_DONE:
            return DinerMode()


class CookingMode(Mode):
    CMD_COOK = 1
    CMD_PLATE = 2
    CMD_RECIPES = 3
    CMD_CREATE_RECIPE = 4
    CMD_ABORT = 5
    CMD_DONE = 6
    commands = [
        (['cook'], [], ),
        (['plate'], ),
        (['recipes'], ),
        (['write'], ['down'], ['recipe'] ),
        (['abort'], ),
        (['done'], ),
    ]
    prompt = 'cooking >>'
    action = None
    available_ingredients = None
    available_devices = None
    prepared_components = None

    def __init__(self):
        global actions_saved
        self.prepared_components = []
        self.available_ingredients = storage.available_ingredients()
        self.available_devices = kitchen.available_devices()
        if len(actions_saved) == 0:
            self.action = actions.Cook()
        else:
            self.action = actions_saved[0]
            del actions_saved[0]
            for preparation_participle, ingredient in self.action.food.ingredients:
                self.prepared_components.append('{} {}'.format(preparation_participle, ingredient))
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

    def exec(self, cmd, cmd_input):
        global actions_saved
        if cmd == self.CMD_COOK:
            if len(self.prepared_components) >= 3:
                print_message('Maximum number of ingredients prepared')
            else:
                preparation_command = cmd_input[0]
                device = self._get_device(preparation_command)
                ingredient = self.original_name(cmd_input[1])
                self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient) - 1})
                self.action.add_ingredients([(device.preparation_participle, ingredient)])
                self.prepared_components.append('{} {}'.format(device.preparation_participle, ingredient))
                self.update_commands()
            return self
        if cmd == self.CMD_PLATE:
            self.action.perform()
            self.action = actions.Cook()
            self.prepared_components = []
            return self
        if cmd == self.CMD_CREATE_RECIPE:
            print_title('???')
            print_list(['{} {}'.format(
                preparation, ingredient) for preparation, ingredient in self.action.food.ingredients])
            name = input('recipe name: ')
            if not name:
                print_message('aborted')
            else:
                food.create_recipe(name, self.action.food.ingredients)
                print_message('recipe saved as "{}"'.format(name))
            return self
        if cmd == self.CMD_RECIPES:
            actions_saved.append(self.action)
            return RecipeMode()
        if cmd == self.CMD_ABORT:
            self.action = actions.Cook()
            self.prepared_components = []
            return self
        if cmd == self.CMD_DONE:
            actions_saved.append(self.action)
            return DinerMode()


class RecipeMode(ChoiceMode):
    prompt = 'recipe #'
    recipes = None
    size = 0
    choice_info = None

    def __init__(self):
        super().__init__()
        self.recipes = food.get_recipes()
        self.size = len(self.recipes) + 1

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print_title('Recipes:')
        self.choice_info = ['{}: {}'.format(i, file) for i, file in enumerate(self.recipes, 1)]
        super().print_info()

    def exec_choice(self, choice):
        recipe = food.get_recipe(self.recipes[choice - 1])
        print_title(recipe.name)
        ingredient_list = [' '.join(properties) for properties in recipe.ingredient_properties]
        print_list(ingredient_list)
        return self

    def back(self):
        return CookingMode()


class ShoppingMode(Mode):
    CMD_BUY_STORAGE = 1
    CMD_BUY_INGREDIENT = 2
    CMD_DONE = 3
    commands = [
        (['buy'], []),
        (['buy'], int, [], ['from'], []),
        (['done'], ),
    ]
    prompt = 'shopping >>'
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
        print_title('Available Ingredients:')
        print_list(['{} {}s'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Ingredients for sale:')
        for merchant, ingredients in  self.ingredients_for_sale.items():
            print('Merchant: {}'.format(merchant))
            print_list(['{}: {} space dollars, {} in stock, {} required'.format(i, c, a, s)
                        for i, (a, c, s) in ingredients.items()])
        print_title('Storages for sale:')
        print_list(['{}: {} space dollars'.format(s.name, s.cost) for s in self.storages_for_sale.values()])


    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_BUY_STORAGE:
            storage = self.original_name(cmd_input[1])
            action = actions.BuyStorage(storage)
            action.perform()
            self.storages_for_sale.pop(storage)
            self.update_commands()
            return self
        if cmd == self.CMD_BUY_INGREDIENT:
            amount = int(cmd_input[1])
            ingredient = self.original_name(cmd_input[2])
            merchant = self.original_name(cmd_input[4])
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


class TalkMode(ChoiceMode):
    prompt = 'talk #'
    size = 3
    guest = None
    choice_info = ['1: take order', '2: chat']


    def __init__(self, guest):
        super().__init__()
        self.guest = guest

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print('"Hey, {}?"'.format(self.guest))
        super().print_info()

    def exec_choice(self, choice):
        if choice == 1:
            order = guests.get_order(self.guest)
            if order:
                print('{}: I\'ll have something {}-ish.'.format(self.guest, order))
            else:
                print('{}: Surprise me.'.format(self.guest))
            return self
        elif choice == 2:
            guest = guests.get(self.guest)
            if guest.chatted_today:
                print('"What\'s up, {}?"'.format(self.guest))
                print('{}: "Enough chatting for today, I\'m hungry.".'.format(self.guest))
                return self
            guest.chatted_today = True
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

    def back(self):
        return ServiceMode()


class ChatMode(ChoiceMode):
    prompt = 'chat #'
    guest = None
    chat = None
    choice_info = None

    def __init__(self, guest, chat):
        super().__init__()
        self.guest = guest
        self.chat = chat
        self.size = len(self.chat.replies)

    def update_commands(self):
        super().update_commands()

    def print_info(self):
        print('"What\'s up, {}?"'.format(self.guest))
        print('{}: "{}"'.format(self.guest, self.chat.question))
        self.choice_info = ['{}: "{}"'.format(i, reply) for i, reply in enumerate(self.chat.replies)]
        super().print_info()

    def exec_choice(self, choice):
        action = actions.Chat(self.guest, choice)
        action.perform()
        return TalkMode(self.guest)


    def back(self):
        return TalkMode(self.guest)


class AfterWorkMode(Mode):
    CMD_WATCH_TV = 1
    CMD_SLEEP = 2
    commands = [
        (['watch_tv'],),
        (['sleep'],),
    ]
    prompt = 'after work >>'
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

    def exec(self, cmd, cmd_input):
        self.activities_done += 1
        if self.activities_done > 1 and cmd != self.CMD_SLEEP:
            print('Let\'s not do this today.')
            return self
        if cmd == self.CMD_WATCH_TV:
            print('You watched some TV...')
            return self
        if cmd == self.CMD_SLEEP:
            time.tick()
            return DinerMode()


mode = None
actions_saved = []
time_ticked = None


def run():
    global mode
    global time_ticked
    mode = MenuMode()
    print_info = True
    print('################################  SPACE  DINER  ################################')
    while True:
        if settings.DEBUG:
            levels.debug()
        if print_info:
            if time_ticked:
                print_time(time_ticked)
                time_ticked = None
            mode.print_info()
        if not mode.no_input:
            prompt = '{} '.format(mode.prompt) if mode.prompt else ''
            cmd = input('{} '.format(prompt))
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
