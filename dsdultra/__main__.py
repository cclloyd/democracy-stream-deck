import signal
import sys

from StreamDeck.DeviceManager import DeviceManager, ProbeError

from dsdultra.args import parse_args
from dsdultra.console import show_console
from dsdultra.dsd import DSDUltra
from dsdultra.lib import prompt_library_install, silent_install


def main():
    args = parse_args()

    show_console()

    if args.command == 'install':
        silent_install()
    if args.command == 'build':
        # We dynamically import the build function at runtime to avoid including the build tools in the exe.
        import importlib
        build_func = importlib.import_module('dsdultra.build')
        build_func.build_executable()

    try:
        decks = DeviceManager().enumerate()
    except ProbeError as e:
        print(f'Error loading StreamDeck: {e}')
        if 'No suitable LibUSB' in str(e):
            prompt_library_install()
            input('Press any key to exit...')
            sys.exit(0)
        else:
            input('Press any key to exit...')
            sys.exit(2)
    if not decks:
        print('No Stream Decks found.')
        input('Press any key to exit...')
        sys.exit(1)

    # Use the first visual deck
    deck = next((d for d in decks if d.is_visual()), None)
    if deck is None:
        print('No visual Stream Deck devices found.')
        input('Press any key to exit...')
        sys.exit(1)

    dsd = DSDUltra(deck, args)

    # Keep the script alive until the self.deck is closed (e.g., Exit pressed)
    def signal_handler(sig, frame):
        print(f'Caught interrupt ({sig}), closing deck...')
        try:
            dsd.deck.reset()
            dsd.deck.close()  # Or provide a shutdown/cleanup method
        except Exception as e:
            print(e)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    dsd.start()


main()
