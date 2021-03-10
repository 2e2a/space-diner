from . import cli

TUTORIAL = [
    (cli.DinerMode, cli.DinerMode.CMD_TAKE_ORDER,
     'This short tutorial is going to guide through the first couple of steps. First, try to take an order. '
     'The command is "take order from [NAME]". Use auto-complete: type "take" and press TAB, then type the first '
     'letters of a customer\'s name and press TAB again.'
     ),
    (cli.DinerMode, cli.DinerMode.CMD_KITCHEN,
     'After taking orders, you can go to the kitchen to prepare the food: "go to kitchen".'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK,
     'Every dish consists of three ingredients. Once you have prepared them, they will be automatically plated as '
     'a completed dish. If you like, you can look at available recipes (type: "recipes"). To start cooking, '
     'type "[VERB] [INGREDIENT]". The available verbs (e.g., "grill", "plate"...) and ingredients are listed above.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK,
     'Now you can add a second ingredient.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK,
     'Add a third ingredient.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_DINER,
     'Once you have completed a dish, return to your guests: "go to diner".'
     ),
    (cli.DinerMode, cli.DinerMode.CMD_SERVE,
     'Now it\'s time to serve your dish: "serve [DISH] to [NAME]". After serving all the customers, you can '
     'call it a day ("close up"). New guests will come tomorrow. (This is the end of the tutorial. You can '
     'type "help" at any point during the game for hints and a list of available commands.)'
     ),
]


tutorial_step = 0


def increment_tutorial(mode, cmd_num):
    global tutorial_step
    if tutorial_step < len(TUTORIAL):
        tutorial_mode, command, text = TUTORIAL[tutorial_step]
        if cmd_num == command and isinstance(mode, tutorial_mode):
            tutorial_step += 1


def get_mode_tutorial(mode):
    global tutorial_step
    if tutorial_step < len(TUTORIAL):
        tutorial_mode, command, text = TUTORIAL[tutorial_step]
        if isinstance(mode, tutorial_mode):
            return text
