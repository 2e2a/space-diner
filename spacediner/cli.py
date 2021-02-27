import os
import re
import readline
import textwrap
import math
from datetime import datetime

from . import activities
from . import cheats
from . import diner
from . import food
from . import guests
from . import kitchen
from . import shopping
from . import levels
from . import ingredients
from . import reviews
from . import skills
from . import social
from . import storage
from . import time


LINE_WIDTH = 100


def cls():
    os.system('cls' if os.name=='nt' else 'clear')


def print_text(str):
    # TODO: capitalize just the first letter.
    for line in textwrap.wrap(str, width=LINE_WIDTH):
        print(line)


def print_title(str):
    print(str)
    print('-' * (len(str)))


def print_list(list, double_columns=True):
    if list:
        length = None
        if double_columns and not any(len(e) >= (math.floor(LINE_WIDTH/2)-2) for e in list):
            for e in list:
                if length:
                    print('{}- {}'.format(' '*int((LINE_WIDTH/2)-length-2), e))
                    length = None
                else:
                    if list.index(e) == len(list) - 1:
                        print('- {}'.format(e))
                    else:
                        print('- {}'.format(e), end='')
                    length = len(e)
        else:
            for e in list:
                print('- {}'.format(e))
    else:
        print('-')
    print_newline()


def print_header(header_values=None):
    cls()
    number_of_tildes = int(math.floor((LINE_WIDTH - 13) / 2))
    print_text('~' * LINE_WIDTH)
    print('{} SPACE DINER'.format(' ' * number_of_tildes))
    print_text('~' * LINE_WIDTH)
    if header_values:
        for name, values in header_values:
            print_value(name, *values)
        print_text('~' * LINE_WIDTH)
        print_newline()


def print_value(key, *values):
    value = ' '.join([str(v) for v in values])
    print('{}: {}'.format(key, value))


def print_message(msg):
    print('*** {} ***'.format(msg))
    print_newline()


def print_dialog(name, msg):
    print('{}: "{}"'.format(name, msg))


def print_dialog_with_info(name, info, msg):
    print('{} {}: "{}"'.format(name, info, msg))


def print_newline():
    print('')


def ascii_name(name):
    ascii_name = re.sub(r'[^a-zA-Z0-9- ]+', '', name.lower(), count=16)
    ascii_name = ascii_name.strip('_')
    return ascii_name


class CommandCompleter:
    commands = None
    matches = []

    def __init__(self, commands):
        self.commands = commands
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

    def _get_completion(self, cmd, pos):
        if pos >= len(cmd):
            return None
        next_cmd_arg = cmd[pos + 1]
        if isinstance(next_cmd_arg, str):
            return [next_cmd_arg]
        elif isinstance(next_cmd_arg, list):
            return next_cmd_arg

    def _get_cmd_completions(self, cmd, pos):
        if pos >= len(cmd):
            return []
        next_cmd_arg = cmd[pos]
        if isinstance(next_cmd_arg, list):
            return next_cmd_arg
        elif isinstance(next_cmd_arg, str):
            return [next_cmd_arg]
        elif next_cmd_arg == int:
            return '1'

    def _get_arg_completions(self, arg, cmd_arg):
        completed = 0
        arg_split = arg.split()
        cmd_split = cmd_arg.split()
        part_incomplete = False
        for arg_part, cmd_part in zip(arg_split, cmd_split):
            if arg_part != ascii_name(cmd_part):
                part_incomplete = True
                break
            else:
                completed += 1
        ends_with_space = arg.endswith(' ')
        if not part_incomplete and not ends_with_space:
            completed -= 1
        completed = max(0, completed)
        completion = ' '.join(cmd_split[completed:])
        if '-' in arg:
            sub_args_completed = arg.count('-')
            remaining_completion_parts = completion.split('-')[sub_args_completed:]
            if len(remaining_completion_parts) > 1:
                completion = '-'.join(remaining_completion_parts)
            else:
                completion = remaining_completion_parts[0]
        return [completion]

    def _match_list(self, cmd, pos, arg, allow_partial):
        match = None
        completions = []
        cmd_arg = cmd[pos]
        for choice in cmd_arg:
            if arg == ascii_name(choice):
                match = choice
                completions.extend(self._get_cmd_completions(cmd, pos + 1))
            elif allow_partial and ascii_name(choice).startswith(arg):
                match = choice
                completions.extend(self._get_arg_completions(arg, choice))
        return match, completions

    def _match_string(self, cmd, pos, arg, allow_partial):
        match = None
        completion = None
        cmd_arg = cmd[pos]
        if arg == ascii_name(cmd_arg):
            match = cmd_arg
            completion = self._get_arg_completions(arg, cmd_arg)
        elif allow_partial and ascii_name(cmd_arg).startswith(arg):
            match = cmd_arg
            completion = self._get_arg_completions(arg, cmd_arg)
        return match, completion

    def _match_num(self, cmd, pos, arg, allow_partial):
        match = None
        completion = ['1']
        if arg.isnumeric():
            match = arg
            completion = [arg]
        return match, completion

    def match_arg(self, cmd, pos, arg, allow_partial=False):
        if pos >= len(cmd):
            return False, False
        arg = ascii_name(arg)
        cmd_arg = cmd[pos]
        match = None
        completion = None
        if not arg:
            match = ''
            completion = self._get_cmd_completions(cmd, pos)
        elif isinstance(cmd_arg, list):
            match, completion = self._match_list(cmd, pos, arg, allow_partial)
        elif isinstance(cmd_arg, str):
            match, completion = self._match_string(cmd, pos, arg, allow_partial)
        elif cmd_arg == int:
            match, completion = self._match_num(cmd, pos, arg, allow_partial)
        return match, completion

    def _arg_splits(self, cmd_input, pos=0):
        if pos >= len(cmd_input):
            return [[]]
        arg_splits = []
        for i in range(pos + 1, len(cmd_input) + 1):
            arg = ' '.join(cmd_input[pos:i])
            next_arg_splits = self._arg_splits(cmd_input, i)
            for next_arg_split in next_arg_splits:
                next_arg_split.insert(0, arg)
            arg_splits.extend(next_arg_splits)
        return arg_splits

    def matching_commands(self, cmd_input):
        matching_commands = []
        arg_splits = self._arg_splits(cmd_input)
        completions = None
        for cmd_num, cmd in enumerate(self.commands):
            if not cmd:
                continue
            for arg_split in arg_splits:
                cmd_arg_match = True
                matched_cmd = []
                if arg_split:
                    input_len = len(arg_split)
                    for i, arg in enumerate(arg_split):
                        is_last_arg = (i == input_len - 1)
                        match, completions = self.match_arg(cmd, i, arg, allow_partial=is_last_arg)
                        if match is None:
                            cmd_arg_match = False
                            break
                        else:
                            matched_cmd.append(match)
                else:
                    match, completions = self.match_arg(cmd, 0, '')
                if cmd_arg_match:
                    cmd_complete = len(matched_cmd) == len(cmd)
                    if not cmd_complete:
                        matched_cmd = None
                    matching_commands.append((cmd_num, matched_cmd, completions))
        return matching_commands

    def completions(self, cmd_input):
        completions = []
        for _, _, cmd_completions in self.matching_commands(cmd_input):
            if cmd_completions:
                completions.extend(cmd_completions)
        return completions

    def match_command(self, cmd_input):
        matching_commands = self.matching_commands(cmd_input)
        if len(matching_commands) != 1:
            return None, None
        cmd_num, matched_command, _ = matching_commands[0]
        return cmd_num, matched_command

    def split_input(self):
        buffer = readline.get_line_buffer()
        if not buffer:
            return []
        args = buffer.split()
        if buffer.endswith(' '):
            args.append('')
        return args

    def complete(self, text, state):
        if state == 0:
            cmd_input = self.split_input()
            self.matches = self.completions(cmd_input)
        try:
            return self.matches[state] + ' '
        except IndexError:
            return None


class Mode:
    commands = None
    prompt = None
    names = {}
    completer = None
    empty_input = False
    back_mode = None
    hint = None

    def __init__(self, back=None):
        self.back_mode = back
        self.update_commands()

    def update_commands(self):
        self.completer = CommandCompleter(self.commands)

    def wait_for_input(self):
        print_newline()
        input('<press ENTER to continue>')

    def print_header(self):
        print_header()

    def print_info(self):
        print('')

    def print_help(self):
        if self.commands:
            print_text('')
            print_title('Available commands')
            command_list = []
            for command in self.commands:
                text = ''
                is_available = True
                for words in command:
                    if isinstance(words, str):
                        text += '{} '.format(words)
                    elif isinstance(words, list):
                        if len(words) == 1:
                            text += '{} '.format(words[0])
                        elif len(words) > 1:
                            text += '{}/{}/etc. '.format(words[0], words[1])
                        else:
                            is_available = False
                    elif words == int:
                        text += 'NUMBER '
                if is_available:
                    command_list.append(text)
            print_list(command_list)
        self.wait_for_input()

    def print_hint(self):
        if self.hint:
            hint_text = '(Hint: {})'.format(self.hint)
            print_text(hint_text)
            print_newline()

    def exec(self, cmd, cmd_input):
        raise NotImplemented()

    def back(self):
        if self.back_mode:
            self.back_mode.update_commands()
            return self.back_mode

    def log(self, cmd_num, cmd):
        global logfile
        if not logfile:
            return
        logfile.write('{}; #{}; {};\n'.format(self.__class__.__name__, cmd_num, ' '.join(cmd)))

    def parse(self, cmd_input):
        if cmd_input.startswith('!'):
            cheats.cheat(cmd_input)
            self.update_commands()
            return self
        if cmd_input and self.commands:
            cmd_input_list = cmd_input.split()
            matched_cmd_num, matched_cmd = self.completer.match_command(cmd_input_list)
            if matched_cmd_num is not None and matched_cmd_num >= 0 and matched_cmd:
                self.log(matched_cmd_num, matched_cmd)
                return self.exec(matched_cmd_num, matched_cmd)
            else:
                self.print_help()
        elif self.empty_input:
            return self.exec(None, None)
        return None


class ChoiceMode(Mode):
    CMD_CHOICE = 0
    commands = [
        (int,),
    ]
    choices = []
    back_enabled = True
    back_label = 'Back'
    title = None

    def exec_choice(self, choice):
        raise NotImplemented

    def print_info(self):
        if self.title:
            print_title(self.title)
        choice_info = ['{}: {}'.format(i, choice) for i, choice in enumerate(self.choices, 1)]
        if self.back_enabled:
            choice_info += ['0: {}'.format(self.back_label)]
        print_list(choice_info, double_columns=False)

    def print_help(self):
        print_newline()
        print_text('Select a number.')
        self.wait_for_input()

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_CHOICE:
            try:
                choice = int(cmd_input[0])
                if choice < 0 or choice > len(self.choices):
                    print_message('Invalid choice.')
                    return self
                if self.back_enabled and choice == 0:
                    return self.back()
            except ValueError:
                print_message('Select a number.')
                return self
            return self.exec_choice(choice - 1)


class InfoMode(Mode):
    prompt = '<press ENTER to continue>'
    empty_input = True

    def exec(self, cmd, cmd_input):
        print_newline()
        return self.back()


class StartMode(ChoiceMode):
    prompt = 'start #'
    choices = ['Continue', 'New game', 'Load game']
    back_label = 'Exit'
    title = 'Start menu'

    def exec_choice(self, choice):
        if choice == 0:
            levels.autosave_load()
            print_value('Level', levels.level.name)
            return DinerMode()
        elif choice == 1:
            return NewGameMode(back=self)
        elif choice == 2:
            return LoadGameMode(back=self)

    def back(self):
        exit()


class NewGameMode(ChoiceMode):
    prompt = 'new game #'
    levels = None
    choices = None
    title = 'Select level'
    back_label = 'Exit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.levels = levels.list()
        self.choices = self.levels

    def exec_choice(self, choice):
        levels.init(self.levels[choice])
        self.print_header()
        print_text(levels.level.name)
        print_newline()
        print_text(levels.level.intro)
        print_newline()
        diner_name = input('Diner name (default: {}): '.format(diner.diner.name))
        if diner_name:
            diner.diner.name = diner_name
        chef_name = input('Your name: ')
        if chef_name:
            diner.diner.chef = 'Chef {}'.format(chef_name)
        return FirstHelpMode()

    def back(self):
        #return StartMode()
        exit()


class SaveGameMode(ChoiceMode):
    prompt = 'save #'
    saved_games = None
    choices = None
    title = 'Select slot'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_games = levels.saved_games()
        self.choices = []
        for slot in range(1, 9):
            file = self.saved_games.get(slot)
            if file:
                self.choices.append(file)
            else:
                self.choices.append('<empty>')

    def exec_choice(self, choice):
        levels.save_game(choice)
        return DinerMode()


class LoadGameMode(ChoiceMode):
    prompt = 'load #'
    choices = None
    title = 'Select saved game'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_games = levels.saved_games()
        self.choices = self.saved_games.items()

    def exec_choice(self, choice):
        levels.load_game(choice)
        print_value('Level', levels.level.name)
        return FirstHelpMode()


class FirstHelpMode(InfoMode):

    def print_info(self):
        title = 'Welcome to your new diner, {}!'.format(diner.diner.chef)
        print_title(title)
        print_text(
            'How to play? Use auto-complete: type the first letters of a command and press TAB. Type \'help\' to '
            'display a list of available commands. During your first day, you will receive general gameplay hints.\n'
            'What to do first? Take your guests\' orders in the diner, prepare food in the kitchen, and serve it.\n'
            'Heads up: your guests have specific dietary restrictions and preferences. '
            'Make them happy, and they will repay you in space dollars and positive reviews!'
        )
        print_newline()

    def back(self):
        time.tick()
        return DinerMode()


class DinerMode(Mode):
    CMD_KITCHEN = 0
    CMD_TAKE_ORDER = 1
    CMD_CHAT = 2
    CMD_SERVE = 3
    CMD_SEND_HOME = 4
    CMD_MENU = 5
    CMD_REVIEWS = 6
    CMD_COMPENDIUM = 7
    CMD_CLOSE_UP = 8
    CMD_EXIT = 9
    #CMD_SAVE = 9
    commands = [
        ('kitchen',),
        ('take order from', []),
        ('chat with', []),
        ('serve', [], 'to', []),
        ('send home', []),
        ('menu',),
        ('reviews',),
        ('compendium',),
        ('close up',),
        #('save',),
        ('exit',),
    ]
    prompt = 'diner >>'
    hint = (
        'In the dining room, you can chat with your guests, take their orders, and serve them food. '
        'For preparing food, go to the kitchen. When all the guests are gone, close up the diner - '
        'new guests will come tomorrow.'
    )

    def update_commands(self):
        cooked_food = food.plated()
        available_guests = guests.get_guests()
        guests_with_chats = guests.guests_with_chats()
        guests_with_orders = guests.guests_with_orders()
        guests_without_orders = guests.guests_without_orders()
        self.commands[self.CMD_TAKE_ORDER] = ('take order from', guests_without_orders) # FIXME: dont reinit, just set arg EVERYWHERE
        self.commands[self.CMD_CHAT] = ('chat with', guests_with_chats)
        self.commands[self.CMD_SERVE] = ('serve', cooked_food, 'to', guests_with_orders)
        self.commands[self.CMD_SEND_HOME] = ('send home', available_guests)
        super().update_commands()

    def print_header(self):
        available_guests = guests.get_guests()
        print_header([
            ('Location', [diner.diner.name, '(dining room)']),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
            ('Seats taken', ['{}/{}'.format(len(available_guests), diner.diner.seats)]),
            ('Sanitation', ['{}/5'.format(diner.diner.sanitation)]),
            ('Interior decoration', [', '.join(diner.diner.available_decoration)]),
        ])

    def print_info(self):
        available_guests = guests.get_guests()
        print_title('Food:')
        print_list(food.plated())
        print_title('Guests:')
        names_with_groups = []
        for guest_name in available_guests:
            guest = guests.get(guest_name)
            names_with_groups.append('{} ({})'.format(guest.name, guest.group_name if guest.groups else 'regular'))
        print_list(names_with_groups)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_KITCHEN:
            return KitchenMode(back=self)
        if cmd == self.CMD_TAKE_ORDER:
            guest = cmd_input[1]
            order = guests.take_order(guest)
            if order:
                print_dialog(guest, order)
            else:
                print_dialog(guest, 'There is nothing for me on the menu.')
                guests.leave(guest)
                print_text('{} left.'.format(guest))
            self.wait_for_input()
            return self
        if cmd == self.CMD_CHAT:
            guest = cmd_input[1]
            chat = guests.chat(guest)
            print_dialog(guest, chat)
            self.wait_for_input()
            self.update_commands()
            return self

        if cmd == self.CMD_SERVE:
            dish = cmd_input[1]
            guest = cmd_input[3]
            guests.serve(guest, dish)
            guests.leave(guest)
            print_text('{} left.'.format(guest))
            self.wait_for_input()
            return self
        if cmd == self.CMD_SEND_HOME:
            guest = cmd_input[1]
            guests.send_home(guest)
            print_text('{} left.'.format(guest))
            self.wait_for_input()
            return self
        if cmd == self.CMD_MENU:
            return DinerMenuMode(back=self)
        if cmd == self.CMD_REVIEWS:
            return ReviewsInfoMode(back=self)
        if cmd == self.CMD_COMPENDIUM:
            return CompendiumMode(back=self)
        if cmd == self.CMD_CLOSE_UP:
            for plated_food in food.plated():
                print_message('throw away {}'.format(plated_food))
            print_newline()
            for guest in guests.get_guests():
                guests.send_home(guest)
                print_text('{} left.'.format(guest))
            print_newline()
            time.tick()
            return ReviewsInfoMode(back=ActivityMode())
        #if cmd == self.CMD_SAVE:
        #    return SaveGameMode(back=self)
        if cmd == self.CMD_EXIT:
            #levels.autosave_save()
            #return StartMode()
            return NewGameMode()


class DinerMenuMode(InfoMode):

    def print_info(self):
        print_title('{} menu'.format(diner.diner.name))
        print_list(food.get_menu())


class KitchenMode(Mode):
    CMD_DINER = 0
    CMD_COOK = 1
    CMD_COMPENDIUM = 2
    CMD_TRASH = 3
    CMD_RECIPES = 4
    CMD_SAVE_RECIPE = 5
    commands = [
        ('diner',),
        ([], [],),
        ('compendium',),
        ('trash',),
        ('recipes',),
        ('save recipe', []),
    ]
    prompt = 'kitchen >>'
    orders = None
    available_ingredients = None
    available_devices = None
    hint = (
        'You can follow the available recipes or create your own dishes. Every dish consists of three ingredients. '
        'Once you have prepared them, they will be automatically plated as a completed dish.'
    )

    def __init__(self, **kwargs):
        self.orders = guests.ordered()
        self.available_devices = kitchen.available_devices()
        super().__init__(**kwargs)

    def update_commands(self):
        self.available_ingredients = storage.available_ingredients()
        preparations = [d.command for d in self.available_devices.values()]
        self.commands[self.CMD_COOK] = (preparations, list(self.available_ingredients.keys()))
        recipe_choices = food.plated()
        self.commands[self.CMD_SAVE_RECIPE] = ('save recipe', recipe_choices)
        super().update_commands()

    def print_header(self):
        print_header([
            ('Location', [diner.diner.name, '(kitchen)']),
            ('Time', [time.now()]),
        ])

    def print_info(self):
        print_title('Orders:')
        print_list(['{}: {}'.format(g, o) for g, o in self.orders.items()])
        print_title('Available ingredients:')
        ingredient_info = []
        for ingredient, available in self.available_ingredients.items():
            info = '{} x {}'.format(available, ingredient)
            custom_properties = ingredients.get_extra_properties(ingredient)
            if custom_properties:
                info += ' ({})'.format(', '.join(custom_properties))
            ingredient_info.append(info)
        print_list(ingredient_info)
        print_title('Kitchen:')
        print_list(['{} for {}'.format(d.name, d.preparation) for d in self.available_devices.values()])
        print_title('Prepared:')
        print_list(food.cooked_ingredients())
        print_title('Plated:')
        print_list(list(food.plated()))

    def _get_device(self, preparation_command):
        for device in self.available_devices.values():
            if device.command == preparation_command:
                return device
        return None

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_DINER:
            return self.back()
        if cmd == self.CMD_COOK:
            preparation_command = cmd_input[0]
            device = self._get_device(preparation_command)
            ingredient = cmd_input[1]
            food.cook_ingredients([(device.result, ingredient)])
            if food.ready_to_plate():
                name = food.plate()
                print_message('Plated {}'.format(name))
            self.update_commands()
            return self
        if cmd == self.CMD_COMPENDIUM:
            return CompendiumMode(back=self)
        if cmd == self.CMD_TRASH:
            cooked_ingredients = food.cooked_ingredients()
            if cooked_ingredients:
                print_message('throw away {}'.format(', '.join(cooked_ingredients)))
            food.trash()
            self.update_commands()
            return self
        if cmd == self.CMD_RECIPES:
            return RecipeMode(back=self)
        if cmd == self.CMD_SAVE_RECIPE:
            dish = cmd_input[1]
            return SaveRecipeMode(dish, back=self)


class RecipeMode(ChoiceMode):
    prompt = 'recipe #'
    choices = None
    title = 'Recipes'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = food.get_recipes()

    def _print_recipe(self, recipe):
        print_title(recipe.name)
        ingredient_list = [
            'Ingredient {}: {}'.format(i, ', '.join(properties))
            for i, properties in enumerate(recipe.ingredient_properties, 1)
        ]
        print_list(ingredient_list)

    def exec_choice(self, choice):
        recipe = food.get_recipe(self.choices[choice])
        self._print_recipe(recipe)
        self.wait_for_input()
        return self


class SaveRecipeMode(ChoiceMode):
    choices = None
    prompt = 'Add property:'
    back_label = 'Done'

    ingredient = 0
    dish = None
    ingredient_property_choices = None

    @property
    def title(self):
        return 'Choose which properties of ingredient {} will be part of the recipe'.format(self.ingredient + 1)

    def __init__(self, dish, **kwargs):
        self.dish = food.get(dish)
        self.ingredient_property_choices = [[], [], []]
        self.choices = self.dish.ingredient_properties(self.ingredient)
        super().__init__(**kwargs)

    def _print_recipe(self):
        print_title('Recipe:')
        print_list(', '.join(ingredient_properties) for ingredient_properties in self.ingredient_property_choices)

    def print_info(self):
        self._print_recipe()
        super().print_info()

    def exec_choice(self, choice):
        self.ingredient_property_choices[self.ingredient].append(self.choices[choice])
        del self.choices[choice]
        if not self.choices:
            return self.back()
        return self

    def back(self):
        if not self.ingredient_property_choices[self.ingredient]:
            return self
        self.ingredient += 1
        if self.ingredient < 3:
            self.choices = self.dish.ingredient_properties(self.ingredient)
            return self
        else:
            self._print_recipe()
            name = None
            while not name:
                name = input('Recipe name: '.format(self.prompt))
            food.save_as_recipe(name, self.ingredient_property_choices)
            print_message('saved {}.'.format(name))
            return super().back()


class CompendiumMode(ChoiceMode):
    prompt = 'choice #'
    choices = ['Guests', 'Ingredients']
    title = 'Compendium'

    def exec_choice(self, choice):
        if choice == 0:
            return GuestCompendiumMode(back=self)
        if choice == 1:
            return IngredientCompendiumMode(back=self)
        return self


class GuestCompendiumMode(ChoiceMode):
    prompt = 'guest #'
    choices = None
    title = 'Guest compendium'

    def __init__(self, **kwargs):
        self.choices = sorted(guests.get_available_groups())
        super().__init__(**kwargs)

    def exec_choice(self, choice):
        group = guests.get_group(self.choices[choice])
        if group.description:
            print_text(group.description)
        else:
            print_text('Unknown.')
        self.wait_for_input()
        return self


class IngredientCompendiumMode(ChoiceMode):
    prompt = 'ingredient #'
    choices = None
    title = 'Ingredient compendium'

    def __init__(self, **kwargs):
        ingredients = set(storage.available_ingredients().keys())
        ingredients.update(shopping.available_ingredients())
        self.choices = sorted(ingredients)
        super().__init__(**kwargs)

    def exec_choice(self, choice):
        ingredient = ingredients.get(self.choices[choice])
        if ingredient.description:
            print_text(ingredient.description)
            if ingredient.extra_properties:
                print_newline()
                print_text('Properties: {}'.format(', '.join(ingredient.extra_properties)))
        else:
            print_text('Unknown.')
        self.wait_for_input()
        return self


class ReviewsInfoMode(InfoMode):
    hint = (
        'The daily reviews provide pointers for ways to improve your food and your diner. Pay attention to the '
        'general preferences (+) and aversions (-) of your target groups and the individual taste of your regulars - '
        'you might be able to elevate their orders with something they like.'
    )

    def _rating_info(self, name, count, rating):
        if count == 0:
            return '{}:\tno reviews yet'.format(name)
        n_stars = round(rating)
        return '[{}{}] ({:0.1f}) - {} - based on {} review(s)'.format(
            '*' * n_stars,
            '-' * (5 - n_stars),
            float(rating),
            name,
            count,
            )

    def print_header(self):
        print_header([
            ('Location', [diner.diner.name, '(office)']),
            ('Time', [time.now()]),
        ])

    def print_info(self):
        print_text('You read today\'s reviews.')
        print_text('')
        print_title('Ratings')
        ratings = []
        for group, rating in reviews.get_ratings().items():
            rating = self._rating_info(group, rating.count, rating.aggregate)
            ratings.append(rating)
        print_list(ratings)

        print_title('Today\'s reviews')
        todays_reviews = reviews.get_reviews()
        print_list(todays_reviews)

        print_title('Discovered preferences')
        guest_likes = []
        for guest, (likes, dislikes) in reviews.get_likes().items():
            if not likes and not dislikes:
                continue
            guest_like = '{}: '.format(guest)
            if likes:
                guest_like += ', '.join(map(lambda x: '+' + x, likes))
            if dislikes:
                if likes:
                    guest_like += ', '
                guest_like += ', '.join(map(lambda x: '-' + x, dislikes))
            guest_likes.append(guest_like)
        print_list(guest_likes)


class ActivityMode(ChoiceMode):
    prompt = 'menu #'
    title = 'Available activities'
    back_enabled = False
    activities = None
    meetings = None
    hint = (
        'Evening activities can advance your social relationships: when you make your regulars happy, they might '
        'invite you to social events. Other activities can affect your skills. Do not forget to clean your diner '
        'once in a while.'
    )

    def __init__(self, **kwargs):
        self.meetings = sorted(social.available_meetings())
        meeting_choices = list(map(lambda name: 'meet ' + name, self.meetings))
        self.activities = sorted(activities.available_activities())
        self.fixed_activities = ['sleep']
        if diner.diner.is_dirty:
            self.fixed_activities.append('clean diner')
        self.fixed_activities = sorted(self.fixed_activities)
        self.choices = meeting_choices + self.activities + self.fixed_activities
        super().__init__(**kwargs)

    def print_skill(self, name, level):
        progress = '#' * int(level) + '-' * (skills.MAX_SKILL_LEVEL - int(level))
        line = '[{}] {}/{} - {}'.format(progress, level, skills.MAX_SKILL_LEVEL, name)
        return line

    def print_skills(self):
        print_title('Skills')
        skill_values = [self.print_skill(name, level) for name, level in skills.get_levels()]
        print_list(skill_values)

    def print_header(self):
        print_header([
            ('Location', [diner.diner.name, '(outside)']),
            ('Time', [time.now()]),
        ])

    def print_info(self):
        print_text('Now you have time for one evening activity.')
        print_newline()
        print_value('Sanitation status of the diner', '{}/5'.format(diner.diner.sanitation))
        print_newline()
        self.print_skills()
        super().print_info()

    def exec_choice(self, choice):
        if choice < len(self.meetings):
            guest = self.meetings[choice]
            return MeetingMode(guest)
        elif choice < len(self.meetings) + len(self.activities):
            choice -= len(self.meetings)
            activity = self.activities[choice]
            activities.do(activity)
            self.print_skills()
        else:
            choice -= (len(self.meetings) + len(self.activities))
            if self.fixed_activities[choice] == 'clean diner':
                diner.diner.clean()
                print_message('Diner cleaned.')
        self.wait_for_input()
        return SleepMode()


class MeetingMode(ChoiceMode):
    prompt = 'reply #'
    choices = None
    title = 'Answer'
    back_enabled = False

    guest = None
    meeting = None

    def __init__(self, guest, **kwargs):
        self.guest = guest
        super().__init__(**kwargs)
        self.meeting = social.get(self.guest).get_meeting()
        self.choices = self.meeting.get_replies()

    def print_info(self):
        print_text(self.meeting.text)
        print_dialog(self.guest, self.meeting.question)
        print_newline()
        super().print_info()

    def exec_choice(self, choice):
        reply = choice
        social.meet(self.guest, reply)
        social.lock_friendship(self.guest)
        self.wait_for_input()
        return SleepMode()


class SleepMode(InfoMode):

    def print_info(self):
        print_text('You go to sleep.')
        print_newline()

    def back(self):
        time.tick()
        if time.calendar.is_week_start:
            return DinerMenuEditMode()
        return ShoppingMode()


class DinerMenuEditMode(ChoiceMode):
    prompt = 'edit #'
    choices = None
    title = 'Update weekly diner menu'
    back_label = 'Done'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = food.get_menu()

    def exec_choice(self, choice):
        return DinerMenuItemMode(item=choice, back=self)

    def back(self):
        return ShoppingMode()


class DinerMenuItemMode(ChoiceMode):
    prompt = 'add to menu #'
    choices = None
    title = 'Select recipe'
    item = None

    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.item = item
        self.choices = food.not_on_menu()

    def exec_choice(self, choice):
        food.update_menu(self.item, self.choices[choice])
        return self.back()


class ShoppingMode(ChoiceMode):
    prompt = 'merchant #'
    choices = None
    title = 'Visit merchant'
    hint = (
        'Every morning you have the opportunity to stock up on supplies. Try to plan ahead and to be prepared even '
        'for unexpectedly crowded days at the diner. New merchants might become available during the game.'
    )
    ingredients_for_sale = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = shopping.get_available()

    def update_commands(self):
        self.ingredients_for_sale = shopping.for_sale()
        super().update_commands()

    def print_header(self):
        print_header([
            ('Location', [shopping.market.name]),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
        ])

    def print_info(self):
        if shopping.market.description:
            print_text(shopping.market.description)
            print_newline()
        print_title('Merchants available today')
        print_list([
            '{} [{}]'.format(merchant, ', '.join(merchant_ingredients))
            for merchant, merchant_ingredients in self.ingredients_for_sale.items()
        ])
        super().print_info()

    def exec_choice(self, choice):
        merchant = self.choices[choice]
        merchant_mode = MerchantMode(merchant)
        merchant_description = shopping.get(merchant).description
        if merchant_description:
            print_text(merchant_description)
        if shopping.has_chat_available(merchant):
            owner = shopping.owner(merchant)
            chat = shopping.chat(merchant)
            print_dialog(owner, chat)
            self.wait_for_input()
        return merchant_mode

    def back(self):
        time.tick()
        return DinerMode()


class MerchantMode(Mode):
    CMD_BUY_INGREDIENT = 0
    CMD_DONE = 1
    commands = [
        ('buy', int, []),
        ('done',),
    ]
    prompt = 'shopping >>'
    merchant = None
    available_ingredients = None
    ingredients_for_sale = None

    def __init__(self, merchant, **kwargs):
        self.merchant = merchant
        super().__init__(**kwargs)

    def update_commands(self):
        self.available_ingredients = storage.available_ingredients()
        self.ingredients_for_sale = shopping.merchant_for_sale(self.merchant)
        ingredient_names = list(self.ingredients_for_sale.keys())
        self.commands[self.CMD_BUY_INGREDIENT] = ('buy', int, ingredient_names)
        super().update_commands()

    def print_header(self):
        print_header([
            ('Location', [shopping.market.name, ' - ', self.merchant]),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
        ])

    def print_info(self):
        print_title('Ingredients for sale:')
        print_list([
            '{}: {} space dollars, {} in stock, {} required'.format(ingredient, cost, amount, stock)
            for ingredient,  (amount, cost, stock) in self.ingredients_for_sale.items()
        ])
        print_title('Ingredients in stock in the diner:')
        print_list(['{} x {}'.format(a, i) for i, a in self.available_ingredients.items()])

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_BUY_INGREDIENT:
            amount = int(cmd_input[1])
            ingredient = cmd_input[2]
            error = None
            merchant = shopping.get(self.merchant)
            if not merchant.is_ingredient_available(ingredient, amount):
                error = 'Not enough ingredients'
            cost = merchant.cost(ingredient) * amount
            if cost > levels.level.money:
                error = 'Not enough money'
            if not error:
                levels.level.money = levels.level.money - cost
                merchant.buy(ingredient, amount)
                storage.store_ingredient(ingredient, amount)
            else:
                print_message('Could not buy ingredients: {}'.format(error))
            self.update_commands()
            return self
        if cmd == self.CMD_DONE:
            return ShoppingMode()


mode = None
logfile = None


def run(args):
    global mode
    global logfile
    if args.get('log', False):
        logfile_name = 'space-diner_{}.log'.format(datetime.now().strftime('%Y-%m-%d-%H%M%S'))
        logfile = open(logfile_name, 'w')
    #mode = StartMode()  # TODO: restore when save & load works
    mode = NewGameMode()
    while True:
        try:
            mode.print_header()
            mode.print_info()
            if time.calendar.is_first_day:
                mode.print_hint()
            prompt = '{} '.format(mode.prompt) if mode.prompt else ''
            cmd = input('{} '.format(prompt))
            print_newline()
            next_mode = mode.parse(cmd)
            if next_mode:
                mode = next_mode
        except (KeyboardInterrupt, EOFError):
            try:
                print_newline()
                yes = input('Save and exit game? (y/N) ')
                if yes in ['y', 'Y']:
                    #levels.autosave_save()
                    if logfile:
                        logfile.close()
                    exit()
            except (KeyboardInterrupt, EOFError):
                print_newline()
                if logfile:
                    logfile.close()
                exit()


def init():
    pass
