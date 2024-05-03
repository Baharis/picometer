from picometer.process import process_routine_queue


def main():
    from picometer.parser import parse_path
    routine_queue = parse_path('../example.yaml')
    process_routine_queue(routine_queue)


if __name__ == '__main__':
    main()
