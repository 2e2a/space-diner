from . import actions
from . import food
from . import levels
from . import storage


class Mode:
    commands = []
    prompt = None

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


class ActionMode(Mode):
    commands = [
        (['cooking'],),
        (['service'],),
        (['exit'],),
    ]

    def print_info(self):
        print('Level: {}'.format(levels.level.name))

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == 1:
            return CookingMode()
        if cmd == 2:
            exit()


class CookingMode(Mode):
    commands = [
        (['cook'], [], ),
        (['done'], ),
    ]
    prompt = 'cooking'
    action = None
    available_ingredients = None

    def __init__(self):
        self.available_ingredients = storage.available_ingredients()
        self.update_commands()
        self.action = actions.Cook()

    def update_commands(self):
        ingredients = [i.replace(' ', '_') for i in self.available_ingredients.keys()]
        self.commands[0] = (['cook'], ingredients)

    def print_info(self):
        print('Available Ingredients:')
        print(self.available_ingredients)

    def print_help(self):
        print('Help:')
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == 1:
            ingredient = input[1].replace('_', ' ')
            self.available_ingredients.update({ingredient: self.available_ingredients.get(ingredient) - 1})
            self.action.add_ingredient(ingredient)
            return self
        if cmd == 2:
            self.action.perform()
            self.action = actions.Cook()
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

