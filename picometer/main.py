from picometer.process import process


def main():
    from picometer.parser import parse_path
    routine = parse_path('../example.yaml')
    process(routine)


if __name__ == '__main__':
    main()
