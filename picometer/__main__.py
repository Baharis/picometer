from argparse import ArgumentParser, Namespace
from picometer.instructions import Routine
from picometer.logging import add_file_handler
from picometer.process import process
import sys


def parse_args() -> Namespace:
    """Parse provided arguments if program was run directly from the CLI"""
    desc = 'Precisely define and measure across multiple crystal structures'
    author = 'Author: Daniel Tchoń, baharis @ GitHub'
    ap = ArgumentParser(prog='picometer', description=desc, epilog=author)
    ap.add_argument('filename', help='Path to yaml file with routine '
                                     'settings and instructions')
    if len(sys.argv) == 1:
        ap.print_help(sys.stderr)
        sys.exit(1)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    if filename := args.filename:
        add_file_handler('picometer.log')
        routine = Routine.from_yaml(filename)
        process(routine)
    return 0


if __name__ == '__main__':
    sys.exit(main())
