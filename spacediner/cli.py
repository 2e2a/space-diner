import re
import readline

from . import actions
from . import activities
from . import diner
from . import food
from . import guests
from . import kitchen
from . import merchants
from . import levels
from . import ingredients
from . import reviews
from . import settings
from . import skills
from . import social
from . import storage
from . import time


def print_text(str):
    # TODO: capitalize just the first letter.
    print(str)


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


def print_message(msg):
    print('*** {} ***'.format(msg))


def print_dialog(name, msg):
    print('{}: "{}"'.format(name, msg))


def print_dialog_with_info(name, info, msg):
    print('{} {}: "{}"'.format(name, info, msg))


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
    empty_input = False
    no_input = False

    def __init__(self):
        self.update_commands()

    def update_commands(self):
        if not self.no_input:
            self.completer = CommandCompleter(self.commands)

    def print_info(self):
        print('')

    def print_help(self):
        # TODO: add simple help
        raise NotImplemented()

    def exec(self, cmd, cmd_input):
        raise NotImplemented()

    def parse(self, cmd_input):
        if cmd_input:
            cmd_input_list = cmd_input.split()
            matching_command = self.completer.match_command(cmd_input_list)
            if matching_command:
               return self.exec(matching_command, cmd_input_list)
        elif self.empty_input:
            return self.exec(None, None)
        self.print_help()
        return None

    def name_for_command(self, name):
        cmd_name = re.sub(r'[^a-zA-Z0-9]+','_',name.lower(), count=16)
        cmd_name = cmd_name.strip('_')
        self.names.update({cmd_name: name})
        return cmd_name

    def original_name(self, cmd_name):
        return self.names.get(cmd_name)


class ChoiceMode(Mode):
    CMD_CHOICE = 1
    commands = [
        (int,),
    ]
    choices = []
    back_enabled = True
    back_label = 'Back'
    title = None

    def exec_choice(self, choice):
        raise  NotImplemented

    def back(self):
        raise NotImplemented

    def print_info(self):
        super().print_info()
        if self.title:
            print_title(self.title)
        choice_info = ['{}: {}'.format(i, choice) for i, choice in enumerate(self.choices, 1)]
        if self.back_enabled:
            choice_info += ['0: {}'.format(self.back_label)]
        print_list(choice_info)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_CHOICE:
            choice = int(cmd_input[0])
            if choice < 0 or choice > len(self.choices):
                print('Invalid choice.')
                return self
            if self.back_enabled and choice == 0:
                return self.back()
            return self.exec_choice(choice)


class InfoMode(Mode):
    prompt = '<press ENTER to continue>'
    empty_input = True

    def print_help(self):
        print('Help:')
        print(self.commands)

    def back(self):
        raise NotImplemented

    def exec(self, cmd, cmd_input):
        return self.back()


class MenuMode(ChoiceMode):
    prompt = 'menu #'
    choices = ['Continue', 'New game', 'Load game']
    back_label = 'Exit'
    title = 'Menu'

    def exec_choice(self, choice):
        if choice == 1:
            levels.autosave_load()
            print_value('Level', levels.level.name)
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
    choices = None
    title = 'Select level'

    def __init__(self):
        super().__init__()
        self.levels = levels.list()
        self.choices = self.levels

    def exec_choice(self, choice):
        levels.init(self.levels[choice - 1])
        diner_name = input('Diner name (default: {}): '.format(diner.diner.name))
        if diner_name:
            diner.diner.name = diner_name
        time.tick()
        return DinerMode()

    def back(self):
        return MenuMode()


class SaveGameMode(ChoiceMode):
    prompt = 'save #'
    saved_games = None
    choices = None
    title = 'Select slot'

    def __init__(self):
        super().__init__()
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

    def back(self):
        return DinerMode()


class LoadGameMode(ChoiceMode):
    prompt = 'load #'
    choices = None
    title = 'Select saved game'

    def __init__(self):
        super().__init__()
        self.saved_games = levels.saved_games()
        self.choices = self.saved_games.items()

    def exec_choice(self, choice):
        levels.load_game(choice)
        print_value('Level', levels.level.name)
        return DinerMode()

    def back(self):
        return MenuMode()


class DinerMode(Mode):
    CMD_COOKING = 1
    CMD_SERVICE = 2
    CMD_SKILLS = 3
    CMD_COMPENDIUM = 4
    CMD_CLOSE_UP = 5
    CMD_SAVE = 6
    CMD_EXIT = 7
    commands = [
        (['cooking'],),
        (['service'],),
        (['skills'],),
        (['compendium'],),
        (['close_up'],),
        (['save'],),
        (['exit'],),
    ]
    prompt = 'diner >>'

    def print_info(self):
        super().print_info()
        print_text('--------------------------------')
        print_value('Diner', diner.diner.name)
        print_value('Day', time.now())
        print_value('Money', levels.level.money, 'space dollars')
        print_text('--------------------------------')

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_COOKING:
            return CookingMode()
        if cmd == self.CMD_SERVICE:
            return ServiceMode()
        if cmd == self.CMD_SKILLS:
            return SkillInfoMode()
        if cmd == self.CMD_COMPENDIUM:
            return CompendiumMode()
        if cmd == self.CMD_CLOSE_UP:
            global actions_saved
            for action in actions_saved:
                action.abort()
            actions_saved.clear()
            actions.CloseUp().perform()
            time.tick()
            return AfterWorkMode()
        if cmd == self.CMD_SAVE:
            return SaveGameMode()
        if cmd == self.CMD_EXIT:
            levels.autosave_save()
            return MenuMode()


class SkillInfoMode(InfoMode):

    def back(self):
        return DinerMode()

    def print_skill(self, skill, value):
        progress = '#'*int(value) + '-'*(10 - int(value))
        line = '[{}] {}/10 - {}'.format(progress, value, skill)
        return line

    def print_info(self):
        super().print_info()
        print_title('Skills')
        skill_values = [self.print_skill(skill, value) for skill, value in skills.get().items()]
        print_list(skill_values)


class ServiceMode(Mode):
    CMD_TAKE_ORDER = 1
    CMD_CHAT = 2
    CMD_SERVE = 3
    CMD_SEND_HOME = 4
    CMD_COOKING = 5
    CMD_DONE = 6
    commands = [
        (['chat_with'], []),
        (['take_order_from'], []),
        (['serve'], [], ['to'], []),
        (['send_home'], []),
        (['cooking'], ),
        (['done'], ),
    ]
    prompt = 'service >>'

    def update_commands(self):
        cooked_food = [self.name_for_command(f) for f in food.plated()]
        available_guests = [self.name_for_command(g) for g in guests.available_guests()]
        guests_with_chats = [self.name_for_command(g) for g in guests.guests_with_chats()]
        guests_with_orders = [self.name_for_command(g) for g in guests.guests_with_orders()]
        guests_without_orders = [self.name_for_command(g) for g in guests.guests_without_orders()]
        self.commands[self.CMD_TAKE_ORDER - 1] = (['take_order_from'], guests_without_orders)
        self.commands[self.CMD_CHAT - 1] = (['chat_with'], guests_with_chats)
        self.commands[self.CMD_SERVE - 1] = (['serve'], cooked_food, ['to'], guests_with_orders)
        self.commands[self.CMD_SEND_HOME - 1] = (['send_home'], available_guests)
        super().update_commands()

    def print_info(self):
        super().print_info()
        print_title('Food:')
        print_list(food.plated())
        print_title('Guests:')
        names_with_groups = []
        for guest_name in guests.available_guests():
            guest = guests.get(guest_name)
            if guest.groups:
                names_with_groups.append(
                    '{} ({})'.format(guest.name, guest.group_name)
                )
            else:
                names_with_groups.append(guest.name)
        print_list(names_with_groups)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_TAKE_ORDER:
            guest = self.original_name(cmd_input[1])
            return TakeOrderMode(guest)
        if cmd == self.CMD_CHAT:
            guest = self.original_name(cmd_input[1])
            group = guests.get_group_name(guest)
            chat = social.next_chat(group)
            if chat:
                return ChatMode(guest, chat)
        if cmd == self.CMD_SERVE:
            food = self.original_name(cmd_input[1])
            guest = self.original_name(cmd_input[3])
            action = actions.Serve(food, guest)
            action.perform()
            self.update_commands()
            return self
        if cmd == self.CMD_SEND_HOME:
            guest = self.original_name(cmd_input[1])
            action = actions.SendHome(guest)
            action.perform()
            self.update_commands()
            return self
        if cmd == self.CMD_COOKING:
            return CookingMode()
        if cmd == self.CMD_DONE:
            return DinerMode()


class CookingMode(Mode):
    CMD_COOK = 1
    CMD_TRASH = 2
    CMD_RECIPES = 3
    CMD_COOKING_BOT = 4
    CMD_ABORT = 5
    CMD_SERVICE = 6
    CMD_DONE = 7
    commands = [
        (['cook'], [], ),
        (['trash'], ),
        (['recipes'], ),
        (['bot'], ),
        (['abort'], ),
        (['service'], ),
        (['done'], ),
    ]
    prompt = 'cooking >>'
    action = None
    orders = None
    available_ingredients = None
    available_devices = None
    prepared_components = None

    def __init__(self):
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
        super().__init__()

    def update_commands(self):
        ingredients = []
        for ingredient, available in self.available_ingredients.items():
            if available: ingredients.append(self.name_for_command(ingredient))
        preparations = [d.command for d in self.available_devices.values()]
        self.commands[0] = (preparations, ingredients)
        super().update_commands()

    def print_info(self):
        super().print_info()
        print_title('Orders:')
        print_list(['{}: {}'.format(g, o) for g, o in self.orders.items()])
        print_title('Available Ingredients:')
        print_list(['{} {}s'.format(a, i) for i, a in self.available_ingredients.items()])
        print_title('Kitchen:')
        print_list(['{} for {}'.format(d.name, d.preparation) for d in self.available_devices.values()])
        print_title('Prepared:')
        print_list(self.prepared_components)
        print_title('Plated:')
        print_list(list(food.plated()))

    def print_help(self):
        print('Help:')
        print(self.commands)

    def _get_device(self, preparation_command):
        for device in self.available_devices.values():
            if device.command == preparation_command:
                return device
        return None

    def exec(self, cmd, cmd_input):
        global actions_saved
        if cmd == self.CMD_COOK:
            preparation_command = cmd_input[0]
            device = self._get_device(preparation_command)
            ingredient = self.original_name(cmd_input[1])
            self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient) - 1})
            self.action.add_ingredients([(device.result, ingredient)])
            self.prepared_components.append('{} {}'.format(device.result, ingredient))
            self.update_commands()
            if len(self.prepared_components) == 3:
                self.action.perform()
                print_message('Plated {}'.format(self.action.food.name))
                self.action = actions.Cook()
                self.prepared_components = []
            return self
        if cmd == self.CMD_TRASH:
            self.action.abort()
            self.prepared_components = []
            return self
        if cmd == self.CMD_COOKING_BOT:
            actions_saved.append(self.action)
            return CookingBotMenuMode()
        if cmd == self.CMD_RECIPES:
            actions_saved.append(self.action)
            return RecipeMode()
        if cmd == self.CMD_ABORT:
            self.action = actions.Cook()
            self.prepared_components = []
            return self
        if cmd == self.CMD_SERVICE:
            actions_saved.append(self.action)
            return ServiceMode()
        if cmd == self.CMD_DONE:
            actions_saved.append(self.action)
            return DinerMode()


class RecipeMode(ChoiceMode):
    prompt = 'recipe #'
    choices = None
    title = 'Recipes'

    def __init__(self):
        super().__init__()
        self.choices = food.get_recipes()

    def _print_recipe(self, recipe):
        print_title(recipe.name)
        ingredient_list = [' '.join(properties) for properties in recipe.ingredient_properties]
        print_list(ingredient_list)

    def exec_choice(self, choice):
        recipe = food.get_recipe(self.choices[choice - 1])
        self._print_recipe(recipe)
        return self

    def back(self):
        return CookingMode()


class CookingBotMenuMode(ChoiceMode):
    prompt = 'cooking bot #'
    choices = ['Cook saved dish', 'Save plated dish', 'View saved dishes']
    title = 'Input'

    def __init__(self):
        super().__init__()
        print_dialog('KiBo3000', 'bleep ... blup ...')

    def exec_choice(self, choice):
        if choice == 1:
            return CookingBotCookMode()
        elif choice == 2:
            return CookingBotSaveMode()
        elif choice == 3:
            return CookingBotListMode()
        return self

    def back(self):
        return CookingMode()


class CookingBotCookMode(ChoiceMode):
    prompt = 'cooking bot #'
    choices = None
    title = 'Select dish'

    def __init__(self):
        print_dialog('KiBo3000', 'bleep ... blup ...')
        self.choices = food.get_dishes()
        super().__init__()

    def exec_choice(self, choice):
        dish = self.choices[choice - 1]
        dish_recipe = food.get_dish(dish)
        if dish_recipe.can_be_cooked():
            ingredients = dish_recipe.get_prepared_ingredients()
            self.action = actions.Cook(ingredients)
            self.action.perform()
            print_dialog('KiBo3000', 'Cooking {}...'.format(dish))
        else:
            print_dialog('KiBo3000', 'Not enough ingredients or equipment not available anymore.')
        return CookingBotMenuMode()

    def back(self):
        return CookingBotMenuMode()


class CookingBotSaveMode(ChoiceMode):
    prompt = 'cooking bot #'
    choices = None
    title = 'Select dish'

    def __init__(self):
        super().__init__()
        print_dialog('KiBo3000', 'bleep ... blup ...')

    def exec_choice(self, choice):
        dish = self.choices[choice - 1]
        print('')
        print_dialog('KiBo3000', 'Custom name for {}?'.format(dish))
        name = input('dish name: '.format(self.prompt))
        self.action = actions.SaveDish(dish, new_name=name)
        self.action.perform()
        print_message('saved {} ... bleep ... blup...'.format(name if name else dish))
        return CookingBotMenuMode()

    def back(self):
        return CookingBotMenuMode()


class CookingBotListMode(RecipeMode):
    prompt = 'cooking bot #'
    title = 'Dish'


    def __init__(self):
        self.recipes = food.get_dishes()
        self.choices = self.recipes
        super().__init__()

    def exec_choice(self, choice):
        recipe = food.get_dish(self.recipes[choice - 1])
        self._print_recipe(recipe)
        return self

    def back(self):
        return CookingBotMenuMode()


class TakeOrderMode(InfoMode):
    guest = None

    def __init__(self, guest):
        self.guest = guest
        super().__init__()

    def print_info(self):
        super().print_info()
        action = actions.TakeOrder(self.guest)
        action.perform()

    def back(self):
        return ServiceMode()


class ChatMode(InfoMode):
    guest = None
    chat = None

    def __init__(self, guest, chat):
        self.guest = guest
        self.chat = chat
        super().__init__()

    def print_info(self):
        super().print_info()
        action = actions.Chat(self.guest)
        action.perform()
        print_dialog(self.guest, self.chat)

    def back(self):
        return ServiceMode()


class CompendiumMode(ChoiceMode):
    prompt = 'choice #'
    choices = ['Guests', 'Ingredients']
    title = 'Compendium'

    def exec_choice(self, choice):
        if choice == 1:
            return GuestCompendiumMode()
        if choice == 2:
            return IngredientCompendiumMode()
        return self

    def back(self):
        return DinerMode()


class GuestCompendiumMode(ChoiceMode):
    prompt = 'guest #'
    choices = None
    title = 'Guest compendium'

    def __init__(self):
        self.choices = sorted(guests.get_available_groups())
        super().__init__()

    def exec_choice(self, choice):
        group = guests.get_group(self.choices[choice - 1])
        if group.description:
            print_text(group.description)
        else:
            print_text('Unknown.')
        return self

    def back(self):
        return CompendiumMode()


class IngredientCompendiumMode(ChoiceMode):
    prompt = 'ingredient #'
    choices = None
    title = 'Ingredient compendium'

    def __init__(self):
        ingredients = set(storage.available_ingredients().keys())
        ingredients.update(merchants.available_ingredients())
        self.choices = sorted(ingredients)
        super().__init__()

    def exec_choice(self, choice):
        ingredient = ingredients.get(self.choices[choice - 1])
        if ingredient.description:
            print_text(ingredient.description)
        else:
            print_text('Unknown.')
        return self

    def back(self):
        return CompendiumMode()


class AfterWorkMode(Mode):
    CMD_ACTIVITY = 1
    CMD_SHOPPING = 2
    CMD_RATINGS = 3
    CMD_MEET = 4
    CMD_SLEEP = 5
    commands = [
        ([], ),
        (['shopping'],),
        (['reviews'],),
        (['meet'],  []),
        (['sleep'],),
    ]
    prompt = 'after work >>'
    activities =  None
    activities_done = 0
    meetings = None

    def __init__(self):
        self.activities_done = 0
        self.activities = activities.available_activities()
        self.meetings = social.available_meetings()
        super().__init__()

    def update_commands(self):
        activities = [self.name_for_command(activity) for activity in self.activities]
        meetings = [self.name_for_command(meeting) for meeting in self.meetings]
        self.commands[self.CMD_ACTIVITY - 1] = (activities,)
        self.commands[self.CMD_MEET - 1] = (['meet'],  meetings)
        super().update_commands()

    def print_info(self):
        super().print_info()
        print_title('Available activities')
        print_list(self.activities)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, cmd_input):
        if cmd == self.CMD_SHOPPING:
            return ShoppingMode()
        if cmd == self.CMD_RATINGS:
            return ReviewsInfoMode()
        if cmd == self.CMD_MEET:
            guest = self.original_name(cmd_input[1])
            return MeetingMode(guest)
        if cmd == self.CMD_SLEEP:
            time.tick()
            return DinerMode()
        if cmd == self.CMD_ACTIVITY:
            self.activities_done += 1
            if self.activities_done > 1:
                print('Let\'s not do this today.')
                return self
            activity = self.original_name(cmd_input[0])
            activities.do(activity)


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
        super().print_info()
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
            return AfterWorkMode()


class ReviewsInfoMode(InfoMode):

    def back(self):
        return AfterWorkMode()

    def _rating_info(self, name, count, rating):
        if count == 0:
            return '{}:\tno reviews yet'.format(name)
        n_stars = round(rating)
        return '{}:\t[{}{}] ({:0.1f}) based on {} review(s)'.format(
            name,
            '*' * n_stars,
            '-' * (5 - n_stars),
            float(rating),
            count,
            )

    def print_info(self):
        super().print_info()
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
                guest_like += ','.join(map(lambda x: '+' + x, dislikes))
            guest_likes.append(guest_like)
        print_list(guest_likes)


class MeetingMode(ChoiceMode):
    prompt = 'reply #'
    choices = None
    title = 'Answer'
    back_enabled = False

    guest = None
    meeting = None

    def __init__(self, guest):
        self.guest = guest
        super().__init__()
        self.meeting = social.get(self.guest).get_meeting()
        self.choices = self.meeting.get_replies()

    def print_info(self):
        print_text(self.meeting.text)
        print_dialog(self.guest, self.meeting.question)
        super().print_info()

    def exec_choice(self, choice):
        reply = choice - 1
        action = actions.Meet(self.guest, reply)
        action.perform()
        return MeetingResultMode()


class MeetingResultMode(InfoMode):

    def back(self):
        return AfterWorkMode()


mode = None
actions_saved = []


def run():
    global mode
    mode = MenuMode()
    print_info = True
    print('################################  SPACE  DINER  ################################')
    while True:
        if settings.DEBUG:
            levels.debug()
        if print_info:
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


def init():
    pass
