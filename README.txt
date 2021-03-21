Installing Space Diner
----------------------

Prerequisites:
--------------

- python3 is required. You can check your python version with the following command: "python --version".
  If you don't have python3, see python.org.
- Download the package file "space-diner-VERSION.tar.gz".

Installation:
-------------

1. Open a terminal/command prompt and go to the directory with the downloaded package.
2. Run the following command: "pip3 install space-diner-VERSION.tar.gz"
   (replace VERSION with the actual version number from the file name)
3. Check if any of the following conditions apply – otherwise, you are done!
   - If your python version < 3.7, additionally run: "pip3 install importlib_resources".
   - Under Windows, additionally run: "pip3 install pyreadline."
   - Under Linux, try to run the command space-diner. If it is not available, you need to adjust your shell's PATH
     (for details, see: https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site):
        - Run: "python -m site --user-base". This will typically return a path like "~/.local/bin".
        - Add the line "export PATH="$PATH:~/.local/bin"", adjusted with the path from above, to your "~/.bashrc" file,
          e.g., at the end of the file (if you are using the standard bash terminal).
        - Run: "source ~/.bashrc" or start a new terminal.

(Instead of installing the package globally, you can alternatively use a virtual environment.
For detailed instructions, see:
https://packaging.python.org/tutorials/installing-packages/#optionally-create-a-virtual-environment )

Starting the game:
------------------

You can now start the game from the terminal with the following command: "space-diner"