import signal
import sys
import traceback


from dsdultra.args import parse_args
from dsdultra.console import show_console
from dsdultra.installer import InstallerWizard


def main():
    args = parse_args()
    wizard = InstallerWizard()

    if args.command == 'install':
        wizard.silent_install()
        sys.exit(0)
    if args.command == 'shortcut':
        wizard.create_shortcut()
        sys.exit(0)
    if args.command == 'build':
        # We dynamically import the build function at runtime to avoid including the build tools in the exe.
        import importlib
        build_func = importlib.import_module('dsdultra.build')
        build_func.build_executable()
        sys.exit(0)

    if args.console:
        show_console()

    from StreamDeck.DeviceManager import DeviceManager, ProbeError
    try:
        decks = DeviceManager().enumerate()
    except ProbeError as e:
        print(f'Error loading StreamDeck: {e}')
        if 'No suitable LibUSB' in str(e):
            wizard.prompt_library_install()
            input('Press any key to exit...')
            sys.exit(0)
        else:
            input('\nPress any key to exit...')
            sys.exit(2)
    if not decks:
        print('No Stream Decks found.')
        input('\nPress any key to exit...')
        sys.exit(1)

    # Use the first visual deck
    deck = next((d for d in decks if d.is_visual()), None)
    if deck is None:
        print('No visual Stream Deck devices found.')
        input('\nPress any key to exit...')
        sys.exit(1)

    from dsdultra.dsd import DSDUltra
    try:
        dsd = DSDUltra(deck, args)

        # Keep the script alive until the self.deck is closed (e.g., Exit pressed)
        def signal_handler(sig, frame):
            print(f'Caught interrupt ({sig}), closing deck...')
            dsd.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        dsd.start()
    except Exception as e:
        traceback.print_exc()
        print(f'Error starting DSDUltra: {e}')
        input('\nPress any key to exit...')
        sys.exit(1)


main()
