import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='dsdultra: Run a command with optional configuration and debug mode.'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='run',
        choices=('run', 'install', 'build', 'shortcut'),
        help='The command to execute (when running as: python -m dsdultra <command>)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode.'
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Opens logs on launch.'
    )
    parser.add_argument(
        '-c', '--config',
        dest='config_path',
        metavar='CONFIG_PATH',
        help='Path to the configuration folder.'
    )
    parser.add_argument(
        '--trace',
        action='store_true',
        help='Enable trace logging.'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print version and exit.'
    )
    return parser.parse_args()
