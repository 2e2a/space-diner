import subprocess
from spacediner import main


def run():
    cmd = ['ptpython', main.__file__]
    subprocess.run(cmd)