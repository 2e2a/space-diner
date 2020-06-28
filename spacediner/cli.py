import re
import readline

from . import actions
from . import activities
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


def print_text(str):
    # TODO: capitalize just the first letter.
    print(str)


def print_title(str):
    print(str)
    print('-' * (len(str)))


def print_list(list):
    if list:
        for e in list:
            print('- {}'.format(e))
    else:
        print('-')
    print('')


def print_header(header_values):
    print_text('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for name, values in header_values:
        print_value(name, *values)
    print_text('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
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
            if not cmd:
                continue
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
        return self.commands.index(command)

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
                self.matches = suggestions
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
                    if isinstance(words, list):
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

    def parse(self, cmd_input):
        if cmd_input and self.commands:
            cmd_input_list = cmd_input.split()
            matching_command = self.completer.match_command(cmd_input_list)
            if matching_command is not None:
                return self.exec(matching_command, cmd_input_list)
        elif self.empty_input:
            return self.exec(None, None)
        self.print_help()
        return None

    def name_for_command(self, name):
        cmd_name = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower(), count=16)
        cmd_name = cmd_name.strip('_')
        self.names.update({cmd_name: name})
        return cmd_name

    def original_name(self, cmd_name):
        return self.names.get(cmd_name)


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
        print_list(choice_info)

    def print_help(self):
        print_text('Select a number.')

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_CHOICE:
            choice = int(cmd_input[0])
            if choice < 0 or choice > len(self.choices):
                print_message('Invalid choice.')
                return self
            if self.back_enabled and choice == 0:
                return self.back()
            return self.exec_choice(choice - 1)


class InfoMode(Mode):
    prompt = '<press ENTER to continue>'
    empty_input = True

    def exec(self, cmd, cmd_input):
        print_newline()
        return self.back()


class WaitForInputMode(InfoMode):
    pass


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.levels = levels.list()
        self.choices = self.levels

    def exec_choice(self, choice):
        levels.init(self.levels[choice])
        diner_name = input('Diner name (default: {}): '.format(diner.diner.name))
        if diner_name:
            diner.diner.name = diner_name
        chef_name = input('Your name: ')
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
        print_text('')
        title = 'Welcome to your new diner, {}!'.format(diner.diner.chef)
        print_title(title)
        print_text(
            'How to play? Use auto-complete: type the first letters of a command and press TAB. Type \'help\' to '
            'display a list of available commands. During your first day, you will receive general gameplay hints.\n'
            'What to do first? Take your guests\' orders in the diner, prepare food in the kitchen, and serve it.\n'
            'Heads up: your guests have specific dietary restrictions and preferences. '
            'Make them happy, and they will repay you in space dollars and positive reviews!\n'
        )

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
    CMD_COMPENDIUM = 6
    CMD_CLOSE_UP = 7
    CMD_SAVE = 8
    CMD_EXIT = 9
    commands = [
        (['kitchen'],),
        (['take_order_from'], []),
        (['chat_with'], []),
        (['serve'], [], ['to'], []),
        (['send_home'], []),
        (['menu'],),
        (['compendium'],),
        (['close_up'],),
        (['save'],),
        (['exit'],),
    ]
    prompt = 'diner >>'
    hint = (
        'In the dining room, you can chat with your guests, take their orders, and serve them food. '
        'For preparing food, go to the kitchen. When all the guests are gone, close up the diner - '
        'new guests will come tomorrow.'
    )

    def update_commands(self):
        cooked_food = [self.name_for_command(f) for f in food.plated()]
        available_guests = [self.name_for_command(g) for g in guests.available_guests()]
        guests_with_chats = [self.name_for_command(g) for g in guests.guests_with_chats()]
        guests_with_orders = [self.name_for_command(g) for g in guests.guests_with_orders()]
        guests_without_orders = [self.name_for_command(g) for g in guests.guests_without_orders()]
        self.commands[self.CMD_TAKE_ORDER] = (['take_order_from'], guests_without_orders)
        self.commands[self.CMD_CHAT] = (['chat_with'], guests_with_chats)
        self.commands[self.CMD_SERVE] = (['serve'], cooked_food, ['to'], guests_with_orders)
        self.commands[self.CMD_SEND_HOME] = (['send_home'], available_guests)
        super().update_commands()

    def print_info(self):
        available_guests = guests.available_guests()
        print_header([
            ('Location', [diner.diner.name, '(dining room)']),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
            ('Seats taken', ['{}/{}'.format(len(available_guests), diner.diner.seats)]),
            ('Sanitation', ['{}/5'.format(diner.diner.sanitation)]),
        ])
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
            guest = self.original_name(cmd_input[1])
            action = actions.TakeOrder(guest)
            action.perform()
            return WaitForInputMode(back=self)
        if cmd == self.CMD_CHAT:
            guest = self.original_name(cmd_input[1])
            action = actions.GuestChat(guest)
            action.perform()
            return WaitForInputMode(back=self)
        if cmd == self.CMD_SERVE:
            food = self.original_name(cmd_input[1])
            guest = self.original_name(cmd_input[3])
            action = actions.Serve(food, guest)
            action.perform()
            return WaitForInputMode(back=self)
        if cmd == self.CMD_SEND_HOME:
            guest = self.original_name(cmd_input[1])
            action = actions.SendHome(guest)
            action.perform()
            return WaitForInputMode(back=self)
        if cmd == self.CMD_MENU:
            return DinerMenuMode(back=self)
        if cmd == self.CMD_COMPENDIUM:
            return CompendiumMode(back=self)
        if cmd == self.CMD_CLOSE_UP:
            global actions_saved
            for action in actions_saved:
                action.abort()
            actions_saved.clear()
            actions.CloseUp().perform()
            time.tick()
            return ReviewsInfoMode()
        if cmd == self.CMD_SAVE:
            return SaveGameMode(back=self)
        if cmd == self.CMD_EXIT:
            levels.autosave_save()
            return StartMode()


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
        (['diner'],),
        (['cook'], [],),
        (['compendium'],),
        (['trash'],),
        (['recipes'],),
        (['save_recipe'],),
    ]
    prompt = 'kitchen >>'
    action = None
    orders = None
    available_ingredients = None
    available_devices = None
    prepared_components = None
    hint = (
        'You can follow the available recipes or create your own dishes. Every dish consists of three ingredients. '
        'Once you have prepared them, they will be automatically plated as a completed dish.'
    )

    def __init__(self, **kwargs):
        global actions_saved
        self.orders = guests.ordered()
        self.available_ingredients = storage.available_ingredients()
        self.available_devices = kitchen.available_devices()
        self.prepared_components = []
        if len(actions_saved) == 0:
            self.action = actions.Cook()
        else:
            self.action = actions_saved[0]
            del actions_saved[0]
            for preparation, ingredient in self.action.food.ingredients:
                self.prepared_components.append('{} {}'.format(preparation, ingredient))
        super().__init__(**kwargs)

    def update_commands(self):
        ingredients = []
        for ingredient, available in self.available_ingredients.items():
            if available: ingredients.append(self.name_for_command(ingredient))
        preparations = [d.command for d in self.available_devices.values()]
        self.commands[self.CMD_COOK] = (preparations, ingredients)
        recipe_choices = [self.name_for_command(dish) for dish in food.plated()]
        self.commands[self.CMD_SAVE_RECIPE] = (['save_recipe'], recipe_choices)
        super().update_commands()

    def print_info(self):
        print_title('Orders:')
        print_list(['{}: {}'.format(g, o) for g, o in self.orders.items()])
        print_title('Available ingredients:')
        print_list(['{} x {}'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Kitchen:')
        print_list(['{} for {}'.format(d.name, d.preparation) for d in self.available_devices.values()])
        print_title('Prepared:')
        print_list(self.prepared_components)
        print_title('Plated:')
        print_list(list(food.plated()))

    def _get_device(self, preparation_command):
        for device in self.available_devices.values():
            if device.command == preparation_command:
                return device
        return None

    def exec(self, cmd, cmd_input):
        global actions_saved
        if cmd == self.CMD_DINER:
            actions_saved.append(self.action)
            return self.back()
        if cmd == self.CMD_COOK:
            preparation_command = cmd_input[0]
            device = self._get_device(preparation_command)
            ingredient = self.original_name(cmd_input[1])
            self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient) - 1})
            self.action.add_ingredients([(device.result, ingredient)])
            self.prepared_components.append('{} {}'.format(device.result, ingredient))
            if len(self.prepared_components) == 3:
                self.action.perform()
                print_message('Plated {}'.format(self.action.food.name))
                self.action = actions.Cook()
                self.prepared_components = []
            self.update_commands()
            return self
        if cmd == self.CMD_COMPENDIUM:
            return CompendiumMode(back=self)
        if cmd == self.CMD_TRASH:
            self.action.abort()
            self.prepared_components = []
            # TODO: trash action
            return self
        if cmd == self.CMD_RECIPES:
            actions_saved.append(self.action)
            return RecipeMode(back=self)
        if cmd == self.CMD_SAVE_RECIPE:
            actions_saved.append(self.action)
            dish = self.original_name(cmd_input[1])
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
        ingredient_list = [' '.join(properties) for properties in recipe.ingredient_properties]
        print_list(ingredient_list)
        if recipe.properties:
            properties = filter(lambda p: p != recipe.name.lower(), recipe.properties)
            print_value('Properties of the dish', ', '.join(properties))
            print_newline()

    def exec_choice(self, choice):
        recipe = food.get_recipe(self.choices[choice])
        self._print_recipe(recipe)
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
            self.action = actions.SaveRecipe(name, self.ingredient_property_choices)
            self.action.perform()
            print_message('saved {}.'.format(name))
            return super().back()


class CookingBotMode(ChoiceMode):
    prompt = 'cooking bot #'
    choices = ['Cook saved dish', 'Save plated dish', 'View saved dishes']
    title = 'Input'

    def __init__(self):
        super().__init__()
        print_dialog('KiBo3000', 'bleep ... blup ...')

    def exec_choice(self, choice):
        if choice == 1:
            return CookingBotCookMode()
        elif choice == 3:
            return CookingBotListMode()
        return self


class CookingBotCookMode(ChoiceMode):
    prompt = 'cooking bot #'
    choices = None
    title = 'Select dish'

    def __init__(self):
        print_dialog('KiBo3000', 'bleep ... blup ...')
        self.choices = food.get_dishes()
        super().__init__()

    def exec_choice(self, choice):
        dish = self.choices[choice]
        dish_recipe = food.get_dish(dish)
        if dish_recipe.can_be_cooked():
            self.action = actions.Cook(dish_recipe.ingredient_properties)
            self.action.perform()
            print_dialog('KiBo3000', 'Cooking {}...'.format(dish))
        else:
            print_dialog('KiBo3000', 'Not enough ingredients or equipment not available anymore.')
        return CookingBotMode()

    def back(self):
        return CookingBotMode()


class CookingBotListMode(RecipeMode):
    prompt = 'cooking bot #'
    title = 'Dish'

    def __init__(self):
        self.recipes = food.get_dishes()
        self.choices = self.recipes
        super().__init__()

    def exec_choice(self, choice):
        recipe = food.get_dish(self.recipes[choice])
        self._print_recipe(recipe)
        return self

    def back(self):
        return CookingBotMode()


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
        print_newline()
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
        else:
            print_text('Unknown.')
        print_newline()
        return self


class ReviewsInfoMode(InfoMode):
    hint = (
        'The daily reviews provide pointers for ways to improve your food and your diner. Pay attention to the '
        'general preferences (+) and aversions (-) of your target groups and the individual taste of your regulars - '
        'you might be able to elevate their orders with something they like.'
    )

    def back(self):
        return ActivityMode()

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

    def print_info(self):
        print_header([
            ('Location', [diner.diner.name, '(office)']),
            ('Time', [time.now()]),
        ])
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
                guest_like += ','.join(map(lambda x: '+' + x, likes))
            if dislikes:
                guest_like += ','.join(map(lambda x: '-' + x, dislikes))
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

    def print_info(self):
        print_header([
            ('Location', [diner.diner.name, '(outside)']),
            ('Time', [time.now()]),
        ])
        print_text('Now you have time for one evening activity.')
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
            action = actions.DoActivity(activity)
            action.perform()
            self.print_skills()
        else:
            choice -= (len(self.meetings) + len(self.activities))
            if self.fixed_activities[choice] == 'clean diner':
                action = actions.CleanDiner()
                action.perform()
        return WaitForInputMode(back=SleepMode())


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
        super().print_info()

    def exec_choice(self, choice):
        reply = choice
        action = actions.Meet(self.guest, reply)
        action.perform()
        return WaitForInputMode(back=SleepMode())


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
        action = actions.UpdateMenu(self.item, self.choices[choice])
        action.perform()
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

    def print_info(self):
        print_header([
            ('Location', [shopping.market.name]),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
        ])
        if shopping.market.description:
            print_text(shopping.market.description)
        print_title('Merchants available today')
        print_list([
            '{} [{}]'.format(merchant, ', '.join(merchant_ingredients))
            for merchant, merchant_ingredients in self.ingredients_for_sale.items()
        ])
        super().print_info()

    def exec_choice(self, choice):
        merchant_name = self.choices[choice]
        merchant_mode = MerchantMode(merchant_name)
        merchant_description = shopping.get(merchant_name).description
        if merchant_description:
            print_text(merchant_description)
        if shopping.has_chat_available(merchant_name):
            action = actions.MerchantChat(merchant_name)
            action.perform()
            return WaitForInputMode(back=merchant_mode)
        return merchant_mode

    def back(self):
        time.tick()
        return DinerMode()


class MerchantMode(Mode):
    CMD_BUY_INGREDIENT = 0
    CMD_DONE = 1
    commands = [
        (['buy'], int, []),
        (['done'],),
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
        ingredient_names = [self.name_for_command(ingredient) for ingredient in self.ingredients_for_sale.keys()]
        self.commands[self.CMD_BUY_INGREDIENT] = (['buy'], int, ingredient_names)
        super().update_commands()

    def print_info(self):
        print_header([
            ('Location', [shopping.market.name, ' - ', self.merchant]),
            ('Time', [time.now()]),
            ('Money', [levels.level.money, 'space dollars']),
        ])
        print_title('Owned ingredients:')
        print_list(['{} x {}'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Ingredients for sale:')
        print_list([
            '{}: {} space dollars, {} in stock, {} required'.format(ingredient, cost, amount, stock)
            for ingredient,  (amount, cost, stock) in self.ingredients_for_sale.items()
        ])

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_BUY_INGREDIENT:
            amount = int(cmd_input[1])
            ingredient = self.original_name(cmd_input[2])
            action = actions.BuyIngredients(self.merchant, ingredient, amount)
            action.perform()
            self.update_commands()
            return self
        if cmd == self.CMD_DONE:
            return ShoppingMode()


mode = None
actions_saved = []


def run():
    global mode
    mode = StartMode()
    print_info = True
    print('################################  SPACE  DINER  ################################')
    while True:
        try:
            if print_info:
                mode.print_info()
                if time.calendar.is_first_day:
                    mode.print_hint()
            prompt = '{} '.format(mode.prompt) if mode.prompt else ''
            cmd = input('{} '.format(prompt))
            print_newline()
            next_mode = mode.parse(cmd)
            if next_mode:
                mode = next_mode
                print_info = True
            else:
                print_info = False
        except (KeyboardInterrupt, EOFError):
            try:
                print_newline()
                yes = input('Save and exit game? (y/N)')
                if yes in ['y', 'Y']:
                    levels.autosave_save()
                    exit()
            except (KeyboardInterrupt, EOFError):
                print_newline()
                exit()


def init():
    pass
