# TODO: autocompletion for moss/moss-milk is broken
# TODO: rewards/trophies for achievements, e.g., served 10/50/100 dishes, received 10/50/100 positive reviews...
# TODO: check if rewards by normal guests are possible
# TODO: bug: sometimes prepared ingredients appear in the kitchen although they were already served
# TODO: check non-ascii characters in name factories
# TODO: sometimes broken: NameFactory create (some names cause a problem?)
# TODO: make activities available on specific days
# TODO: special weekend day (last day of the week) with two activities instead of work and one activity
# TODO: think about menu: are all/some initial menu items fixed?


from . import run

if __name__ == "__main__":
    run.run(dev=True)
