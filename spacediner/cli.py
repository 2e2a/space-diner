from . import actions
from . import storage
from . import food


class Mode:
    commands = []
    prompt = None

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
        return self


class ActionMode(Mode):
    commands = [
        (['cooking'],),
        (['exit'],),
    ]

    def print_help(self):
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == 1:
            return CookMode()
        if cmd == 2:
            exit()


class CookMode(Mode):
    commands = [
        (['cook'], [], ),
        (['done'], ),
    ]
    prompt = 'cooking'
    ingredients = None
    action = None

    def __init__(self):
        self.update_commands()
        self.action = actions.Cook()

    def update_commands(self):
        self.ingredients = storage.available_ingredients()
        ingredients = [ingredient.replace(' ', '_') for ingredient in self.ingredients.keys()]
        self.commands[0] = (['cook'], ingredients)

    def print_help(self):
        print(self.commands)

    def exec(self, cmd, input):
        if cmd == 1:
            ingredient = input[1].replace('_', ' ')
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
        prompt = '({}) '.format(mode.prompt) if mode.prompt else ''
        cmd = input('space diner {}>> '.format(prompt))
        mode = mode.parse(cmd)

