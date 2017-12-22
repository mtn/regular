import readline
import sys

from src.parser import *

PROMPT = ">> "
READLINERC = "util/readline.rc"


def die(msg):
    print(msg)
    exit(1)

def run_repl():
    readline.read_init_file(READLINERC)

    while True:
        line = input(PROMPT)

        if line == "exit":
            break

        try:
            regex, word = line.split(":")
        except:
            print("Incorrect input format")
            exit(1)

        # Parser(line).parse()


def run_batch():
    pass

if __name__ == "__main__":
    print("*(be)e*(cd)c")
    print(Parser("*(be)e*(cd)c").parse())
    print("a*(c*(a))c*(bc)")
    print(Parser("a*(c*(a))c*(bc)").parse())
    # if len(sys.argv) == 1:
    #     run_repl()
    # elif len(sys.argv) == 2:
    #     run_batch()
    # else:
    #     die("Usage: python3 regular.py [FILENAME]")
