from argparse import ArgumentParser, Namespace
from picometer.parser import parse_path
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


def main() -> None:
    args = parse_args()
    if filename := args.filename:
        routine = parse_path(filename)
        process(routine)


if __name__ == '__main__':
    main()
