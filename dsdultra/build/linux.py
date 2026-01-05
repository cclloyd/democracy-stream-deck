import sys

from nuitka.__main__ import main as nuitka_main


def build_executable():
    sys.argv = [
        'nuitka',  # dummy program name
        '--onefile',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--standalone',
        '--assume-yes-for-downloads',
        f'--output-filename=dsd',
        '--enable-plugin=tk-inter',
        '--enable-plugin=pyqt6',
        '--include-package=StreamDeck',
        '--include-package=Xlib',
        '--no-deployment-flag=self-execution',
        '--nofollow-import-to=dsdultra.build',
        '--output-dir=build',
        'dsdultra/',
    ]
    nuitka_main()
