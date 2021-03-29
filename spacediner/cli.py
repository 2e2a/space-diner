import math
import os
import re
import readline
import rlcompleter
import textwrap
import shutil
import sys
from datetime import datetime

from . import activities
from . import cheats
from . import diner
from . import food
from . import goals
from . import guests
from . import kitchen
from . import shopping
from . import levels
from . import ingredients
from . import reviews
from . import save as save_module
from . import settings
from . import skills
from . import social
from . import storage
from . import time


LINE_WIDTH = 100


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def line_width():
    width = LINE_WIDTH
    terminal_width = shutil.get_terminal_size(fallback=(LINE_WIDTH, 24)).columns
    if terminal_width < LINE_WIDTH:
        width = terminal_width
    return width


def centering_spaces(text):
    return ' ' * int((line_width() - len(text)) / 2)


def is_small_screen():
    return line_width() < LINE_WIDTH


def wait_for_input():
    print_newline()
    if settings.text_only():
        print_text('Press ENTER to continue.')
    else:
        print_text('<press ENTER to continue>')
    input('')


def input_with_default(default, prompt='path: '):
    if sys.platform == 'linux':
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            return input(prompt)
        finally:
            readline.set_startup_hook()
    else:
        print_text('Default: {} (copy+paste and adjust path if necessary)'.format(default))
        path = input(prompt)
        return path if path else default


def print_text(text):
    # TODO: capitalize just the first letter.
    for line in textwrap.wrap(text, width=line_width()):
        print(line)


def print_title(text):
    if settings.text_only():
        print(text)
    else:
        print(text)
        print('-' * (len(text)))


def print_list(text_list, double_columns=True):
    if text_list:
        length = None
        if (
                double_columns and not is_small_screen()
                and not any(len(e) >= (math.floor(LINE_WIDTH/2)-2) for e in text_list)
        ):
            for text in text_list:
                if length:
                    print('{}- {}'.format(' '*int((LINE_WIDTH/2)-length-2), text))
                    length = None
                else:
                    if text_list.index(text) == len(text_list) - 1:
                        print('- {}'.format(text))
                    else:
                        print('- {}'.format(text), end='')
                    length = len(text)
        else:
            for text in text_list:
                print_text('- {}'.format(text))
    else:
        print('-')
    print_newline()


def print_header(header_values=None):
    cls()
    if settings.text_only():
        print('SPACE DINER')
    else:
        width = line_width()
        number_of_tildes = int(math.floor((width - 13) / 2))
        print_text('~' * width)
        print('{} SPACE DINER'.format(' ' * number_of_tildes))
        print_text('~' * width)
    if header_values:
        for name, values in header_values:
            print_value(name, *values)
        if not settings.text_only():
            print_text('~' * width)
    print_newline()


def print_value(key, *values):
    value = ' '.join([str(v) for v in values])
    print('{}: {}'.format(key, value))


def print_message(msg):
    print('*{}*'.format(msg))


def print_dialog(name, msg):
    print_text('{}: "{}"'.format(name, msg))


def print_dialog_with_info(name, info, msg):
    print_text('{} {}: "{}"'.format(name, info, msg))


def print_newline():
    print('')


def ascii_name(name):
    ascii_name = re.sub(r'[^a-zA-Z0-9- ()]+', '', name.lower(), count=16)
    ascii_name = ascii_name.strip('_')
    return ascii_name


class CommandCompleter:
    commands = None
    matches = []

    def __init__(self, commands):
        self.commands = commands
        readline.set_completer(self.complete)
        if readline.__doc__ and 'libedit' in readline.__doc__:
            # OSX
            readline.parse_and_bind("bind ^I rl_complete")
        else:
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

    def _get_partial_cmd_completions(self, cmd, intput_arg):
        next_cmd_arg = cmd[-1]
        if isinstance(next_cmd_arg, list):
            return [arg for arg in next_cmd_arg if arg.startswith(intput_arg)]
        elif isinstance(next_cmd_arg, str):
            return next_cmd_arg
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
            elif remaining_completion_parts:
                completion = remaining_completion_parts[0]
        if completion.startswith('('):
            completion = completion[1:]
        return [completion]

    def _match_list(self, cmd, pos, arg, allow_partial):
        match = None
        completions = []
        cmd_arg = cmd[pos]
        for choice in cmd_arg:
            if arg == ascii_name(choice):
                match = choice
                if allow_partial:
                    completions.extend(self._get_partial_cmd_completions(cmd, arg))
                else:
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
            return None, None
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

    def _completion_matches(self, completions, input_arg):
        return any(completion for completion in completions if completion.endswith(input_arg))

    def match_command(self, cmd_input):
        matching_commands = self.matching_commands(cmd_input)
        if matching_commands and len(matching_commands) == 1:
            cmd_num, matched_command, completions = matching_commands[0]
            if (
                    not completions
                    or completions and self._completion_matches(completions, cmd_input[-1])
            ):
                return cmd_num, matched_command
        return None, None

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
    hint_shown = False
    dont_truncate_cmd_help = []

    def __init__(self, back=None):
        self.back_mode = back
        self.update_commands()

    def update_commands(self):
        self.completer = CommandCompleter(self.commands)

    def get_prompt(self):
        if settings.text_only():
            return 'Your command:'
        else:
            return self.prompt

    def wait_for_input(self):
        wait_for_input()

    def print_header(self):
        print_header()

    def print_info(self):
        print('')

    def print_help(self):
        if self.hint:
            print_text(self.hint)
            print_newline()
        if self.commands:
            print_text('')
            print_title('Available commands')
            command_list = []
            for cmd_num, command in enumerate(self.commands):
                text = ''
                is_available = True
                for words in command:
                    if isinstance(words, str):
                        text += '{} '.format(words)
                    elif isinstance(words, list):
                        if len(words) == 1:
                            text += '{} '.format(words[0])
                        elif len(words) > 1:
                            if cmd_num in self.dont_truncate_cmd_help:
                                text += '/'.join(words)
                            else:
                                text += '{}/{}/etc. '.format(words[0], words[1])
                        else:
                            is_available = False
                    elif words == int:
                        text += 'NUMBER '
                if is_available:
                    command_list.append(text)
            print_list(command_list)
        print_text('Use auto-complete: type the first letters of a command and press TAB.')
        self.wait_for_input()

    def print_hint(self):
        if self.hint and not self.hint_shown:
            hint_text = '*Info*: {}'.format(self.hint)
            print_text(hint_text)
            print_newline()
            self.hint_shown = True

    def print_tutorial(self):
        if levels.is_tutorial_enabled():
            from .tutorial import get_mode_tutorial
            text = get_mode_tutorial(self)
            if text:
                print_text('*Tutorial*: {}'.format(text))
                print_newline()

    def increment_tutorial(self, cmd_num):
        from .tutorial import increment_tutorial
        increment_tutorial(self, cmd_num)

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
                self.increment_tutorial(matched_cmd_num)
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

    def get_prompt(self):
        if settings.text_only():
            return 'Your choice:'
        else:
            return self.prompt

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
    empty_input = True

    def exec(self, cmd, cmd_input):
        print_newline()
        return self.back()

    def get_prompt(self):
        if settings.text_only():
            return 'Press ENTER to continue.'
        else:
            return '<press ENTER to continue>'

class LogoMode(InfoMode):

    prompt = ''

    def print_header(self):
        cls()
        if settings.text_only():
            print_text('Welcome to Space Diner!')
            print_newline()
            print_text('Press ENTER to start the game.')
        else:
            print_newline()
            print_newline()
            logo = (
                '############## SPACE DINER ##############\n'
                '#                                       #\n'
                '#                          .-"""""-.    #\n'
                '#   > plate bun           (_________)   #\n'
                '#   > plate pickles        o o o o o    #\n'
                '#   > grill tentacle       xXxXxXxXx    #\n'
                '#   > serve Space Burger  (_________)   #\n'
                '#                                       #\n'
                '#########################################\n'
            )
            for line in logo.split('\n'):
                print(centering_spaces(line) + line)
            prompt_text = '<press ENTER to start the game>'
            print_text(centering_spaces(prompt_text) + prompt_text)

    def get_prompt(self):
        return None

    def back(self):
        return StartMode()


class StartMode(ChoiceMode):
    prompt = 'start #'
    choices = ['Load Game', 'New game']
    back_label = 'Exit'
    title = 'Start menu'

    def exec_choice(self, choice):
        if not save_module.has_save_path():
            save_module.set_save_path()
        if choice == 0:
            return LoadGameMode(back=self)
        elif choice == 1:
            return NewGameMode(back=self)

    def print_header(self):
        print_header([
            ('A game by', ['Marta and Alexej (Gvarab Games)']),
            ('Many thanks to our testers', ['Kathrin, Kuba, David, Doro, Andreas']),
        ])

    def back(self):
        sys.exit()


class NewGameMode(ChoiceMode):
    prompt = 'new game #'
    levels = None
    choices = None
    title = 'Select level'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.levels = levels.get()
        self.choices = self.levels

    def exec_choice(self, choice):
        levels.init_level(self.levels[choice])
        self.print_header()
        print_title(levels.get_name())
        print_text(levels.get_intro())
        print_newline()
        print_title('Goals')
        print_list(goals.get_texts(), double_columns=False)
        print_text('(Note: your progress is automatically saved once per day in the game. '
                   'There is one savegame file per level and diner. '
                   'If you have already played this level, choose a different diner name this '
                   'time to avoid overwriting the other savegame.)'
                   )
        print_newline()
        print_text('Diner name (default: {}): '.format(diner.diner.name))
        diner_name = input('')
        if diner_name:
            diner.diner.name = diner_name
        print_text('Your name: ')
        chef_name = input('')
        if chef_name:
            diner.diner.chef = 'Chef {}'.format(chef_name)
        return FirstHelpMode()

    def back(self):
        return StartMode()


class SaveGameMode(ChoiceMode):
    prompt = 'save #'
    saved_games = None
    choices = None
    title = 'Select slot'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_games = save_module.saved_games()
        self.choices = []
        for slot in range(1, 9):
            file = self.saved_games.get(slot)
            if file:
                self.choices.append(file)
            else:
                self.choices.append('<empty>')

    def exec_choice(self, choice):
        save_module.save_game(choice)
        return DinerMode()


class LoadGameMode(ChoiceMode):
    prompt = 'load #'
    choices = None
    title = 'Select saved game'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = save_module.saved_games().values()

    def exec_choice(self, choice):
        save_module.load_game(choice + 1)
        return DinerMode()


class FirstHelpMode(InfoMode):

    def print_info(self):
        title = 'Welcome to your new diner, {}!'.format(diner.diner.chef)
        print_title(title)
        print_newline()
        print_text(
            'How to play? Use auto-complete: type the first letters of a command and press TAB. Type \'help\' to '
            'display a list of available commands. During your first day, you will receive gameplay hints. '
            'We recommend to set the terminal size to 100x40.'
        )
        print_newline()
        print_text(
            'What to do first? Take your guests\' orders in the diner, prepare food in the kitchen, and serve it. '
        )
        print_newline()
        print_text(
            'Heads up: your guests have specific dietary restrictions and preferences that you will discover during '
            'the game. Make the guests happy, and they will repay you in space dollars and positive reviews!'
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
    CMD_LOOK_UP = 5
    CMD_CLOSE_UP = 6
    CMD_EXIT = 7
    commands = [
        ('go to kitchen',),
        ('take order from', []),
        ('chat with', []),
        ('serve', [], 'to', []),
        ('dismiss', []),
        ('look up', ['recipes', 'guests', 'ingredients', 'menu', 'today\'s reviews', 'goals']),
        ('close up',),
        ('exit',),
    ]
    prompt = 'diner >>'
    hint = (
        'In the dining room, you can take orders, chat with your guests, and look up information (e.g., about your '
        'guests or your progress in the game). Type "help" to see all available commands.'
    )
    dont_truncate_cmd_help = [CMD_LOOK_UP]

    def update_commands(self):
        cooked_food = food.plated()
        available_guests = guests.get_guests()
        guests_with_chats = guests.guests_with_chats()
        guests_with_orders = guests.guests_with_orders()
        guests_without_orders = guests.guests_without_orders()
        self.commands[self.CMD_TAKE_ORDER] = ('take order from', guests_without_orders) # FIXME: dont reinit, just set arg EVERYWHERE
        self.commands[self.CMD_CHAT] = ('chat with', guests_with_chats)
        self.commands[self.CMD_SERVE] = ('serve', cooked_food, 'to', guests_with_orders)
        self.commands[self.CMD_SEND_HOME] = ('dismiss', available_guests)
        super().update_commands()

    def print_header(self):
        available_guests = guests.get_guests()
        decoration = [', '.join(diner.diner.available_decoration)] if diner.diner.available_decoration else '-'
        print_header([
            ('Location', [diner.diner.name, '(dining room)']),
            ('Time', [time.now()]),
            ('Money', [levels.get_money(), 'space dollars']),
            ('Seats taken', ['{}/{}'.format(len(available_guests), diner.diner.seats)]),
            ('Sanitation', ['{}/5'.format(diner.diner.sanitation)]),
            ('Interior decoration', decoration),
        ])

    def print_info(self):
        available_guests = guests.get_guests()
        print_title('Food:')
        print_list(food.plated())
        print_title('Guests:')
        names_with_info = []
        for guest_name in available_guests:
            guest = guests.get(guest_name)
            if guest.is_regular:
                group = 'regular, {}'.format(guest.group) if guest.group else 'regular'
            else:
                group = guest.group
            info = ''
            if guest.order:
                info = ', order: {}'.format(guest.order.wish)
            names_with_info.append('{} ({}){}'.format(guest.name, group, info))
        print_list(names_with_info, double_columns=False)

    @staticmethod
    def exec_look_up(back, arg):
        if arg == 'menu':
            return DinerMenuMode(back=back)
        if arg == 'recipes':
            return RecipeMode(back=back)
        if arg == 'today\'s reviews':
            return ReviewsInfoMode(back=back)
        if arg == 'guests':
            return GuestInfoMode(back=back)
        if arg == 'ingredients':
            return IngredientInfoMode(back=back)
        if arg == 'goals':
            return GoalsInfoMode(back=back)

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
            self.update_commands()
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
            self.update_commands()
            return self
        if cmd == self.CMD_SEND_HOME:
            guest = cmd_input[1]
            guests.send_home(guest)
            print_text('{} left.'.format(guest))
            self.wait_for_input()
            self.update_commands()
            return self
        if cmd == self.CMD_LOOK_UP:
            return self.exec_look_up(self, cmd_input[-1])
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
        if cmd == self.CMD_EXIT:
            save_module.autosave_save()
            return StartMode()


class DinerMenuMode(InfoMode):

    def print_info(self):
        print_text('This is the current menu from which your guests can select items. At the beginning of each new '
                   'week, you get the chance to change your menu.')
        print_newline()
        print_title('{} menu'.format(diner.diner.name))
        print_list(food.get_menu())


class KitchenMode(Mode):
    CMD_DINER = 0
    CMD_COOK = 1
    CMD_TRASH = 2
    CMD_LOOK_UP = 3
    CMD_SAVE_RECIPE = 4
    commands = [
        ('go to diner',),
        ([], [],),
        ('trash prepared ingredients',),
        ('look up', ['recipes', 'guests', 'ingredients', 'menu', 'today\'s reviews', 'goals']),
        ('save recipe', []),
    ]
    prompt = 'kitchen >>'
    orders = None
    available_ingredients = None
    available_devices = None
    hint = (
        'In the kitchen, you prepare the food. Each dish consists of three ingredients (the order does not matter). '
        'You can follow existing recipes or create your own. Try to match your guests\' orders.'
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
        cooked_ingredients = food.cooked_ingredients()
        print_list(cooked_ingredients + ['']*(3-len(cooked_ingredients)), double_columns=False)
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
        if cmd == self.CMD_TRASH:
            cooked_ingredients = food.cooked_ingredients()
            if cooked_ingredients:
                print_message('throw away {}'.format(', '.join(cooked_ingredients)))
            food.trash()
            self.update_commands()
            return self
        if cmd == self.CMD_LOOK_UP:
            return DinerMode.exec_look_up(self, cmd_input[-1])
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
        print_newline()
        print('Ingredients:')
        ingredient_list = [', '.join(properties) for properties in recipe.ingredient_properties]
        print_list(ingredient_list, double_columns=False)
        print('Properties of the dish: {}'.format(', '.join(recipe.all_properties())))

    def print_info(self):
        print_text('This is a list of available recipes. You can also add your own recipes to this collection: '
                   'after completing a new dish, you can save the recipe.')
        print_newline()
        super().print_info()

    def exec_choice(self, choice):
        recipe = food.get_recipe(self.choices[choice])
        self._print_recipe(recipe)
        self.wait_for_input()
        return self


class SaveRecipeMode(ChoiceMode):
    prompt = 'menu #'
    choices = ["Quick-save the recipe", "Advanced recipe maker"]
    title = 'How would you like to save your recipe?'
    dish = None

    def print_info(self):
        print_text(
            'You can save your dish as a new recipe. Use quick-save to quickly note down the preparation of the '
            'ingredients - then only exact replications of your dish will be considered as instances of the recipe. '
            'Use the advanced recipe maker to create more flexible recipes.'
        )
        print_newline()
        super().print_info()

    def __init__(self, dish, **kwargs):
        self.dish = food.get(dish)
        super().__init__(**kwargs)

    def exec_choice(self, choice):
        if choice == 0:
            print_title('Recipe:')
            self.print_recipe(self.dish.all_ingredient_properties())
            name = None
            while not name:
                name = input('Recipe name: ')
            food.save_as_recipe(name, self.dish.all_ingredient_properties())
            self.back_mode.update_commands()
            return self.back_mode
        elif choice == 1:
            return AdvancedSaveRecipeMode(self.dish, back=self.back_mode)

    @staticmethod
    def print_recipe(ingredient_properties_list):
        print_list(
            [', '.join(ingredient_properties) for ingredient_properties in ingredient_properties_list],
            double_columns=False
        )

class AdvancedSaveRecipeMode(ChoiceMode):
    choices = None
    prompt = 'Add property:'
    back_label = 'Done'

    ingredient = 0
    dish = None
    ingredient_properties = None
    ingredient_property_choices = None

    @property
    def title(self):
        return 'Choose which properties of ingredient {} will be part of the recipe'.format(self.ingredient + 1)

    def __init__(self, dish, **kwargs):
        self.dish = dish
        self.ingredient_property_choices = [[], [], []]
        self.choices = self.dish.ingredient_properties(self.ingredient)
        super().__init__(**kwargs)

    def print_info(self):
        print_text(
            'For each component, you can choose the crucial properties that need to '
            'be met. For example, if the first ingredient is grilled beef, you can decide whether '
            'the recipe requires the exact same preparation (then select two properties: "grilled" and "beef"), '
            'or any kind of beef is ok (select the property: "beef"), or even any kind of meat goes ("meat"). '
            'Then, select the required properties of the second and third component in the same manner.'
        )
        print_newline()
        print_title('Prepared dish:')
        SaveRecipeMode.print_recipe(self.dish.all_ingredient_properties())
        print_title('Recipe draft:')
        SaveRecipeMode.print_recipe(self.ingredient_property_choices)
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
            cls()
            print_title('Recipe:')
            SaveRecipeMode.print_recipe(self.ingredient_property_choices)
            name = None
            while not name:
                name = input('Recipe name: ')
            food.save_as_recipe(name, self.ingredient_property_choices)
            print_message('saved {}.'.format(name))
            return super().back()


class GuestInfoMode(ChoiceMode):
    prompt = 'guest #'
    choices = None
    title = 'Guest infos'

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


class IngredientInfoMode(ChoiceMode):
    prompt = 'ingredient #'
    choices = None
    title = 'Ingredient infos'

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


class GoalsInfoMode(InfoMode):

    def print_info(self):
        print_title('Goals')
        print_list(goals.get_progresses(), double_columns=False)


class ReviewsInfoMode(InfoMode):
    hint = (
        'The daily reviews provide pointers for ways to improve your food and your diner. Pay attention to the '
        'general preferences (+) and aversions (-) of your target groups and the individual taste of your regulars - '
        'you might be able to elevate their orders with something they like.'
    )

    def _rating_info(self, name, count, rating):
        if count == 0:
            if settings.text_only():
                return '(N/A) - {} - no reviews yet'.format(name)
            else:
                return '[-----] (N/A) - {} - no reviews yet'.format(name)
        else:
            if settings.text_only():
                return '({:0.1f}) - {} - based on {} review(s)'.format(
                float(rating),
                name,
                count,
                )
            else:
                n_stars = round(rating)
                return '[{}{}] ({:0.1f}) - {} - based on {} review(s)'.format(
                    '*' * n_stars,
                    '-' * (5 - n_stars),
                    float(rating),
                    name,
                    count,
                    )

#    def print_header(self):
#        print_header([
#            ('Location', [diner.diner.name, '(office)']),
#            ('Time', [time.now()]),
#        ])

    def print_info(self):
        print_text('You read today\'s reviews.')
        print_newline()
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
        'Evening activities can advance your social relationships: on some days, your regular customers '
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
        if settings.text_only():
            line = '{}/{} - {}'.format(level, skills.MAX_SKILL_LEVEL, name)
        else:
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
        if self.meetings:
            print_newline()
            print_text('You have been invited to a social event!')
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
        print_newline()
        print_dialog(self.guest, self.meeting.question)
        print_newline()
        super().print_info()

    def exec_choice(self, choice):
        reply = choice
        social.meet(self.guest, reply)
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

    def print_info(self):
        print_text('It\'s the beginning of a new week! You have the chance to edit what is on the menu. Would '
                   'you like to replace anything?')
        print_newline()
        super().print_info()

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
        'for crowded days at the diner. New merchants might become available during the game.'
    )
    merchants = None
    available_ingredients = None
    back_label = 'Leave market'

    def update_commands(self):
        self.available_ingredients = storage.available_ingredients()
        self.merchants = {
            '{} ({})'.format(merchant, ', '.join(merchant_ingredients)): merchant
            for merchant, merchant_ingredients in shopping.for_sale().items()
        }
        self.choices = list(self.merchants.keys())
        super().update_commands()

    def print_header(self):
        print_header([
            ('Location', [shopping.market.name]),
            ('Time', [time.now()]),
            ('Money', [levels.get_money(), 'space dollars']),
        ])

    def print_info(self):
        if shopping.market.description:
            print_text(shopping.market.description)
            print_newline()
        print_title('Ingredients in stock in the diner:')
        print_list(['{} x {}'.format(a, i) for i, a in self.available_ingredients.items()])
        super().print_info()

    def exec_choice(self, choice):
        merchant = self.merchants[self.choices[choice]]
        merchant_mode = MerchantMode(merchant)
        merchant_description = shopping.get(merchant).description
        if merchant_description:
            print_text(merchant_description)
        print_newline()
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
    CMD_BUY_EACH = 1
    CMD_DONE = 2
    commands = [
        ('buy', int, []),
        ('buy', int, 'each'),
        ('done',),
    ]
    prompt = 'shopping >>'
    merchant = None
    available_ingredients = None
    ingredients_for_sale = None
    hint = (
        'You can buy individual ingredients (e.g., "buy 5 potato") or stock up on everything the merchant '
        'offers ("buy 5 each"). Type "done" to leave.'
        )

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
            ('Money', [levels.get_money(), 'space dollars']),
        ])

    def print_info(self):
        print_title('Ingredients for sale:')
        print_list([
            '{}: {} space dollars, {} in stock, {} required'.format(ingredient, cost, amount, stock)
            for ingredient,  (amount, cost, stock) in self.ingredients_for_sale.items()
        ])
        print_title('Ingredients in stock in the diner:')
        print_list(['{} x {}'.format(a, i) for i, a in self.available_ingredients.items()])
        print_newline()
        print_text('Type "done" to leave this merchant and get back to the market.')
        print_newline()

    def _can_buy(self, merchant, amount, ingredient):
        cost = 0
        error = None
        ingredients = [ingredient] if ingredient else list(self.ingredients_for_sale.keys())
        for ingredient in ingredients:
            if not merchant.is_ingredient_available(ingredient, amount):
                error = 'Not enough ingredients'
            cost += merchant.cost(ingredient) * amount
        if cost > levels.get_money():
            error = 'Not enough money'
        if error:
            cost = 0
            print_message('Could not buy ingredients: {}'.format(error))
            self.wait_for_input()
        return cost

    def exec(self, cmd, cmd_input):
        merchant = shopping.get(self.merchant)
        if cmd == self.CMD_BUY_INGREDIENT:
            amount = int(cmd_input[1])
            ingredient = cmd_input[2]
            cost = self._can_buy(merchant, amount, ingredient)
            if cost:
                levels.add_money(-cost)
                merchant.buy(ingredient, amount)
                storage.store_ingredient(ingredient, amount)
                self.update_commands()
            return self
        if cmd == self.CMD_BUY_EACH:
            amount = int(cmd_input[1])
            cost = self._can_buy(merchant, amount, None)
            if cost:
                levels.add_money(-cost)
                for ingredient in self.ingredients_for_sale.keys():
                    merchant.buy(ingredient, amount)
                    storage.store_ingredient(ingredient, amount)
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
    mode = LogoMode()
    while True:
        try:
            mode.print_header()
            mode.print_info()
            if time.calendar.is_first_day:
                mode.print_hint()
            mode.print_tutorial()
            prompt = '{} '.format(mode.get_prompt()) if mode.get_prompt() else ''
            cmd = input('{} '.format(prompt))
            print_newline()
            next_mode = mode.parse(cmd)
            if next_mode:
                mode = next_mode
        except (KeyboardInterrupt, EOFError):
            try:
                print_newline()
                yes = input('Exit game? (y/N) ')
                if yes in ['y', 'Y']:
                    if logfile:
                        logfile.close()
                    sys.exit()
            except (KeyboardInterrupt, EOFError):
                print_newline()
                if logfile:
                    logfile.close()
                sys.exit()


def init():
    pass