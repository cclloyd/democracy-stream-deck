import signal
import sys

from StreamDeck.DeviceManager import DeviceManager, ProbeError

from dsdultra.args import parse_args
from dsdultra.dsd import DSDUltra
from dsdultra.lib import prompt_library_install, silent_install


def main():
    args = parse_args()

    if args.command == 'install':
        silent_install()

    try:
        decks = DeviceManager().enumerate()
    except ProbeError as e:
        print(f'Error loading StreamDeck: {e}')
        if 'No suitable LibUSB' in str(e):
            prompt_library_install()
            sys.exit(0)
        else:
            sys.exit(2)
    if not decks:
        print('No Stream Decks found.')
        return

    # Use the first visual deck
    deck = next((d for d in decks if d.is_visual()), None)
    if deck is None:
        print('No visual Stream Deck devices found.')
        return

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
