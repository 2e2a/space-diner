from . import cli

TUTORIAL = [
    (cli.DinerMode, cli.DinerMode.CMD_TAKE_ORDER, 'Try to take an order.'),
    (cli.DinerMode, cli.DinerMode.CMD_KITCHEN, 'Now go to the kitchen please.'),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK, 'Cook!'),
]


tutorial_step = 0


def increment_tutorial(mode, cmd_num):
    global tutorial_step
    tutorial_mode, command, text = TUTORIAL[tutorial_step]
    if cmd_num == command and isinstance(mode, tutorial_mode):
        tutorial_step += 1


def get_tutorial(mode):
    global tutorial_step
    if tutorial_step < len(TUTORIAL):
        tutorial_mode, command, text = TUTORIAL[tutorial_step]
        if isinstance(mode, tutorial_mode):
            return text