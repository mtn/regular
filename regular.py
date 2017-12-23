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

        print(RE(Parser(regex).parse()).match(word))


def run_batch():
    with open(sys.argv[1], "r") as f:
        for line in f:
            try:
                regex, word = line.strip().split(":")
            except:
                print("Incorrect input format")
                exit(1)

            print(RE(Parser(regex).parse()).match(word))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_repl()
    elif len(sys.argv) == 2:
        run_batch()
    else:
        die("Usage: python3 regular.py [FILENAME]")
