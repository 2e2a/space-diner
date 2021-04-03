# Installing Space Diner

## Prerequisites

Python3 is required. You can check your python version in the terminal/command prompt with: `python --version`. 
 If you don't have python3, see [python.org](https://www.python.org/).

## Installation

Open a terminal/command prompt and run the following command:   
**`pip install space-diner`**

If this doesn't work on your system, try using the command `pip3` instead of `pip`.

_Instead of installing the package globally, you can alternatively use a virtual environment.
See the instructions on [packaging.python.org](https://packaging.python.org/tutorials/installing-packages/#optionally-create-a-virtual-environment) for details._


## Starting the game

You can now start the game from the terminal with the following command:  
**`space-diner`**

You can optionally start the game in a text-only mode (without decorative special characters):
`space-diner --text-only`


## Additional instructions for Linux users

If the command `space-diner` is not available after installation, you need to adjust your shell's PATH
(see [packaging.python.org](https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site)
for detailed instructions):
  - Run: `python -m site --user-base`. This will typically return a path like `~/.local/bin`.
  - Add the line `export PATH="$PATH:~/.local/bin"`, adjusted with the path from above, to your `~/.bashrc` file,
e.g., at the end of the file (if you are using the standard bash terminal).
  - Run: `source ~/.bashrc` or start a new terminal.
  

## Troubleshooting

If you encounter any other problems during installation or during the game, feel free to contact us (marta@2e2a.de)
or to [create an issue on GitHub](https://github.com/2e2a/space-diner/issues).

- If, under Linux, starting the game with space-diner returns the error 'command not found', check the following:
  - Run python `-m site --user-base`, which will return a path. Check if this path is included in the list that is returned by echo $PATH.
  If not, check if the line you added to `~/.bashrc` is correct.
  - In case it still doesn't work, try to alternatively start the game with `~/.local/bin/space-diner`
  (potentially adjusted based on the output of python -m site --user-base, as described above).
