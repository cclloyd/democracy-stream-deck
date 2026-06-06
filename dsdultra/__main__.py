import signal
import sys
import traceback
from datetime import datetime
from pathlib import Path

import psutil

from dsdultra.version import VERSION
from dsdultra.args import parse_args
from dsdultra.config import DSDConfig
from dsdultra.console import show_console
from dsdultra.installer import InstallerWizard
from dsdultra.logging import redirect_output_to_file
from dsdultra.util import is_frozen


def check_elgato_running(path: Path):
    process_name = path.stem.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and process_name in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def main():
    try:
        args = parse_args()
        wizard = InstallerWizard()
        config = DSDConfig(None)

        if args.version or args.command == 'version':
            print(VERSION)
            sys.exit(0)
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

        if check_elgato_running(config.elgato_path):
            from PyQt6.QtWidgets import QApplication, QMessageBox
            message = 'Elgato StreamDeck is currently running. Please close it before launching this app.'
            print(message)
            if is_frozen():
                app = QApplication(sys.argv)
                QMessageBox.warning(None, 'DSDUltra', message)
                app.quit()
            sys.exit(1)

        redirect_output_to_file(config.log_path)
        if config.show_console:
            show_console(log_path=config.log_path)

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
            dsd = DSDUltra(deck, args, started=datetime.now(), config=config)

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
    except Exception as e:
        try:
            config = DSDConfig(None)
            redirect_output_to_file(config.log_path)
        except:
            pass
        print(e)
        traceback.print_exc()
        raise e

main()
