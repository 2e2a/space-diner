import pickle

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
     'Once you have prepared three ingredients, they will be automatically plated as '
     'a completed dish. If someone ordered a specific dish, you can look up the recipe (type: "look up recipes"). '
     'If someone asked for an ingredient/property (e.g., "raw", "pickles"), it is sufficient to add one ingredient '
     'that matches the order. '
     'To start cooking, type "[VERB] [INGREDIENT]", e.g., "grill beef". '
     'The available verbs and ingredients are listed above.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK,
     'Now you can add a second ingredient.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_COOK,
     'Add a third ingredient.'
     ),
    (cli.KitchenMode, cli.KitchenMode.CMD_DINER,
     'Once you have completed one or more dishes, return to your guests: "go to diner".'
     ),
    (cli.DinerMode, cli.DinerMode.CMD_SERVE,
     'Now it\'s time to serve your dish: "serve [DISH] to [NAME]". After serving food to all the customers, you can '
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


def save(file):
    global tutorial_step
    pickle.dump(tutorial_step, file)


def load(file):
    global tutorial_step
    tutorial_step = pickle.load(file)